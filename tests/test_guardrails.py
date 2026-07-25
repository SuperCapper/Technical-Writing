#!/usr/bin/env python
"""Exercises tools/guardrails.py and the parameter-coercion path in tools/apply_skills.py directly,
with synthetic skills/text -- no API key or network access required.

Run: python tests/test_guardrails.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import guardrails
from apply_skills import coerce_override, resolve_params


def check(label, condition):
    status = "ok" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    # --- max_words: within limit ---
    skill = {"parameters": {"word_limit": {"type": "integer", "default": 10}},
             "output_constraints": [{"type": "max_words", "param": "word_limit"}]}
    try:
        guardrails.check_output(skill, "one two three four five", {"word_limit": 10})
        results.append(check("max_words passes when under the limit", True))
    except guardrails.GuardrailViolation:
        results.append(check("max_words passes when under the limit", False))

    # --- max_words: over limit raises ---
    try:
        guardrails.check_output(skill, "one two three four five six seven eight nine ten eleven", {"word_limit": 10})
        results.append(check("max_words raises when over the limit", False))
    except guardrails.GuardrailViolation:
        results.append(check("max_words raises when over the limit", True))

    # --- max_words: no limit configured (param missing from params) is a no-op, not a crash ---
    try:
        guardrails.check_output(skill, "word " * 500, {})
        results.append(check("max_words no-ops when its param isn't set", True))
    except guardrails.GuardrailViolation:
        results.append(check("max_words no-ops when its param isn't set", False))

    # --- unknown constraint type raises, rather than silently passing ---
    bad_skill = {"output_constraints": [{"type": "not_a_real_validator", "param": "x"}]}
    try:
        guardrails.check_output(bad_skill, "anything", {"x": 1})
        results.append(check("unknown output_constraint type raises rather than silently passing", False))
    except guardrails.GuardrailViolation:
        results.append(check("unknown output_constraint type raises rather than silently passing", True))

    # --- CLI --param overrides coerce to the declared type ---
    results.append(check("integer override coerces from string", coerce_override("15", "integer") == 15))
    results.append(check("boolean override 'false' coerces to False", coerce_override("false", "boolean") is False))
    results.append(check("boolean override 'true' coerces to True", coerce_override("true", "boolean") is True))
    results.append(check("already-typed values pass through unchanged", coerce_override(15, "integer") == 15))

    # --- resolve_params applies coercion using the skill's own declared parameter types ---
    skill2 = {"parameters": {"word_limit": {"type": "integer", "default": 250},
                              "include_disclaimer": {"type": "boolean", "default": True}}}
    params = resolve_params(skill2, {"word_limit": "60", "include_disclaimer": "false"})
    results.append(check("resolve_params coerces word_limit to int 60", params["word_limit"] == 60))
    results.append(check("resolve_params coerces include_disclaimer to bool False", params["include_disclaimer"] is False))

    if not all(results):
        print(f"\n{results.count(False)} FAILURE(S)")
        return 1
    print(f"\nAll {len(results)} guardrail checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
