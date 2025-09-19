from dataclasses import dataclass
from typing import Dict, Any
import numpy as np

@dataclass
class Song:
    id: int                 # 0..N-1 interno simulazione
    track_id: str           # id Spotify dal CSV
    features: np.ndarray    # vettore normalizzato (float32)
    meta: Dict[str, Any]    # artists, track_name, genre, popularity
