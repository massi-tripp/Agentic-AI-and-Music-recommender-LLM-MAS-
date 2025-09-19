import numpy as np
import pandas as pd
from typing import List, Dict
from .data_types import Song

def genre_prototypes(songs: List[Song]) -> Dict[str, np.ndarray]:
    rows = []
    for s in songs:
        rows.append({"genre": s.meta.get("genre","unknown"), "feat": s.features})
    df = pd.DataFrame(rows)
    # average feature per genre
    protos = {}
    for g, grp in df.groupby("genre"):
        M = np.stack(grp["feat"].to_list(), axis=0)
        protos[g] = M.mean(axis=0)
    return protos

def make_agent_profiles(n_agents: int, songs: List[Song], seed: int = 42) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    protos = genre_prototypes(songs)
    genres = list(protos.keys())
    k = len(genres)
    # Dirichlet mixture over genres + small gaussian noise
    profiles = []
    for _ in range(n_agents):
        w = rng.dirichlet(alpha=np.ones(min(4,k)))  # prefer 3–4 genres
        chosen = rng.choice(genres, size=len(w), replace=False)
        vec = sum(w[i]*protos[chosen[i]] for i in range(len(w)))
        vec = vec + rng.normal(0, 0.15, size=vec.shape)  # personal taste
        # normalize for cosine
        norm = np.linalg.norm(vec) + 1e-9
        profiles.append((vec / norm).astype("float32"))
    return profiles
