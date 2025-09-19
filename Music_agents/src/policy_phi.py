# src/policy_phi.py
import json, asyncio, os
from typing import Dict, Any

# Limita il parallelismo verso l'LLM 
_SEM = asyncio.Semaphore(2)

def _system_prompt() -> str:
    # Prompt severo: un solo oggetto JSON, campi esatti, niente testo extra
    return (
        "You are a policy for a music recommendation agent.\n"
        "Output only a SINGLE JSON object with EXACTLY these fields:\n"
        '{"action":"SHARE|WAIT","targets":[strings],"song_id":int,"mode":"COOP|COMP","explain":"short"}\n'
        "No prose. No code fences. No extra keys. No trailing text.\n"
        "Rules: prefer at most 2 targets with highest trust and low load; "
        "pick only from provided candidates; never invent song_id; if uncertain, action=WAIT."
    )

def _user_payload(state: Dict[str, Any]) -> str:
    # Stato compatto e strutturato
    payload = {
        "neighbors": state.get("neighbors", []),
        "candidates": state.get("candidates", []),
        "recent_listens": state.get("recent_listens", []),
    }
    return json.dumps({"state": payload}, ensure_ascii=False)

# ------------------ OLLAMA (locale) ------------------
def _ollama_chat(endpoint: str, model: str, system: str, user: str, temperature: float) -> Dict:
    import requests
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"temperature": temperature},
        "stream": False,
        "format": "json",  # forza l'output a JSON puro
    }
    r = requests.post(f"{endpoint}/api/chat", json=data, timeout=120)
    r.raise_for_status()
    msg = r.json()["message"]["content"]  # stringa JSON
    # parsing rigido: se fallisce, lascio propagare l'eccezione
    return json.loads(msg)

# ------------------ LiteLLM (provider-agnostic) ------------------
async def _litellm_json(model: str, system: str, user: str, temperature: float) -> Dict:
    # requires: pip install litellm
    from litellm import acompletion
    resp = await acompletion(
        model=model,
        messages=[{"role":"system","content": system},
                  {"role":"user","content": user}],
        response_format={"type":"json_object"},
        temperature=temperature,
        max_tokens=256,
    )
    content = resp.choices[0].message.content
    return json.loads(content)

# ------------------ PUBLIC ENTRY ------------------
async def llm_decide_action(state: Dict[str, Any], conf) -> Dict[str, Any]:
    """
    Structured policy: if LLM disabled => heuristic.
    Uses conf.llm.* (dot access). If the LLM fails, exceptions propagate
    and the Agent logs an ERROR (better observability).
    """
    # ---- SAFE READ OF CONFIG ----
    llm_conf = getattr(conf, "llm", None)
    llm_enabled = bool(getattr(llm_conf, "enabled", False)) if llm_conf else False
    temperature = float(getattr(llm_conf, "temperature", 0.0)) if llm_conf else 0.0
    backend = getattr(llm_conf, "backend", "ollama") if llm_conf else "ollama"
    model = getattr(llm_conf, "model", "phi3:mini") if llm_conf else "phi3:mini"
    endpoint = getattr(llm_conf, "endpoint", "http://127.0.0.1:11434") if llm_conf else "http://127.0.0.1:11434"

    # ---- HEURISTIC FALLBACK (no LLM) ----
    def _heuristic():
        cands = state.get("candidates") or []
        neighbors = state.get("neighbors") or []
        if not cands or not neighbors:
            return {"action": "WAIT"}
        best = max(cands, key=lambda c: c.get("base_score", -1e9))
        targets = [
            n["id"] for n in sorted(
                neighbors, key=lambda x: (x.get("trust", 0.0), -x.get("load", 0.0)),
                reverse=True
            )[:2]
        ]
        return {
            "action": "SHARE",
            "targets": targets,
            "song_id": int(best["song_id"]),
            "mode": "COOP",
            "explain": "heuristic",
            "source": "heuristic",
        }

    if not llm_enabled:
        return _heuristic()

    # ---- LLM BRANCH ----
    system = _system_prompt()
    user = _user_payload(state)

    # stampa quando chiamiamo il modello
    '''print(
        f"[LLM] backend={backend} model={model} called step={state.get('step','?')}",
        flush=True
    )'''

    async with _SEM:
        if backend == "ollama":
            obj = await asyncio.to_thread(
                lambda: _ollama_chat(endpoint, model, system, user, temperature)
            )
        else:  # "litellm"
            obj = await _litellm_json(model, system, user, temperature)

    # validazione minima
    if not isinstance(obj, dict) or "action" not in obj:
        raise ValueError(f"LLM returned non-compliant JSON: {obj}")

    obj.setdefault("targets", [])
    obj.setdefault("mode", "COOP")
    obj.setdefault("explain", "llm")   # se il modello non mette explain
    obj["source"] = "llm"
    return obj
