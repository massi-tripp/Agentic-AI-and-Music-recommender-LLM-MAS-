# src/simulate.py
import asyncio, random
from pathlib import Path

import numpy as np
import networkx as nx

from .config import load_config
from .data_loaders.spotify import load_spotify_csv
from .profile_gen import make_agent_profiles
from .env import Environment
from .agent import Agent
from .logger import RunLogger


async def run_once(cfg_path: str | None = None, run_dir: str | None = None):
    from datetime import datetime
    root = Path(__file__).resolve().parents[1]
    cfg_path = cfg_path or str(root / "configs" / "base.yaml")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = run_dir or str(root / "runs" / f"demo-{stamp}")

    conf = load_config(cfg_path)
    random.seed(conf.random_seed)
    np.random.seed(conf.random_seed)

    # --- DATA
    songs = load_spotify_csv(
        path=conf.song_csv_path,
        n_songs=conf.sample["n_songs"],
        by_popularity_quantile=conf.sample["by_popularity_quantile"],
        exclude_explicit=conf.filters["exclude_explicit"],
        features_used=conf.features_used,
    )

    # --- GRAPH
    G = nx.watts_strogatz_graph(
        n=conf.n_agents, k=conf.graph["k"], p=conf.graph["p"], seed=conf.random_seed
    )

    # --- PROFILES
    profiles = make_agent_profiles(conf.n_agents, songs, seed=conf.random_seed)

    # --- ENV + LOGGER
    runlog = RunLogger(run_dir)
    env = Environment(conf, songs, G, profiles, runlog)

    # Log di inizio run (così il file esiste sempre)
    runlog.log_msg({
        "type": "RUN_START",
        "agents": conf.n_agents,
        "songs": len(songs),
        "steps": conf.max_steps,
        "dt": conf.dt,
        "lambda_base": conf.poisson_rate["lambda_base"],
        "llm_enabled": conf.llm.enabled,
    })

    print(f"Run dir: {run_dir} | agents={conf.n_agents} | songs={len(songs)} | steps={conf.max_steps} | dt={conf.dt}")

    # --- AGENTS
    agents = [
        Agent(agent_id=str(u), key=f"key-{u}".encode(), env=env, rng=random.Random(conf.random_seed + int(u)))
        for u in G.nodes()
    ]
    tasks = [asyncio.create_task(a.run()) for a in agents]

    # --- LOOP
    for step in range(conf.max_steps):
        env.step = step
        if step % conf.log_every == 0:
            # progress + adozioni finora
            adopted = sum(len(h) for h in env.history.values())
            print(f"[step {step}/{conf.max_steps}] adopted={adopted}")
        await asyncio.sleep(conf.dt)

    for t in tasks:
        t.cancel()

    print("Done.")



if __name__ == "__main__":
    asyncio.run(run_once())
