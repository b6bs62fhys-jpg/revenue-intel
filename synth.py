"""Synthetic B2B invoice data with planted VAT carousel fraud.

Honest trade: firms invoice a few suppliers/customers in a roughly layered
supply chain. Fraud: rings of short-lived firms that pass goods in a circle,
with one "missing trader" that collects VAT and disappears.
"""
import random
from dataclasses import dataclass


@dataclass
class Invoice:
    seller: int
    buyer: int
    net: float
    vat: float
    month: int  # 0..23


def generate(n_honest=2000, n_rings=12, ring_size=(4, 7), months=24, seed=7,
             hard=False):
    """hard=True: honest long-lived loops exist, fraud rings leak (drop
    months, mix in honest-looking trade, and last longer)."""
    rng = random.Random(seed)
    firms = {}  # id -> dict(start, end, fraud)
    invoices = []

    # honest firms, three tiers (producer -> wholesale -> retail)
    tiers = [[], [], []]
    for i in range(n_honest):
        t = rng.choices([0, 1, 2], weights=[0.25, 0.35, 0.40])[0]
        start = rng.randint(0, 6)
        firms[i] = dict(start=start, end=months, fraud=False, tier=t)
        tiers[t].append(i)

    for t in (0, 1):
        for seller in tiers[t]:
            for _ in range(rng.randint(2, 6)):
                buyer = rng.choice(tiers[t + 1])
                for m in range(firms[seller]["start"] + 1, months):
                    if rng.random() < 0.55:
                        net = rng.lognormvariate(8.5, 0.9)
                        invoices.append(Invoice(seller, buyer, net, net * 0.19, m))
    # some honest two-way trade so cycles are not a perfect signal
    for _ in range(80):
        a, b = rng.sample(tiers[1], 2)
        for m in rng.sample(range(8, months), 6):
            n1 = rng.lognormvariate(7.5, 0.6)
            invoices.append(Invoice(a, b, n1, n1 * 0.19, m))
            n2 = rng.lognormvariate(7.5, 0.6)
            invoices.append(Invoice(b, a, n2, n2 * 0.19, m))

    # hard mode: honest loops (e.g. tolling, return flows, group firms)
    if hard:
        for _ in range(60):
            size = rng.randint(3, 5)
            ids = rng.sample(tiers[1], size)
            for m in rng.sample(range(2, months), rng.randint(8, 18)):
                amount = rng.lognormvariate(8.8, 0.5)
                for k in range(size):
                    invoices.append(Invoice(ids[k], ids[(k + 1) % size],
                                            amount, amount * 0.19, m))

    # fraud rings
    next_id = n_honest
    ring_ids = []
    for _ in range(n_rings):
        size = rng.randint(*ring_size)
        ids = list(range(next_id, next_id + size))
        next_id += size
        start = rng.randint(8, 16)
        life = rng.randint(8, 14) if hard else rng.randint(4, 7)
        for f in ids:
            firms[f] = dict(start=start, end=start + life, fraud=True, tier=1)
        ring_ids.append(ids)
        base = rng.lognormvariate(10.5, 0.5)
        for rep in range(life):
            m = start + rep
            if m >= months:
                break
            amount = base * (1 + 0.04 * rep)
            for k in range(size):
                s, b = ids[k], ids[(k + 1) % size]
                if hard and rng.random() < 0.25:
                    continue  # leaky ring: missing legs
                invoices.append(Invoice(s, b, amount, amount * 0.19, m))
            if hard:  # honest-looking cover business
                for f in ids:
                    cover = amount * rng.uniform(0.6, 1.6)
                    invoices.append(Invoice(f, rng.choice(tiers[2]), cover,
                                            cover * 0.19, m))
            # exit leg to an honest retailer from a ring member
            out = rng.choice(tiers[2])
            invoices.append(Invoice(ids[0], out, amount * 1.05,
                                    amount * 1.05 * 0.19, m))
    return firms, invoices, ring_ids
