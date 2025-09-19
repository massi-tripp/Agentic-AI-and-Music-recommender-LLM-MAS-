from typing import Dict, Any
# Hook da rimpiazzare con chiamata all'SDK LLM (temperature=0, output JSON)
async def llm_decide_action(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: snapshot strutturato.
    Output JSON: {"action": "SHARE"|"WAIT","targets": ["u42",...],"song_id": int,"mode":"COOP"|"COMP","explain": "..."}
    """
    # Placeholder: policy euristica, poi sostituisci con LLM
    if not state["neighbors"]: return {"action":"WAIT"}
    best = max(state["candidates"], key=lambda c: c["base_score"])
    targets = [n["id"] for n in sorted(state["neighbors"], key=lambda x: x["trust"], reverse=True)[:2]]
    return {"action":"SHARE","targets":targets,"song_id":best["song_id"],"mode":"COOP","explain":"heuristic"}
