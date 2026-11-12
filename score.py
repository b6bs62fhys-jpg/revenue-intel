"""Baseline risk scoring on the invoice graph.

Signals per firm (all computable from e-invoice data alone):
  cycle_share  share of its sales value flowing in a closed loop of other
               firms (strongly connected component with >= 3 members)
  short_life   active for few months relative to turnover
  burst        turnover per active month, relative to peers
Final score = weighted mix, rank-normalised. No labels needed.
"""
from collections import defaultdict
import math
import networkx as nx


def build_graph(invoices):
    g = nx.DiGraph()
    for inv in invoices:
        if g.has_edge(inv.seller, inv.buyer):
            g[inv.seller][inv.buyer]["w"] += inv.net
            g[inv.seller][inv.buyer]["months"].add(inv.month)
        else:
            g.add_edge(inv.seller, inv.buyer, w=inv.net, months={inv.month})
    return g


def score(invoices):
    g = build_graph(invoices)
    sales = defaultdict(float)
    active = defaultdict(set)
    for inv in invoices:
        sales[inv.seller] += inv.net
        active[inv.seller].add(inv.month)
        active[inv.buyer].add(inv.month)

    # strongly connected components: loops of 3+ firms
    in_loop = defaultdict(float)
    for comp in nx.strongly_connected_components(g):
        if len(comp) < 3:
            continue
        sub = g.subgraph(comp)
        for u, v, d in sub.edges(data=True):
            in_loop[u] += d["w"]

    raw = {}
    for f in g.nodes:
        s = sales[f] or 1.0
        cycle_share = min(1.0, in_loop[f] / s)
        life = len(active[f])
        short_life = 1.0 / (1.0 + max(0, life - 3))
        burst = math.log1p(s / max(life, 1))
        raw[f] = (cycle_share, short_life, burst)

    bmax = max(r[2] for r in raw.values()) or 1.0
    return {f: 0.6 * c + 0.25 * sl + 0.15 * (b / bmax)
            for f, (c, sl, b) in raw.items()}
