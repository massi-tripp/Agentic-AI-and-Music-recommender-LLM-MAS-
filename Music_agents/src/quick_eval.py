import json, pathlib, collections, math
import networkx as nx

def gini(xs):
    xs = sorted(x for x in xs if x>0)
    if not xs: return 0.0
    n, s = len(xs), sum(xs)
    cum = 0
    for i, x in enumerate(xs, 1):
        cum += i * x
    return (2*cum)/(n*s) - (n+1)/n

def latest_log():
    return sorted(pathlib.Path("runs").rglob("messages.jsonl"))[-1]

def load_events(p):
    for ln in open(p, "rb"):
        yield json.loads(ln)

def main():
    p = latest_log()
    events = list(load_events(p))
    adopts = [e for e in events if e.get("type")=="ADOPT"]
    print(f"log: {p} | ADOPT events: {len(adopts)}")

    # Popolarità per song
    pop = collections.Counter(e["song_id"] for e in adopts)
    print("Top-5 songs by adoption:", pop.most_common(5))
    print("Gini(popularity):", round(gini(list(pop.values())), 3))

    # Cascade per song (dimensione componente in grafo di diffusion)
    cascade_sizes = {}
    for song_id, edges in collections.defaultdict(list).items():
        pass  # placeholder

    # costruiamo una volta sola:
    by_song = collections.defaultdict(list)
    for e in adopts:
        by_song[e["song_id"]].append((e["sender"], e["receiver"]))
    top_casc = []
    for sid, edge_list in by_song.items():
        G = nx.DiGraph()
        G.add_edges_from(edge_list)  # sender -> receiver
        # componente più grande (sul grafo non orientato)
        if G.number_of_nodes():
            cc = max(nx.connected_components(G.to_undirected()), key=len)
            top_casc.append((sid, len(cc)))
    top_casc.sort(key=lambda x: x[1], reverse=True)
    print("Top-5 cascades (song_id, size):", top_casc[:5])

if __name__ == "__main__":
    main()
