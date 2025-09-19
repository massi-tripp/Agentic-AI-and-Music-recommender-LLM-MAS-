# src/metrics_advanced.py
import json, pathlib, math, statistics as st
from collections import Counter, defaultdict, deque
from typing import Dict, List, Tuple, Iterable, Optional
import networkx as nx

# ---------- util ----------
def latest_log() -> pathlib.Path:
    logs = sorted(pathlib.Path("runs").rglob("messages.jsonl"))
    if not logs: raise FileNotFoundError("No runs/*/messages.jsonl found.")
    return logs[-1]

def load_events(p: pathlib.Path) -> List[dict]:
    return [json.loads(ln) for ln in open(p, "rb")]

def gini(xs: Iterable[int | float]) -> float:
    xs = [x for x in xs if x > 0]
    if not xs: return 0.0
    xs.sort()
    n = len(xs); s = sum(xs)
    cum = 0.0
    for i, x in enumerate(xs, start=1):
        cum += i * x
    return (2*cum)/(n*s) - (n+1)/n

def lorenz_points(xs: List[int]) -> List[Tuple[float,float]]:
    xs = sorted(xs)
    n = len(xs); s = sum(xs) or 1.0
    cum = 0.0
    pts = [(0.0, 0.0)]
    for i, x in enumerate(xs, start=1):
        cum += x
        pts.append((i/n, cum/s))
    return pts

