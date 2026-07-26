#!/usr/bin/env python
"""Exercises agent-loop/tools/orchestrator.py's deterministic decision functions with synthetic scores
-- no API key or network access required.

Run: python agent-loop/tests/test_orchestrator.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import orchestrator

HATS = {
    "white": {"lens": "facts", "weight": 1.0, "pass_threshold": 8},
    "yellow": {"lens": "value", "weight": 0.8, "pass_threshold": 6},
    "black": {"lens": "risk", "weight": 1.5, "pass_threshold": 7},
    "red": {"lens": "feelings", "weight": 0.9, "pass_threshold": 6},
    "green": {"lens": "creativity", "weight": 0.5, "pass_threshold": 4},
    "blue": {"lens": "process", "weight": 0.6, "pass_threshold": 6},
}
VETO_HATS = ["black"]


def s(score, justification="because"):
    return {"score": score, "justification": justification}


def check(label, condition):
    status = "ok" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    # --- failing_hats ---
    all_pass = {h: s(9) for h in HATS}
    results.append(check("failing_hats: empty when everything passes", orchestrator.failing_hats(all_pass, HATS) == []))

    one_fail = {**all_pass, "white": s(5)}
    results.append(check("failing_hats: catches a single failure", orchestrator.failing_hats(one_fail, HATS) == ["white"]))

    # --- veto_triggered ---
    results.append(check("veto_triggered: None when black passes", orchestrator.veto_triggered(all_pass, HATS, VETO_HATS) is None))
    risky = {**all_pass, "black": s(3)}
    results.append(check("veto_triggered: fires when black fails", orchestrator.veto_triggered(risky, HATS, VETO_HATS) == "black"))
    results.append(check("veto_triggered: non-veto hat failing doesn't trigger veto",
                          orchestrator.veto_triggered({**all_pass, "green": s(1)}, HATS, VETO_HATS) is None))

    # --- aggregate_score: weighted, not simple mean ---
    # black (weight 1.5, score 10) should pull the average up more than green (weight 0.5, score 10) would.
    high_black = {**all_pass, "black": s(10)}
    high_green = {**all_pass, "green": s(10)}
    agg_black = orchestrator.aggregate_score(high_black, HATS)
    agg_green = orchestrator.aggregate_score(high_green, HATS)
    results.append(check("aggregate_score: higher-weight hat moves the aggregate more than a lower-weight one",
                          agg_black > agg_green))

    # --- choose_repair_lens: veto failure always outranks non-veto failures ---
    both_failing = {**all_pass, "black": s(6), "white": s(1)}  # white is *further* below its own threshold than black
    failing = orchestrator.failing_hats(both_failing, HATS)
    chosen = orchestrator.choose_repair_lens(failing, both_failing, HATS, VETO_HATS)
    results.append(check("choose_repair_lens: veto hat wins even when another hat is further below its threshold",
                          chosen == "risk"))

    # --- choose_repair_lens: among non-veto failures, the furthest-below-threshold wins ---
    non_veto_failing = {**all_pass, "yellow": s(5), "green": s(1)}  # yellow: -1 below threshold; green: -3 below
    failing2 = orchestrator.failing_hats(non_veto_failing, HATS)
    chosen2 = orchestrator.choose_repair_lens(failing2, non_veto_failing, HATS, VETO_HATS)
    results.append(check("choose_repair_lens: picks the hat furthest below its own threshold among non-veto failures",
                          chosen2 == "creativity"))

    # --- choose_repair_lens: raises rather than silently picking something when nothing is failing ---
    try:
        orchestrator.choose_repair_lens([], all_pass, HATS, VETO_HATS)
        results.append(check("choose_repair_lens: raises when called with no failing hats", False))
    except ValueError:
        results.append(check("choose_repair_lens: raises when called with no failing hats", True))

    # --- passing_axes ---
    failing3 = ["white"]
    passing = orchestrator.passing_axes(one_fail, HATS, failing3)
    results.append(check("passing_axes: excludes the failing hat's lens", "facts" not in passing))
    results.append(check("passing_axes: includes every other lens", set(passing) == {"value", "risk", "feelings", "creativity", "process"}))

    if not all(results):
        print(f"\n{results.count(False)} FAILURE(S)")
        return 1
    print(f"\nAll {len(results)} orchestrator checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
