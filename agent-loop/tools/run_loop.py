#!/usr/bin/env python
"""Reference CLI that actually runs the agent-loop architecture end to end: Generate -> Evaluate ->
(pre-filter ->) (Diagnose -> Refine)* -> stop, against a real loop-config and a task brief.

Usage:
    python agent-loop/tools/run_loop.py \
        --loop-config agent-loop/loop-config.example.yaml \
        --task agent-loop/tasks/deployment-delay-email.yaml \
        --transcript-out transcript.json [--dry-run] [--verbose]

This is a reference implementation, at the same fidelity as tools/apply_skills.py elsewhere in this repo:
no durable execution engine, no state store surviving a process restart -- see
agent-loop/schemas/loop-config.schema.json's white_hat_archivist section for the contract a production
implementation would need to satisfy. Here, the full transcript (every draft, every score, every
diagnosis) is written to one JSON file when the loop stops.

--dry-run prints the Generate and Evaluate prompts for the first iteration and stops before any real API
call -- it cannot simulate scores that don't exist, so it can't demonstrate Refine; that requires a real
run with an API key.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools"))
import guardrails  # noqa: E402  (reused deliberately from the book-skills half of this repo)
import orchestrator  # noqa: E402


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_hats(hat_ids, agent_loop_root):
    return {hat_id: load_yaml(agent_loop_root / "hats" / f"{hat_id}.yaml") for hat_id in hat_ids}


def render_generate_prompt(task, hats_by_id, generate_hat_ids):
    personas = [hats_by_id[h]["generate_persona"] for h in generate_hat_ids]
    system_prompt = "\n\n".join(p["system_prompt"] for p in personas)
    directive = " ".join(p["directive"] for p in personas)
    output_schema = "; ".join(p.get("output_schema", "") for p in personas if p.get("output_schema"))
    user_prompt = (
        f"TASK: {task['task']}\n"
        f"AUDIENCE: {task.get('audience', 'general')}\n"
        f"MEDIUM: {task.get('medium', 'plain text')}\n"
        f"DIRECTIVE: {directive}\n"
    )
    if output_schema:
        user_prompt += f"STRUCTURED OUTPUT: {output_schema}\n"
    return system_prompt, user_prompt


def build_evaluate_tool(hat_ids):
    properties = {
        hat_id: {
            "type": "object",
            "required": ["score", "justification"],
            "properties": {
                "score": {"type": "integer", "minimum": 1, "maximum": 10},
                "justification": {"type": "string"},
            },
        }
        for hat_id in hat_ids
    }
    return {
        "name": "submit_scores",
        "description": "Submit a 1-10 score (10 always means this lens is fully satisfied) and a justification for each cognitive lens.",
        "input_schema": {"type": "object", "required": hat_ids, "properties": properties},
    }


def render_evaluate_system_prompt(hats_by_id, hat_ids):
    rubrics = []
    for hat_id in hat_ids:
        rubric = hats_by_id[hat_id]["evaluate_rubric"]
        anchors = rubric["scoring_anchors"]
        rubrics.append(
            f"--- {hat_id} ({hats_by_id[hat_id]['lens']}) ---\n{rubric['system_prompt']}\n"
            f"1 means: {anchors['1']}\n5 means: {anchors['5']}\n10 means: {anchors['10']}"
        )
    return (
        "You are scoring a draft across several independent cognitive lenses, submitted via the "
        "submit_scores tool. Score each lens strictly on its own dimension only -- every lens scores "
        "1-10 with 10 always meaning that lens is fully satisfied. Do not let a high score on one lens "
        "compensate for a low score on another; you are reporting facts about the draft, not negotiating "
        "an overall verdict.\n\n" + "\n\n".join(rubrics)
    )


def render_diagnose_prompt(task, draft, scores, failing, hats_by_id):
    failing_desc = "\n".join(
        f"- {hat_id} ({hats_by_id[hat_id]['lens']}): {scores[hat_id]['score']}/10 -- {scores[hat_id]['justification']}"
        for hat_id in failing
    )
    system_prompt = (
        "You are the Diagnostic step. You do NOT decide which axis gets repaired -- that has already "
        "been decided deterministically by the orchestrator's code, from the numeric scores alone. Your "
        "only job is to explain the root cause of the failure in the axis named below, concretely enough "
        "that a targeted rewrite can fix it without touching anything else."
    )
    user_prompt = (
        f"ORIGINAL TASK: {task['task']}\n"
        f"PREVIOUS DRAFT:\n{draft}\n\n"
        f"FAILING AXIS/AXES (the orchestrator has already chosen which one to repair from among these):\n{failing_desc}\n\n"
        "Explain the specific root cause of the failure. Quote the exact passage responsible."
    )
    return system_prompt, user_prompt


def render_refine_prompt(task, draft, root_cause, repair_hat, preserve_axes):
    strategy = repair_hat["refine_strategy"]
    preserve_note = (
        f"Preserve these already-passing axes exactly as they are -- do not reword or restructure "
        f"anything that serves them: {', '.join(preserve_axes)}."
        if preserve_axes else ""
    )
    user_prompt = (
        f"ORIGINAL TASK: {task['task']}\n"
        f"PREVIOUS DRAFT:\n{draft}\n\n"
        f"DIAGNOSIS: {root_cause}\n"
        f"{strategy['instruction']}\n"
        f"{preserve_note}"
    )
    return strategy["system_prompt"], user_prompt


def call(client, model, system, user, temperature=0.5, max_tokens=2048, tools=None, tool_choice=None):
    kwargs = dict(model=model, max_tokens=max_tokens, temperature=temperature,
                  system=system, messages=[{"role": "user", "content": user}])
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice
    return client.messages.create(**kwargs)


def run(args):
    agent_loop_root = Path(__file__).resolve().parent.parent
    loop_config = load_yaml(args.loop_config)
    task = load_yaml(args.task)

    hat_ids = loop_config["hats"]
    hats_by_id = load_hats(hat_ids, agent_loop_root)
    veto_hats = loop_config.get("veto_hats", [])
    model = args.model or "claude-sonnet-5"

    generate_hat_ids = task.get("generate_hats") or hat_ids[:1]
    generate_temp = hats_by_id[generate_hat_ids[0]]["generate_persona"].get("default_temperature", 0.5)

    transcript = {"task": task, "loop_config_id": loop_config["id"], "iterations": []}

    client = None
    if not args.dry_run:
        import anthropic
        client = anthropic.Anthropic(api_key=args.api_key)

    draft = None
    previous_aggregate = None
    status = "Generating"

    for iteration in range(1, loop_config["budget"]["max_iterations"] + 1):
        if draft is None:
            system_prompt, user_prompt = render_generate_prompt(task, hats_by_id, generate_hat_ids)
            if args.verbose or args.dry_run:
                print(f"=== [iter {iteration}] GENERATE :: system ===\n{system_prompt}\n", file=sys.stderr)
                print(f"=== [iter {iteration}] GENERATE :: user ===\n{user_prompt}\n", file=sys.stderr)
            if args.dry_run:
                eval_system = render_evaluate_system_prompt(hats_by_id, hat_ids)
                print(f"=== [iter {iteration}] EVALUATE :: system (would run after a real draft) ===\n{eval_system}\n", file=sys.stderr)
                print("[dry-run] stopping before any real API call -- Refine can't be previewed without real scores.", file=sys.stderr)
                return
            response = call(client, model, system_prompt, user_prompt, temperature=generate_temp)
            draft = response.content[0].text

        if loop_config["evaluation"].get("pre_filter_output_constraints") and task.get("output_constraints"):
            fake_skill = {"output_constraints": task["output_constraints"]}
            try:
                guardrails.check_output(fake_skill, draft, task.get("constraint_params", {}))
            except guardrails.GuardrailViolation as e:
                print(f"[iter {iteration}] pre-filter violation (no ensemble call spent): {e}", file=sys.stderr)
                transcript["iterations"].append(
                    {"iteration": iteration, "stage": "pre_filter_failed", "draft": draft, "error": str(e)}
                )
                status = "Failed"
                break

        eval_system = render_evaluate_system_prompt(hats_by_id, hat_ids)
        tool = build_evaluate_tool(hat_ids)
        response = call(client, model, eval_system, f"DRAFT TO SCORE:\n{draft}",
                         temperature=0.0, tools=[tool], tool_choice={"type": "tool", "name": "submit_scores"})
        tool_use_block = next(b for b in response.content if b.type == "tool_use")
        scores = tool_use_block.input

        failing = orchestrator.failing_hats(scores, hats_by_id)
        veto_hat = orchestrator.veto_triggered(scores, hats_by_id, veto_hats)
        aggregate = orchestrator.aggregate_score(scores, hats_by_id)

        record = {"iteration": iteration, "draft": draft, "scores": scores, "aggregate": aggregate}
        transcript["iterations"].append(record)

        if not failing:
            record["decision"] = "accept"
            status = "Completed"
            break

        if veto_hat:
            record["decision"] = f"veto:{veto_hat}"
            # Safety failures don't get a "good enough, stop trying" pass -- always proceed to repair.
        else:
            if previous_aggregate is not None:
                delta = aggregate - previous_aggregate
                if delta < loop_config["convergence"]["improvement_delta_threshold"]:
                    record["decision"] = "stalled"
                    status = "HumanReview"
                    break
            record["decision"] = "refine"
        previous_aggregate = aggregate

        if iteration >= loop_config["budget"]["max_iterations"]:
            record["decision"] = "budget_exhausted"
            status = loop_config["budget"].get("on_ceiling_reached", "return_best_so_far")
            break

        repair_lens = orchestrator.choose_repair_lens(failing, scores, hats_by_id, veto_hats)
        repair_hat_id = loop_config["strategy_map"][repair_lens]
        repair_hat = hats_by_id.get(repair_hat_id) or load_yaml(agent_loop_root / "hats" / f"{repair_hat_id}.yaml")

        diag_system, diag_user = render_diagnose_prompt(task, draft, scores, failing, hats_by_id)
        response = call(client, model, diag_system, diag_user, temperature=0.2)
        root_cause = response.content[0].text
        record["diagnosis"] = {"repair_lens": repair_lens, "repair_hat": repair_hat_id, "root_cause": root_cause}

        preserve_axes = orchestrator.passing_axes(scores, hats_by_id, failing)
        refine_system, refine_user = render_refine_prompt(task, draft, root_cause, repair_hat, preserve_axes)
        response = call(client, model, refine_system, refine_user,
                         temperature=repair_hat["refine_strategy"].get("default_temperature", 0.3))
        draft = response.content[0].text

    transcript["status"] = status
    transcript["final_draft"] = draft
    Path(args.transcript_out).write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    print(f"Wrote {args.transcript_out} (status: {status})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loop-config", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--transcript-out", default="transcript.json")
    parser.add_argument("--model", default=None, help="Defaults to claude-sonnet-5")
    parser.add_argument("--api-key", default=None, help="Defaults to ANTHROPIC_API_KEY env var")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
