"""Deterministic, fail-fast output validators referenced by a skill.yaml's `output_constraints`.

These check the model's *actual* response after a real (non-dry-run) call -- the "hard guardrail" half of
"prompts are soft, architecture is hard." Keep every validator here objective and cheap to compute (string
length, counts, regex). Qualitative judgment calls (did the tone land right, was the argument well
supported) belong to the skill's own `checklist` for a human -- or a future Claude-as-judge pass -- to
assess; they don't belong in this module, which must stay fast and deterministic enough to run on every
invocation without adding a second, fallible LLM call to check the first one.
"""


class GuardrailViolation(Exception):
    """Raised when a skill's real output violates one of its declared output_constraints."""


def max_words(text: str, constraint: dict, params: dict) -> None:
    """Fails if `text` exceeds the word count named by constraint['param'] in `params`."""
    limit_param = constraint["param"]
    limit = params.get(limit_param)
    if limit is None:
        # The run didn't set this parameter (no default, no override) -- nothing to enforce.
        return
    word_count = len(text.split())
    if word_count > limit:
        raise GuardrailViolation(
            f"output is {word_count} words, exceeding the '{limit_param}' limit of {limit}"
        )


VALIDATORS = {
    "max_words": max_words,
}


def check_output(skill: dict, text: str, params: dict) -> None:
    """Runs every output_constraint declared on `skill` against `text` (the model's real response).

    Raises GuardrailViolation on the first constraint that fails. Callers should treat this as fatal:
    fail fast rather than silently pass a violating output on to whatever consumes it next.
    """
    for constraint in skill.get("output_constraints", []):
        constraint_type = constraint["type"]
        validator = VALIDATORS.get(constraint_type)
        if validator is None:
            raise GuardrailViolation(f"unknown output_constraint type: {constraint_type!r}")
        validator(text, constraint, params)
