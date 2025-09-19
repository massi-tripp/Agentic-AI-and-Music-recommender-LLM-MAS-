# src/petri.py
from dataclasses import dataclass
from typing import Dict, Tuple, List, Callable, Set

Marking = Tuple[int, int, int]  # (att, inbox, feed)

@dataclass(frozen=True)
class Transition:
    name: str
    pre: Tuple[int, int, int]          # tokens required from (att, inbox, feed)
    post: Tuple[int, int, int]         # tokens produced   to (att, inbox, feed)
    guard: Callable[[Marking], bool] | None = None

def enabled(t: Transition, m: Marking) -> bool:
    a,i,f = m; pa,pi,pf = t.pre
    if a < pa or i < pi or f < pf:
        return False
    return True if (t.guard is None or t.guard(m)) else False

def fire(t: Transition, m: Marking) -> Marking:
    a,i,f = m; pa,pi,pf = t.pre; ra,ri,rf = t.post
    return (a - pa + ra, i - pi + ri, f - pf + rf)

def build_net(att_max: int, inbox_max: int, feed_max: int) -> Tuple[List[Transition], Callable[[Marking], bool]]:
    # Guards
    def g_refill(m: Marking) -> bool:
        return m[0] < att_max  # att < att_max

    def g_receive(m: Marking) -> bool:
        return m[1] < inbox_max and m[2] > 0

    T = [
        Transition("receive", pre=(0,0,1), post=(0,1,0), guard=g_receive),      # feed->inbox
        Transition("consume", pre=(1,1,0), post=(0,0,1), guard=None),           # att+inbox->feed
        Transition("refill",  pre=(0,0,0), post=(1,0,0), guard=g_refill),       # ->att  (bounded by guard)
    ]
    def within_bounds(m: Marking) -> bool:
        a,i,f = m
        return 0 <= a <= att_max and 0 <= i <= inbox_max and 0 <= f <= feed_max
    return T, within_bounds

def explore(initial: Marking, T: List[Transition], within_bounds: Callable[[Marking], bool], depth: int = 30) -> Tuple[Set[Marking], bool, bool]:
    """
    Returns: (reachable_markings, is_bounded, has_deadlock)
    Bounded = never leaves bounds during exploration.
    Deadlock = exists a reachable marking where no transition enabled (excluding refill-only loops).
    """
    seen: Set[Marking] = set([initial])
    frontier = [initial]
    bounded = True
    deadlock_found = False
    steps = 0

    while frontier and steps < depth:
        m = frontier.pop()
        steps += 1
        en = [t for t in T if enabled(t, m)]
        # consider deadlock when no transitions except maybe 'refill' are enabled
        if not en or all(t.name == "refill" for t in en):
            # if only refill is possible forever and att==0 and inbox==0 and feed==0 -> real deadlock
            if not en or (len(en)==1 and en[0].name=="refill" and m[1]==0 and m[2]==0):
                deadlock_found = True
        for t in en:
            m2 = fire(t, m)
            if not within_bounds(m2):
                bounded = False
            if m2 not in seen:
                seen.add(m2)
                frontier.append(m2)
    return seen, bounded, deadlock_found

# Quick helper for CLI/dev use
def quick_check(att_max=5, inbox_max=10, feed_max=10, att0=5, inbox0=0, feed0=5) -> None:
    T, within = build_net(att_max, inbox_max, feed_max)
    reachable, bounded, dead = explore((att0, inbox0, feed0), T, within, depth=200)
    print(f"reachable={len(reachable)} states | bounded={bounded} | deadlock={dead}")
