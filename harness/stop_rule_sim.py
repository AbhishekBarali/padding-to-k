#!/usr/bin/env python3
"""stop_rule_sim.py: how often the pilot stop rule stops, goes or hesitates, by simulation.

    python harness/stop_rule_sim.py [--base 0.15] [--sims 600]

A simulation under stated assumptions, not a measurement of any model. Assumptions: 60 documents,
3 models, k = 3 and 5, the no-count floor answered once per document and model, floor over-count rate
--base (default 15%), document logit SD 1.0, model SD 0.7, document x model SD 0.7, a document-specific
condition effect SD 0.6. The rule (RUN-PLAN 5.2): STOP if the upper end of the 95% bootstrap interval
of the paired difference is under 10 points; GO if the lower end is above 0; otherwise CAUTION.
Results on 13 Oct 2026 (seed 20261014, 600 simulations, 1000 bootstrap draws):
  true gap  0 points: stop 0.75, go 0.05, caution 0.20
  true gap  5 points: stop 0.25, go 0.37, caution 0.38
  true gap 10 points: stop 0.03, go 0.82, caution 0.14
  true gap 15 points: stop 0.00, go 0.98, caution 0.02
  true gap 20 points: stop 0.00, go 1.00, caution 0.00
Rerun it with the pilot's own floor rate once that is known, and put the table in the stage-2 registration.
"""
import argparse

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", type=float, default=0.15)
    ap.add_argument("--sims", type=int, default=600)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--docs", type=int, default=60)
    ap.add_argument("--models", type=int, default=3)
    args = ap.parse_args()
    rng = np.random.default_rng(20261014)
    D, M, K = args.docs, args.models, 2
    logit = lambda p: np.log(p / (1 - p))
    expit = lambda x: 1 / (1 + np.exp(-x))
    z = rng.normal(size=20000) * np.sqrt(1.0 ** 2 + 0.7 ** 2 + 0.7 ** 2)
    pop0 = expit(logit(args.base) + z).mean()
    shifts = np.linspace(0, 4, 401)
    pops = np.array([expit(logit(args.base) + s + z).mean() for s in shifts])
    for delta in [0.0, 0.05, 0.10, 0.15, 0.20, 0.30]:
        s = shifts[np.argmin(abs(pops - pop0 - delta))]
        out = {"stop": 0, "go": 0, "caution": 0}
        for _ in range(args.sims):
            eta0 = (logit(args.base) + rng.normal(0, 1.0, (D, 1)) + rng.normal(0, 0.7, (1, M))
                    + rng.normal(0, 0.7, (D, M)))
            c_d = rng.normal(0, 0.6, (D, 1))
            y0 = rng.random((D, M)) < expit(eta0)
            y1 = rng.random((D, M, K)) < expit(eta0[..., None] + s + c_d[..., None])
            diff = y1.mean(axis=(1, 2)) - y0.mean(axis=1)
            b = diff[rng.integers(0, D, (args.boot, D))].mean(axis=1)
            lo, hi = np.percentile(b, [2.5, 97.5])
            out["stop" if hi < 0.10 else "go" if lo > 0 else "caution"] += 1
        print(f"true gap {int(delta * 100):2d} points: " + ", ".join(f"{k} {v / args.sims:.2f}" for k, v in out.items()))


if __name__ == "__main__":
    main()
