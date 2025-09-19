import pandas as pd
import numpy as np
from typing import List
from ..data_types import Song

# Simple scalers for raw cols → [0,1]
def norm_tempo(x: pd.Series) -> pd.Series:
    # clamp 50..200 BPM then min-max
    x = x.clip(lower=50, upper=200)
    return (x - 50.0) / (200.0 - 50.0)

def norm_loudness(x: pd.Series) -> pd.Series:
    # loudness is typically in [-60, 0] dB
    x = x.clip(lower=-60.0, upper=0.0)
    return (x + 60.0) / 60.0

FEATURES_CANONICAL = [
    "danceability","energy","valence","acousticness",
    "instrumentalness","speechiness","liveness",
    "tempo_norm","loudness_norm"
]

def load_spotify_csv(path: str, n_songs: int,
                     by_popularity_quantile: float = 0.0,
                     exclude_explicit: bool = False,
                     features_used: List[str] = FEATURES_CANONICAL) -> List[Song]:
    df = pd.read_csv(path)
    # Dedup & minimal cleaning
    df = df.drop_duplicates(subset=["track_id"]).dropna(subset=["track_id","track_name"])
    if exclude_explicit and "explicit" in df.columns:
        df = df[df["explicit"] == False]

    # Add normalized columns
    if "tempo" in df.columns:
        df["tempo_norm"] = norm_tempo(df["tempo"].astype(float))
    if "loudness" in df.columns:
        df["loudness_norm"] = norm_loudness(df["loudness"].astype(float))

    # Keep only rows with all required features
    df = df.dropna(subset=[c.replace("_norm","") if c.endswith("_norm") else c
                           for c in features_used if c not in ["tempo_norm","loudness_norm"]])
    # Popularity-based sampling (optional)
    if by_popularity_quantile and "popularity" in df.columns:
        thr = df["popularity"].quantile(by_popularity_quantile)
        df = df[df["popularity"] >= thr]

    # Final sample for speed
    if n_songs and len(df) > n_songs:
        df = df.sample(n=n_songs, random_state=42)

    # Build Song objects with z-normalized feature vectors (per column)
    feat_df = df.copy()
    # Ensure all features exist:
    for col in ["tempo_norm","loudness_norm"]:
        if col in features_used and col not in feat_df.columns:
            feat_df[col] = 0.0
    feats = feat_df[features_used].astype(float)
    # Column-wise standardization improves cosine behavior
    feats = (feats - feats.mean(axis=0)) / (feats.std(axis=0) + 1e-9)
    feats = feats.astype("float32").to_numpy()

    songs: List[Song] = []
    for i, (_, row) in enumerate(df.iterrows()):
        vec = feats[i]
        songs.append(Song(
            id=i,
            track_id=str(row["track_id"]),
            features=vec,
            meta={
                "track_name": row.get("track_name",""),
                "artists": row.get("artists",""),
                "album_name": row.get("album_name",""),
                "genre": row.get("track_genre","unknown"),
                "popularity": int(row.get("popularity",0))
            }
        ))
    return songs
