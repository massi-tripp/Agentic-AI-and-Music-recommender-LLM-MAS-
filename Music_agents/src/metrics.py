import pandas as pd, numpy as np, networkx as nx

def load_messages(path: str) -> pd.DataFrame:
    return pd.read_json(path, lines=True)

def cascades(df: pd.DataFrame):
    # costruisci grafo diffusion per song_id e misura componenti
    ...

def gini(popularity: pd.Series) -> float:
    x = popularity.values.astype(float); x.sort()
    n = len(x); return (2*np.arange(1, n+1) - n - 1 @ x) / (n * x.sum())
