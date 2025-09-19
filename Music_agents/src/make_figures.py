# make_figures.py
# Genera le figure a partire dai JSONL in runs/*/messages.jsonl
import json, pathlib, collections, math
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# --- Configura i 4 run (metti i tuoi percorsi reali) ---
RUNS = {
    "T1_noLLM_120": "runs/demo-20250827-165201/messages.jsonl",
    "T1_LLM_120":   "runs/demo-20250911-151127/messages.jsonl",
    "T2_noLLM_200": "runs/demo-20250908-143932/messages.jsonl",
    "T2_LLM_200":   "runs/demo-20250911-163711/messages.jsonl",
}

FIGDIR = Path("figs")
FIGDIR.mkdir(exist_ok=True)

def load_events(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File non trovato: {p}")
    with open(p, "rb") as f:
        for ln in f:
            yield json.loads(ln)

def adoption_curve(events):
    # cumulative ADOPT vs step
    by_step = collections.Counter()
    last_step = 0
    for e in events:
        if e.get("type") == "ADOPT":
            s = int(e.get("step", 0))
            by_step[s] += 1
            last_step = max(last_step, s)
    xs = sorted(by_step.keys())
    if not xs:
        return np.array([0]), np.array([0])
    max_step = max(xs)
    arr = np.zeros(max_step + 1, dtype=int)
    for s, c in by_step.items():
        arr[s] = c
    cum = np.cumsum(arr)
    return np.arange(len(cum)), cum

def propose_adopt(events):
    p = a = 0
    for e in events:
        t = e.get("type")
        if t == "PROPOSE": p += 1
        elif t == "ADOPT": a += 1
    acc = a / p if p else 0.0
    return p, a, acc

def song_popularity(events):
    cnt = collections.Counter()
    for e in events:
        if e.get("type") == "ADOPT":
            cnt[int(e["song_id"])] += 1
    return cnt

def lorenz_points(values):
    xs = sorted(values)
    n = len(xs)
    s = sum(xs) or 1.0
    cum = 0
    pts = [(0.0, 0.0)]
    for i, x in enumerate(xs, start=1):
        cum += x
        pts.append((i / n, cum / s))
    return pts

def gini(values):
    xs = sorted(values)
    n = len(xs)
    if n == 0: return 0.0
    s = sum(xs)
    if s == 0: return 0.0
    cum = 0
    for i, x in enumerate(xs, start=1):
        cum += i * x
    return (2 * cum) / (n * s) - (n + 1) / n

def exposure_stats(events):
    proposes = collections.defaultdict(list)  # (receiver,song)->[steps]
    adopts = []
    for e in events:
        if e.get("type") == "PROPOSE":
            key = (e["receiver"], e["song_id"])
            proposes[key].append(int(e.get("step", 0)))
        elif e.get("type") == "ADOPT":
            adopts.append((e["receiver"], e["song_id"], int(e.get("step", 0))))
    exposures = []
    for r, sid, step in adopts:
        steps = proposes.get((r, sid), [])
        exposures.append(sum(1 for s in steps if s < step))
    exposures.sort()
    if not exposures:
        return dict(mean=0.0, median=0.0, p95=0, all=[])
    p95 = exposures[int(0.95 * len(exposures)) - 1] if len(exposures) >= 20 else (exposures[-1] if exposures else 0)
    import statistics as st
    return dict(mean=round(st.mean(exposures),3),
                median=(st.median(exposures) if exposures else 0),
                p95=p95,
                all=exposures)

def decisions_mix(events):
    llm = heur = 0
    for e in events:
        if e.get("type") == "DECISION":
            src = e.get("source", "")
            if src == "llm": llm += 1
            elif src == "heuristic": heur += 1
    return llm, heur

# -------- Carica e pre-elabora tutti i run --------
DATA = {}
for name, path in RUNS.items():
    ev = list(load_events(path))
    xs, cum = adoption_curve(ev)
    p, a, acc = propose_adopt(ev)
    pop = song_popularity(ev)
    lor = lorenz_points(list(pop.values()) or [0])
    g = gini(list(pop.values()))
    exp = exposure_stats(ev)
    llm, heur = decisions_mix(ev)
    DATA[name] = dict(events=ev, xs=xs, cum=cum, propose=p, adopt=a, acc=acc,
                      pop=pop, lor=lor, gini=g, exposure=exp, llm=llm, heur=heur)

# ----------------- FIGURE 1: curve di adozione -----------------
plt.figure(figsize=(7,4))
for name, d in DATA.items():
    plt.plot(d["xs"], d["cum"], label=f"{name}")
plt.xlabel("step")
plt.ylabel("adozioni cumulative")
plt.legend()
plt.tight_layout()
plt.savefig(FIGDIR / "adoption_cumulative.pdf")
plt.savefig(FIGDIR / "adoption_cumulative.png", dpi=200)
plt.close()

# ----------------- FIGURE 2: PROPOSE/ADOPT + acceptance --------
labels = list(DATA.keys())
proposes = [DATA[k]["propose"] for k in labels]
adopts   = [DATA[k]["adopt"]   for k in labels]
accs     = [DATA[k]["acc"]     for k in labels]
x = np.arange(len(labels))
w = 0.35# make_plots.py
from pathlib import Path
from collections import Counter, defaultdict
import json
import math
import os

import numpy as np
import matplotlib.pyplot as plt

# ---------- [1] Config: etichette -> cartelle run (contengono messages.jsonl) ----------
RUNS = {
    "T1_noLLM_120": "runs/demo-20250827-165201",
    "T1_LLM_120"  : "runs/demo-20250911-151127",
    "T2_noLLM_200": "runs/demo-20250908-143932",
    "T2_LLM_200"  : "runs/demo-20250911-163711",
}

OUTDIR = Path("fig")
OUTDIR.mkdir(parents=True, exist_ok=True)

# ---------- [2] Util ----------
def find_log(run_dir: str | Path) -> Path:
    run_dir = Path(run_dir)
    if run_dir.is_file() and run_dir.name.endswith(".jsonl"):
        return run_dir
    cands = sorted(run_dir.rglob("messages.jsonl"))
    if not cands:
        raise FileNotFoundError(f"Nessun messages.jsonl in {run_dir}")
    return cands[-1]

def load_events(log_path: Path):
    ev = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            try:
                ev.append(json.loads(line))
            except json.JSONDecodeError:
                # a volte qualche riga di debug sporca: skippa
                continue
    return ev

def gini(xs):
    xs = [x for x in xs if x > 0]
    if not xs:
        return 0.0
    xs.sort()
    n = len(xs)
    cum = 0.0
    s = sum(xs)
    for i, x in enumerate(xs, 1):
        cum += i * x
    return (2 * cum) / (n * s) - (n + 1) / n

def lorenz_points(xs):
    xs = sorted([x for x in xs if x >= 0])
    s = sum(xs)
    if s <= 0:
        return [(0.0, 0.0), (1.0, 1.0)]
    cum = np.cumsum(xs) / s
    x = np.linspace(0, 1, len(xs) + 1)
    y = np.concatenate([[0.0], cum])
    return list(zip(x, y))

# ---------- [3] Estrazione metriche da un run ----------
def metrics_from_events(events):
    proposes = sum(1 for e in events if e.get("type") == "PROPOSE")
    adopts   = [e for e in events if e.get("type") == "ADOPT"]
    adopts_c = len(adopts)
    dec_llm  = sum(1 for e in events if e.get("type") == "DECISION" and e.get("source") == "llm")
    dec_heu  = sum(1 for e in events if e.get("type") == "DECISION" and e.get("source") == "heuristic")

    by_song = Counter(e["song_id"] for e in adopts if "song_id" in e)
    counts  = list(by_song.values())
    Lpoints = lorenz_points(counts)
    G       = round(gini(counts), 3)

    return {
        "proposes": proposes,
        "adopts": adopts_c,
        "dec_llm": dec_llm,
        "dec_heur": dec_heu,
        "by_song": by_song,
        "lorenz": Lpoints,
        "gini": G,
    }

# ---------- [4] Carica tutti i run ----------
def collect_all():
    allm = {}
    for label, rpath in RUNS.items():
        log = find_log(rpath)
        ev = load_events(log)
        allm[label] = metrics_from_events(ev)
        print(f"[OK] {label}: {log} | PROPOSE={allm[label]['proposes']} ADOPT={allm[label]['adopts']} "
              f"DEC(llm/heur)={allm[label]['dec_llm']}/{allm[label]['dec_heur']} G={allm[label]['gini']}")
    return allm

# ---------- [5] Plot: Lorenz ----------
def plot_lorenz(allm):
    plt.figure(figsize=(8,5))
    # diagonale perfetta eguaglianza
    xs = np.linspace(0,1,100)
    plt.plot(xs, xs, linestyle="--", alpha=0.5)

    for label, m in allm.items():
        pts = np.array(m["lorenz"])
        plt.plot(pts[:,0], pts[:,1], label=f"{label} (G={m['gini']})")

    plt.xlabel("quota brani (cumul.)")
    plt.ylabel("quota adozioni (cumul.)")
    plt.legend(loc="lower right")
    plt.title("Curva di Lorenz delle adozioni")
    out = OUTDIR / "lorenz_all.png"
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    print(f"[SAVE] {out}")

# ---------- [6] Plot: Efficienza separata ----------
def plot_efficiency_split(allm):
    # separa run con/without LLM (dec_llm > 0)
    no_llm = {k:v for k,v in allm.items() if v["dec_llm"] == 0}
    yes_llm = {k:v for k,v in allm.items() if v["dec_llm"] > 0}

    def plot_group(group, title, out_name):
        if not group:
            print(f"[WARN] nessun run per {title}")
            return
        labels = list(group.keys())
        proposes = [group[k]["proposes"] for k in labels]
        adopts   = [group[k]["adopts"] for k in labels]
        acc = [ (a/p) if p>0 else 0.0 for a,p in zip(adopts, proposes) ]

        x = np.arange(len(labels))
        w = 0.35

        plt.figure(figsize=(8,5))
        plt.bar(x - w/2, proposes, width=w, label="PROPOSE")
        plt.bar(x + w/2, adopts,   width=w, label="ADOPT")
        for i,(xi, ai, pi) in enumerate(zip(x, adopts, proposes)):
            txt = f"acc={acc[i]:.3f}"
            plt.text(xi, max(ai,pi)*1.02 if max(ai,pi)>0 else 1, txt, ha="center", va="bottom", fontsize=9)

        plt.xticks(x, labels, rotation=12)
        plt.ylabel("conteggi")
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        out = OUTDIR / out_name
        plt.savefig(out, dpi=220)
        print(f"[SAVE] {out}")

    plot_group(no_llm, "Efficienza — run senza LLM", "efficiency_noLLM.png")
    plot_group(yes_llm, "Efficienza — run con LLM",   "efficiency_LLM.png")

# ---------- [7] Plot: Top-5 separati ----------
def plot_top5_split(allm):
    no_llm = [k for k,v in allm.items() if v["dec_llm"] == 0]
    yes_llm = [k for k,v in allm.items() if v["dec_llm"] > 0]

    def plot_group(labels, out_name, title):
        if not labels:
            print(f"[WARN] nessun run per {title}")
            return
        cols = 2
        rows = math.ceil(len(labels) / cols)
        plt.figure(figsize=(9, 3.5*rows))
        for i, label in enumerate(labels, start=1):
            by_song = allm[label]["by_song"]
            top5 = by_song.most_common(5)
            xs = [str(sid) for sid,_ in top5]
            ys = [cnt for _,cnt in top5]
            ax = plt.subplot(rows, cols, i)
            ax.bar(xs, ys)
            ax.set_title(f"{label} — Top-5 adozioni")
            ax.set_ylim(0, max(ys + [1]) * 1.2)
        plt.suptitle(title)
        plt.tight_layout(rect=[0,0,1,0.96])
        out = OUTDIR / out_name
        plt.savefig(out, dpi=220)
        print(f"[SAVE] {out}")

    plot_group(no_llm, "top5_noLLM.png", "Top-5 brani — run senza LLM")
    plot_group(yes_llm, "top5_LLM.png",  "Top-5 brani — run con LLM")

# ---------- [8] Main ----------
if __name__ == "__main__":
    allm = collect_all()
    plot_lorenz(allm)
    plot_efficiency_split(allm)
    plot_top5_split(allm)
    print("[DONE]")

plt.figure(figsize=(7,4))
plt.bar(x - w/2, proposes, width=w, label="PROPOSE")
plt.bar(x + w/2, adopts,   width=w, label="ADOPT")
for i, a in enumerate(accs):
    plt.text(x[i], max(proposes[i], adopts[i]) * 1.02, f"acc={a:.3f}", ha="center", va="bottom", fontsize=9)
plt.xticks(x, labels, rotation=15)
plt.ylabel("conteggi")
plt.legend()
plt.tight_layout()
plt.savefig(FIGDIR / "propose_adopt_bars.pdf")
plt.savefig(FIGDIR / "propose_adopt_bars.png", dpi=200)
plt.close()

# ----------------- FIGURE 3: Lorenz -----------------------------
plt.figure(figsize=(7,4))
for name, d in DATA.items():
    xs, ys = zip(*d["lor"])
    plt.plot(xs, ys, label=f"{name} (G={d['gini']:.3f})")
plt.plot([0,1],[0,1], linestyle="--", linewidth=1)  # equidistribuzione
plt.xlabel("quota brani (cumul.)")
plt.ylabel("quota adozioni (cumul.)")
plt.legend()
plt.tight_layout()
plt.savefig(FIGDIR / "lorenz_popularity.pdf")
plt.savefig(FIGDIR / "lorenz_popularity.png", dpi=200)
plt.close()

# ----------------- FIGURE 4: Exposure ECDF ---------------------
plt.figure(figsize=(7,4))
for name, d in DATA.items():
    arr = np.array(d["exposure"]["all"])
    if arr.size == 0: continue
    xs = np.sort(arr)
    ys = np.arange(1, len(xs)+1) / len(xs)
    plt.step(xs, ys, where="post", label=f"{name} (med={d['exposure']['median']})")
plt.xlabel("proposte prima dell'adozione")
plt.ylabel("ECDF")
plt.xlim(left=0)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(FIGDIR / "exposure_ecdf.pdf")
plt.savefig(FIGDIR / "exposure_ecdf.png", dpi=200)
plt.close()

# ----------------- FIGURE 5: Decisions LLM vs euristica --------
plt.figure(figsize=(7,4))
x = np.arange(len(labels))
llms  = [DATA[k]["llm"]  for k in labels]
heurs = [DATA[k]["heur"] for k in labels]
plt.bar(x - w/2, heurs, width=w, label="Heuristic")
plt.bar(x + w/2, llms,  width=w, label="LLM")
plt.xticks(x, labels, rotation=15)
plt.ylabel("# decisioni")
plt.legend()
plt.tight_layout()
plt.savefig(FIGDIR / "decisions_mix.pdf")
plt.savefig(FIGDIR / "decisions_mix.png", dpi=200)
plt.close()

# ----------------- FIGURE 6 (facoltativa): Top-5 per adozioni ---
plt.figure(figsize=(7,5))
rows = 2; cols = 2
i = 1
for name, d in DATA.items():
    top5 = d["pop"].most_common(5)
    plt.subplot(rows, cols, i)
    if top5:
        sid = [str(s) for s,_ in top5]
        cnt = [c for _,c in top5]
        plt.bar(sid, cnt)
        plt.title(f"{name} — Top-5 adozioni")
    else:
        plt.title(f"{name} — (nessun dato)")
    i += 1
plt.tight_layout()
plt.savefig(FIGDIR / "top5_popularity.pdf")
plt.savefig(FIGDIR / "top5_popularity.png", dpi=200)
plt.close()

print("Figure salvate in:", FIGDIR.resolve())