# ---------- main analyzers ----------
class AdvancedMetrics:
    def __init__(self, events: List[dict]):
        self.events = events
        self.proposes = [e for e in events if e.get("type")=="PROPOSE"]
        self.adopts   = [e for e in events if e.get("type")=="ADOPT"]
        # quick indexes
        self.adopts_by_song: Dict[int, List[dict]] = defaultdict(list)
        self.proposes_by_song: Dict[int, List[dict]] = defaultdict(list)
        for e in self.adopts:  self.adopts_by_song[e["song_id"]].append(e)
        for e in self.proposes:self.proposes_by_song[e["song_id"]].append(e)

    # ---- Popularity / inequality ----
    def popularity(self) -> Dict:
        counts = Counter(e["song_id"] for e in self.adopts)
        vals = list(counts.values())
        return {
            "total_adopts": len(self.adopts),
            "unique_songs_adopted": len(counts),
            "top5": counts.most_common(5),
            "gini": round(gini(vals), 3),
            "herfindahl": round(sum((c/sum(vals))**2 for c in vals), 3) if vals else 0.0,
            "lorenz": lorenz_points(vals),  # per eventuale plot
        }

    # ---- Efficiency: proposals -> adopts ----
    def efficiency(self) -> Dict:
        total_p = len(self.proposes)
        total_a = len(self.adopts)
        overall_acc = total_a / total_p if total_p else 0.0
        # per-song acceptance
        acc_by_song = {}
        for sid in set(list(self.adopts_by_song.keys()) + list(self.proposes_by_song.keys())):
            p = len(self.proposes_by_song.get(sid, []))
            a = len(self.adopts_by_song.get(sid, []))
            acc_by_song[sid] = a / p if p else 0.0
        top_acc = sorted(acc_by_song.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return {
            "proposes": total_p,
            "adopts": total_a,
            "overall_acceptance": round(overall_acc, 3),
            "top5_acceptance_songs": top_acc[:5],
        }

    # ---- Diffusion graphs + cascade stats ----
    # Build adoption DAG per song (edge: sender -> receiver for each ADOPT)
    def diffusion_graph(self, song_id: int) -> nx.DiGraph:
        G = nx.DiGraph()
        G.add_edges_from((e["sender"], e["receiver"]) for e in self.adopts_by_song.get(song_id, []))
        return G

    # Choose a spanning tree: earliest parent per node (by step)
    def cascade_tree(self, song_id: int) -> Optional[nx.DiGraph]:
        adopts = sorted(self.adopts_by_song.get(song_id, []), key=lambda e: e["step"])
        if not adopts: return None
        first_step_by_node = {}
        parent_of = {}
        for e in adopts:
            r = e["receiver"]; s = e["sender"]
            if r not in first_step_by_node:
                first_step_by_node[r] = e["step"]
                parent_of[r] = s
            else:
                # already adopted earlier; keep earliest parent
                pass
        # roots are senders with no parent (or adopters whose parent is None)
        tree = nx.DiGraph()
        for r, s in parent_of.items():
            tree.add_edge(s, r)
        return tree

    def structural_virality(self, T: nx.DiGraph) -> float:
        # Goel et al. proxy: average shortest-path distance among all pairs in the cascade tree
        if T is None or T.number_of_nodes() < 2:
            return 0.0
        UG = T.to_undirected()
        nodes = list(UG.nodes())
        # all-pairs shortest paths on small graphs is fine
        dists = []
        for i in range(len(nodes)):
            sp = nx.single_source_shortest_path_length(UG, nodes[i])
            for j in range(i+1, len(nodes)):
                dj = sp.get(nodes[j])
                if dj is not None:
                    dists.append(dj)
        return sum(dists)/len(dists) if dists else 0.0

    def cascade_stats(self) -> Dict:
        rows = []
        for sid in self.adopts_by_song.keys():
            T = self.cascade_tree(sid)
            if T is None or T.number_of_nodes()==0:
                continue
            # depth (longest path length)
            depths = {}
            roots = [n for n in T.nodes() if T.in_degree(n)==0]
            for r in roots:
                # BFS depths from each root
                q = deque([(r,0)])
                seen = set([r])
                while q:
                    u,d = q.popleft()
                    depths[u] = max(depths.get(u,0), d)
                    for v in T.successors(u):
                        if v not in seen:
                            seen.add(v); q.append((v,d+1))
            max_depth = max(depths.values()) if depths else 0
            breadth_max = max((len(level) for level in self._levels(T, roots)), default=1)
            virality = round(self.structural_virality(T), 3)
            rows.append((sid, T.number_of_nodes(), max_depth, breadth_max, virality))
        # sort by size desc
        rows.sort(key=lambda r: r[1], reverse=True)
        top5 = rows[:5]
        return {"top5_cascades": top5, "avg_depth": round(st.mean([r[2] for r in rows]), 3) if rows else 0.0,
                "avg_virality": round(st.mean([r[4] for r in rows]), 3) if rows else 0.0}

    def _levels(self, T: nx.DiGraph, roots: List[str]) -> List[List[str]]:
        # level decomposition from roots (combine multiple roots)
        frontier = list(roots)
        seen = set(frontier)
        levels = []
        while frontier:
            levels.append(list(frontier))
            nxt = []
            for u in frontier:
                for v in T.successors(u):
                    if v not in seen:
                        seen.add(v); nxt.append(v)
            frontier = nxt
        return levels

    # ---- Reproduction number R (children per adopter) ----
    def reproduction(self) -> Dict:
        # aggregate across all songs: out-degree in adoption graphs
        outd = []
        for sid in self.adopts_by_song.keys():
            G = self.diffusion_graph(sid)
            outd.extend([G.out_degree(n) for n in G.nodes()])
        R = st.mean(outd) if outd else 0.0
        return {"R_mean": round(R, 3), "R_median": round(st.median(outd), 3) if outd else 0.0}

    # ---- Exposure-before-adoption (how many proposals did a receiver get before adopting that song?) ----
    def exposure(self) -> Dict:
        exp_counts = []
        proposes_by_rcv_song = defaultdict(list)  # (receiver,song)->steps
        for p in self.proposes:
            proposes_by_rcv_song[(p["receiver"], p["song_id"])].append(p["step"])
        for a in self.adopts:
            key = (a["receiver"], a["song_id"])
            steps = proposes_by_rcv_song.get(key, [])
            exp = sum(1 for s in steps if s < a["step"])
            exp_counts.append(exp)
        if not exp_counts:
            return {"mean_exposures": 0.0, "median_exposures": 0.0, "p95": 0}
        exp_counts.sort()
        p95 = exp_counts[int(0.95*len(exp_counts))-1]
        return {
            "mean_exposures": round(st.mean(exp_counts), 3),
            "median_exposures": st.median(exp_counts),
            "p95": p95
        }

def main():
    p = latest_log()
    ev = load_events(p)
    M = AdvancedMetrics(ev)

    pop = M.popularity()
    eff = M.efficiency()
    casc = M.cascade_stats()
    rep = M.reproduction()
    exp = M.exposure()

    print(f"Log: {p}")
    print("---- Popularity ----")
    print(pop)
    print("---- Efficiency ----")
    print(eff)
    print("---- Cascades ----")
    print(casc)
    print("---- Reproduction ----")
    print(rep)
    print("---- Exposure ----")
    print(exp)

if __name__ == "__main__":
    main()
