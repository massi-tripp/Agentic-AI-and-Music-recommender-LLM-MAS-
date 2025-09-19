import numpy as np, uuid, random
from typing import Dict, Any
from .bus import bus
from .protocol import ACLMessage, Performative
from .logger import RunLogger

def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

class Environment:
    def __init__(self, conf, songs, graph, profiles, runlog: RunLogger):
        self.conf = conf
        self.songs = songs
        self.G = graph                 # nodi int
        self.profiles = profiles       # lista di np.ndarray

        # --- Stato agente (sempre chiavi stringa) ---
        self.trust = {(str(u), str(v)): 0.5 for u in self.G for v in self.G.neighbors(u)}
        self.attention = {str(u): conf.attention_budget for u in self.G}
        self.history = {str(u): [] for u in self.G}

        # --- Logging & step ---
        self.runlog = runlog
        self.step = 0

        # --- Anti-spam / targeting controls ---
        # cooldown: evita di proporre lo stesso (receiver, song) per N step
        self.last_proposal: dict[tuple[str, int], int] = {}
        self.cooldown: int = 1
        # gate_threshold: soglia minima sulla probabilità stimata per inviare un PROPOSE
        self.gate_threshold: float = 0.30

    # ===== Helpers runtime =====
    def dt(self) -> float:
        return self.conf.dt

    def poisson_fire(self, rng: random.Random) -> bool:
        # Bernoulli con p ≈ lambda*dt
        lam = self.conf.poisson_rate["lambda_base"]
        return rng.random() < lam * self.conf.dt

    # ===== Candidate selection =====
    def candidates_for(self, u: str, topk: int):
        prof = self.profiles[int(u)]
        scores = [(s.id, cosine_sim(prof, s.features)) for s in self.songs]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:topk]

    def snapshot(self, u: str) -> Dict[str, Any]:
        uid = int(u)  # grafo vuole int
        nbrs = list(self.G.neighbors(uid))
        return {
            "agent_id": u,
            "neighbors": [
                {"id": str(v), "trust": self.trust[(u, str(v))], "load": self.attention[str(v)]}
                for v in nbrs
            ],
            "candidates": [
                {"song_id": sid, "base_score": sc}
                for sid, sc in self.candidates_for(u, self.conf.topk_candidates)
            ],
            "recent_listens": self.history[u][-10:],
            "step": self.step,
        }

    # ===== Proposal gating / cooldown =====
    def can_propose(self, receiver: str, song_id: int) -> bool:
        last = self.last_proposal.get((receiver, song_id), -10**9)
        return (self.step - last) >= self.cooldown

    def mark_propose(self, receiver: str, song_id: int) -> None:
        self.last_proposal[(receiver, song_id)] = self.step

    # ===== Adoption model =====
    def adoption_prob(self, receiver: str, song_id: int, sender: str) -> float:
        prof = self.profiles[int(receiver)]
        song = self.songs[song_id]
        sim = cosine_sim(prof, song.features)  # ~[-1,1]
        t = self.trust[(receiver, sender)]
        base = 0.35  # valore “moderato”; 
        return max(0.0, min(1.0, base + 0.6 * sim + 0.2 * t))

    def apply_adoption(self, receiver: str, song_id: int, sender: str, conv_id: str):
        self.history[receiver].append(song_id)
        self.trust[(receiver, sender)] = min(1.0, self.trust[(receiver, sender)] + 0.05)
        self.runlog.log_msg({
            "type": "ADOPT", "receiver": receiver, "sender": sender,
            "song_id": song_id, "step": self.step, "conv_id": conv_id
        })
