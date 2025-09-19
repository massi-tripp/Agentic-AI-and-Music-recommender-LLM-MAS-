import asyncio, uuid, random

# fallback JSON compatibile
try:
    import orjson as _jsonlib
    def _dumps(x): return _jsonlib.dumps(x)
except Exception:
    import json as _jsonlib
    def _dumps(x): return _jsonlib.dumps(x).encode()

from .bus import bus
from .protocol import ACLMessage, Performative
from .policy_phi import llm_decide_action
from .security import sign


class Agent:
    def __init__(self, agent_id: str, key: bytes, env, rng: random.Random):
        self.id = agent_id
        self.key = key
        self.env = env
        self.inbox = bus.mailbox(agent_id)
        self.rng = rng
        self.internal_decision_count = 0

    async def proactive(self):
        if not self.env.poisson_fire(self.rng):
            return

        state = self.env.snapshot(self.id)

        try:
            decision = await llm_decide_action(state, self.env.conf)  # LLM/heuristic
        except Exception as e:
            self.env.runlog.log_msg({
                "type": "ERROR", "where": "policy",
                "agent": self.id, "err": repr(e), "step": self.env.step
            })
            return

        # --- Post-filter senza 'load' (trust + gate on p(adopt))
        gate = getattr(self.env, "gate_threshold", 0.30)
        tuned_targets = []
        for tgt in decision.get("targets", []):
            trust_ok = True
            if hasattr(self.env, "neighbor_info"):
                info = self.env.neighbor_info(self.id, tgt)
                if info.get("trust", 0.0) < 0.4:
                    trust_ok = False
            else:
                snap_tmp = self.env.snapshot(self.id)
                trust_map = {n["id"]: n.get("trust", 0.5) for n in snap_tmp.get("neighbors", [])}
                if trust_map.get(tgt, 0.0) < 0.4:
                    trust_ok = False
            if not trust_ok:
                continue

            if hasattr(self.env, "can_propose") and not self.env.can_propose(
                tgt, int(decision.get("song_id", -1))
            ):
                continue

            p = self.env.adoption_prob(
                receiver=tgt,
                song_id=int(decision.get("song_id", -1)),
                sender=self.id,
            )
            if p >= gate:
                tuned_targets.append(tgt)
        if not tuned_targets:
            snap = self.env.snapshot(self.id)
            neigh = snap.get("neighbors", [])
            neigh = [n for n in neigh if n.get("trust", 0.0) >= 0.4]
            neigh.sort(key=lambda n: n.get("trust", 0.0), reverse=True)
            tuned_targets = [neigh[0]["id"]] if neigh else []

        decision["targets"] = tuned_targets[:2]
        if not decision.get("targets"):
            decision["action"] = "WAIT"

        if decision.get("action") == "SHARE" and decision.get("targets"):
            snap = self.env.snapshot(self.id)
            candidates = snap.get("candidates", [])
            if candidates:
                best_song = None
                best_score = -1.0
                for c in candidates:
                    s = int(c["song_id"])
                    ps = [
                        self.env.adoption_prob(receiver=t, song_id=s, sender=self.id)
                        for t in decision["targets"]
                    ]
                    score = sum(ps) / len(ps) if ps else -1.0
                    if score > best_score:
                        best_score, best_song = score, s
                if best_song is not None:
                    decision["song_id"] = best_song

        self.env.runlog.log_msg({
            "type": "DECISION",
            "agent": self.id,
            "source": decision.get("source", "unknown"),
            "song_id": int(decision.get("song_id", -1)) if "song_id" in decision else -1,
            "targets": decision.get("targets", []),
            "explain": decision.get("explain", ""),
            "step": self.env.step
        })

        if decision.get("action") != "SHARE":
            return

        song_id = int(decision["song_id"])
        for tgt in decision.get("targets", []):
            # cooldown guard
            if hasattr(self.env, "can_propose") and not self.env.can_propose(tgt, song_id):
                continue

            # probability gate 
            p = self.env.adoption_prob(receiver=tgt, song_id=song_id, sender=self.id)
            gate = getattr(self.env, "gate_threshold", 0.3)
            if p < gate:
                continue

            payload = {"song_id": song_id, "mode": decision.get("mode", "COOP")}
            msg = ACLMessage(
                sender=self.id, receiver=tgt,
                performative=Performative.PROPOSE,
                conv_id=str(uuid.uuid4()),
                content=payload, nonce=str(self.rng.random()),
                sig=sign(self.key, _dumps(payload))
            )

            # log propose (with source/explain)
            self.env.runlog.log_msg({
                "type": "PROPOSE", "sender": self.id, "receiver": tgt,
                "song_id": song_id, "step": self.env.step,
                "source": decision.get("source", "unknown"),
                "explain": decision.get("explain", "")
            })

            await bus.send(msg)

            if hasattr(self.env, "mark_propose"):
                self.env.mark_propose(tgt, song_id)

    async def handle(self, msg: ACLMessage):
        if msg.performative == Performative.PROPOSE:
            prob = self.env.adoption_prob(self.id, msg.content["song_id"], msg.sender)
            if self.rng.random() < prob:
                self.env.apply_adoption(
                    self.id, msg.content["song_id"], msg.sender, msg.conv_id
                )
            else:
                pass  

    async def run(self):
        while True:
            await self.proactive()
            # consume up to attention_budget
            for _ in range(self.env.conf.attention_budget):
                try:
                    msg = self.inbox.get_nowait()
                except asyncio.QueueEmpty:
                    break
                await self.handle(msg)
            await asyncio.sleep(self.env.dt())
