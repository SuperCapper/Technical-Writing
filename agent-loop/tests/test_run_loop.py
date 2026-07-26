#!/usr/bin/env python
"""Exercises agent-loop/tools/run_loop.py's prompt-building functions against the real hat cards and task
files, and its pre-filter wiring to tools/guardrails.py -- the parts of run_loop.py that don't require a
real API call. The Evaluate/Diagnose/Refine API round-trip itself is not covered here; see
agent-loop/README.md for why (--dry-run stops before any real call, by design).

Run: python agent-loop/tests/test_run_loop.py
"""
import sys
from pathlib import Path

AGENT_LOOP_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT_LOOP_ROOT / "tools"))
sys.path.insert(0, str(AGENT_LOOP_ROOT.parent / "tools"))

import run_loop
import guardrails


def check(label, condition):
    status = "ok" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    loop_config = run_loop.load_yaml(AGENT_LOOP_ROOT / "loop-config.example.yaml")
    hats_by_id = run_loop.load_hats(loop_config["hats"], AGENT_LOOP_ROOT)

    task_no_constraints = run_loop.load_yaml(AGENT_LOOP_ROOT / "tasks" / "deployment-delay-email.yaml")
    task_with_constraints = run_loop.load_yaml(AGENT_LOOP_ROOT / "tasks" / "short-status-update.yaml")

    # --- render_generate_prompt renders for both example tasks ---
    for name, task in [("deployment-delay-email", task_no_constraints), ("short-status-update", task_with_constraints)]:
        generate_hat_ids = task.get("generate_hats") or loop_config["hats"][:1]
        try:
            system, user = run_loop.render_generate_prompt(task, hats_by_id, generate_hat_ids)
            results.append(check(f"render_generate_prompt renders for {name}", bool(system) and task["task"] in user))
        except Exception as e:
            results.append(check(f"render_generate_prompt renders for {name}: {e}", False))

    # --- render_evaluate_system_prompt + build_evaluate_tool cover every hat in the loop ---
    hat_ids = loop_config["hats"]
    eval_system = run_loop.render_evaluate_system_prompt(hats_by_id, hat_ids)
    results.append(check("render_evaluate_system_prompt mentions every hat id", all(h in eval_system for h in hat_ids)))
    tool = run_loop.build_evaluate_tool(hat_ids)
    results.append(check("build_evaluate_tool requires every hat id", set(tool["input_schema"]["required"]) == set(hat_ids)))

    # --- render_diagnose_prompt and render_refine_prompt render with synthetic scores ---
    synthetic_scores = {h: {"score": 5, "justification": "synthetic"} for h in hat_ids}
    synthetic_scores["black"] = {"score": 3, "justification": "deceptive claim"}
    failing = ["black"]
    try:
        diag_system, diag_user = run_loop.render_diagnose_prompt(
            task_no_constraints, "a draft", synthetic_scores, failing, hats_by_id
        )
        results.append(check("render_diagnose_prompt renders and includes the failing hat", "black" in diag_user))
    except Exception as e:
        results.append(check(f"render_diagnose_prompt renders: {e}", False))

    repair_hat = hats_by_id["black"]
    try:
        refine_system, refine_user = run_loop.render_refine_prompt(
            task_no_constraints, "a draft", "root cause text", repair_hat, ["facts", "value"]
        )
        results.append(check("render_refine_prompt includes the preservation note", "facts" in refine_user and "value" in refine_user))
    except Exception as e:
        results.append(check(f"render_refine_prompt renders: {e}", False))

    # --- pre-filter wiring: a task's own output_constraints actually reach guardrails.check_output ---
    fake_skill = {"output_constraints": task_with_constraints["output_constraints"]}
    params = task_with_constraints["constraint_params"]
    over_limit_draft = "word " * 100  # word_limit is 40
    try:
        guardrails.check_output(fake_skill, over_limit_draft, params)
        results.append(check("pre-filter wiring: over-limit draft raises GuardrailViolation", False))
    except guardrails.GuardrailViolation:
        results.append(check("pre-filter wiring: over-limit draft raises GuardrailViolation", True))

    under_limit_draft = "word " * 10
    try:
        guardrails.check_output(fake_skill, under_limit_draft, params)
        results.append(check("pre-filter wiring: under-limit draft passes", True))
    except guardrails.GuardrailViolation:
        results.append(check("pre-filter wiring: under-limit draft passes", False))

    if not all(results):
        print(f"\n{results.count(False)} FAILURE(S)")
        return 1
    print(f"\nAll {len(results)} run_loop checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
