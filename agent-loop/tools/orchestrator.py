"""Deterministic orchestrator decisions: which hats failed, whether a veto fired, the aggregate
convergence score, and which lens gets repaired next. Kept separate from run_loop.py's API/CLI glue so
these can be unit-tested with synthetic scores and no network access -- see
agent-loop/tests/test_orchestrator.py.

This takes the repo's "hard guardrails, not soft prompts" principle one step further than just the veto
check: *which axis gets repaired next* is also a deterministic function of the numeric scores, never left
to an LLM's own judgment of "what's worst here." run_loop.py still makes a Diagnostic LLM call, but only to
explain *why* the orchestrator's already-chosen axis failed and to draft the preservation note -- not to
decide *which* axis to fix.
"""


def failing_hats(scores: dict, hats_by_id: dict) -> list:
    """Hat ids whose score is below their own pass_threshold."""
    return [
        hat_id for hat_id, result in scores.items()
        if result["score"] < hats_by_id[hat_id]["pass_threshold"]
    ]


def veto_triggered(scores: dict, hats_by_id: dict, veto_hats: list) -> str | None:
    """The first veto hat id whose score is below its own pass_threshold, or None if no veto fired."""
    for hat_id in veto_hats:
        if hat_id in scores and scores[hat_id]["score"] < hats_by_id[hat_id]["pass_threshold"]:
            return hat_id
    return None


def aggregate_score(scores: dict, hats_by_id: dict) -> float:
    """Weighted average score -- used only by the convergence/improvement-delta check, never for
    pass/fail. Pass/fail is failing_hats()/veto_triggered()'s job alone; see agent-loop/README.md's
    Design Principles for why conflating the two was a real problem in the source material."""
    total_weight = sum(hats_by_id[hat_id]["weight"] for hat_id in scores)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(scores[hat_id]["score"] * hats_by_id[hat_id]["weight"] for hat_id in scores)
    return weighted_sum / total_weight


def choose_repair_lens(failing: list, scores: dict, hats_by_id: dict, veto_hats: list) -> str:
    """Deterministically picks which lens to repair next. A veto-hat failure always outranks every
    non-veto failure, no matter how far under threshold the others are; among candidates of the same
    priority, the hat furthest below its own threshold (in absolute score terms) is chosen."""
    if not failing:
        raise ValueError("choose_repair_lens called with no failing hats")

    veto_failures = [h for h in failing if h in veto_hats]
    candidates = veto_failures if veto_failures else failing
    worst = min(candidates, key=lambda h: scores[h]["score"] - hats_by_id[h]["pass_threshold"])
    return hats_by_id[worst]["lens"]


def passing_axes(scores: dict, hats_by_id: dict, failing: list) -> list:
    """Lenses that passed their threshold -- fed to the refine step's preservation lock so a targeted
    repair doesn't quietly regress an axis that was already fine."""
    return [hats_by_id[hat_id]["lens"] for hat_id in scores if hat_id not in failing]
