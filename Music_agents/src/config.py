# src/config.py
from pydantic import BaseModel
from typing import Dict, List, Optional
import yaml

class LLMConf(BaseModel):
    enabled: bool = False
    backend: str = "ollama"     # "ollama" | "litellm"
    model: str = "phi3:mini"          # ollama: "phi"/"phi3"; litellm: "phi-2"
    temperature: float = 0.0
    max_output_tokens: int = 128
    endpoint: Optional[str] = None  # usato da ollama

class Config(BaseModel):
    # run
    random_seed: int
    max_steps: int
    dt: float
    log_every: int

    # agents/graph
    n_agents: int
    attention_budget: int
    graph: Dict
    poisson_rate: Dict

    # songs/dataset
    song_source: str
    song_csv_path: str
    features_used: List[str]
    sample: Dict
    filters: Dict

    # flags
    topk_candidates: int
    sequential: bool = False

    # llm
    llm: LLMConf

def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config(**data)
