#!/usr/bin/env python
"""Reference CLI for applying Technical-Writing skills to a document via the Claude API.

Usage:
    python tools/apply_skills.py --skill skills/07-instructions/skill.yaml \
        --input draft.md --output revised.md [--param key=value ...]

    python tools/apply_skills.py --pipeline composables/some-pipeline.yaml \
        --input draft.md --output revised.md
"""
import argparse
import sys
from pathlib import Path

import yaml
from jinja2 import Template

import guardrails


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def default_params(skill: dict) -> dict:
    return {k: v.get("default") for k, v in skill.get("parameters", {}).items()}


def coerce_override(value, param_type: str):
    """CLI --param overrides always arrive as strings; pipeline-declared parameters (from YAML) already
    have the right type. Only coerce actual strings, and only per the parameter's declared type, so a
    boolean override like `include_disclaimer=false` doesn't survive as the truthy string "false"."""
    if not isinstance(value, str):
        return value
    if param_type == "integer":
        return int(value)
    if param_type == "boolean":
        return value.strip().lower() in ("1", "true", "yes")
    return value


def resolve_params(skill: dict, overrides: dict) -> dict:
    params = default_params(skill)
    param_defs = skill.get("parameters", {})
    for key, value in overrides.items():
        param_type = param_defs.get(key, {}).get("type", "string")
        params[key] = coerce_override(value, param_type)
    return params


def render_prompt(skill: dict, document: str, params: dict) -> str:
    return Template(skill["user_prompt_template"]).render(document=document, **params)


def apply_skill(skill: dict, document: str, overrides: dict, api_key: str, dry_run: bool, verbose: bool) -> str:
    params = resolve_params(skill, overrides)
    user_prompt = render_prompt(skill, document, params)

    if verbose:
        print(f"[{skill['id']}] input length: {len(document)} chars", file=sys.stderr)
        print(f"[{skill['id']}] rendered prompt length: {len(user_prompt)} chars", file=sys.stderr)

    if dry_run:
        print(f"=== {skill['id']} :: system_prompt ===", file=sys.stderr)
        print(skill["system_prompt"], file=sys.stderr)
        print(f"=== {skill['id']} :: user_prompt ===", file=sys.stderr)
        print(user_prompt, file=sys.stderr)
        if verbose and skill.get("output_constraints"):
            print(f"[{skill['id']}] output_constraints skipped: no real output in --dry-run", file=sys.stderr)
        return document

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=skill.get("model", "claude-sonnet-5"),
        max_tokens=skill.get("max_tokens", 4096),
        system=skill["system_prompt"],
        messages=[{"role": "user", "content": user_prompt}],
    )
    result = response.content[0].text

    try:
        guardrails.check_output(skill, result, params)
    except guardrails.GuardrailViolation as e:
        print(f"[{skill['id']}] GUARDRAIL VIOLATION: {e}", file=sys.stderr)
        sys.exit(1)

    return result


def parse_param_overrides(pairs: list[str]) -> dict:
    overrides = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        overrides[key] = value
    return overrides


def run_single(args):
    skill = load_yaml(args.skill)
    document = Path(args.input).read_text(encoding="utf-8")
    overrides = parse_param_overrides(args.param)
    result = apply_skill(skill, document, overrides, args.api_key, args.dry_run, args.verbose)
    Path(args.output).write_text(result, encoding="utf-8")
    print(f"Wrote {args.output}")


def run_pipeline(args):
    pipeline = load_yaml(args.pipeline)
    document = Path(args.input).read_text(encoding="utf-8")
    for step in pipeline["steps"]:
        skill_path = Path("skills") / (step["skill_id"].split(".", 1)[1]) / "skill.yaml"
        # Fall back to scanning skills/ for the matching id if the naming convention differs.
        if not skill_path.exists():
            skill_path = next(
                p for p in Path("skills").glob("*/skill.yaml")
                if load_yaml(str(p))["id"] == step["skill_id"]
            )
        skill = load_yaml(str(skill_path))
        document = apply_skill(skill, document, step.get("parameters", {}), args.api_key, args.dry_run, args.verbose)
    Path(args.output).write_text(document, encoding="utf-8")
    print(f"Wrote {args.output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--skill", help="Path to a single skill.yaml to apply")
    group.add_argument("--pipeline", help="Path to a composable pipeline yaml (ordered list of skill_id steps)")
    parser.add_argument("--input", required=True, help="Path to the input document")
    parser.add_argument("--output", required=True, help="Path to write the transformed document")
    parser.add_argument("--param", action="append", default=[], help="Override a skill parameter, e.g. --param strictness=strict")
    parser.add_argument("--api-key", default=None, help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts instead of calling the API")
    parser.add_argument("--verbose", action="store_true", help="Log input/prompt sizes to stderr")
    args = parser.parse_args()

    if args.skill:
        run_single(args)
    else:
        run_pipeline(args)


if __name__ == "__main__":
    main()
