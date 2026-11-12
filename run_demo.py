from synth import generate
from score import score


def main(hard=False):
    print("HARD" if hard else "EASY")
    firms, invoices, rings = generate(hard=hard)
    fraud = {f for f, d in firms.items() if d["fraud"]}
    sc = score(invoices)
    ranked = sorted(sc, key=sc.get, reverse=True)

    print(f"firms: {len(firms)}  invoices: {len(invoices)}  "
          f"fraud firms: {len(fraud)} in {len(rings)} rings")
    for k in (len(fraud), 2 * len(fraud), 5 * len(fraud)):
        top = set(ranked[:k])
        hit = len(top & fraud)
        print(f"top {k:4d}: precision {hit / k:5.1%}  recall {hit / len(fraud):5.1%}")
    ring_hit = sum(1 for r in rings if sum(f in set(ranked[:len(fraud)]) for f in r) >= len(r) // 2 + 1)
    print(f"rings mostly caught in top {len(fraud)}: {ring_hit}/{len(rings)}")


if __name__ == "__main__":
    main(False)
    main(True)
