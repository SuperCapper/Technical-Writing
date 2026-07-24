#!/usr/bin/env python
"""Validates every skills/*/skill.yaml against schemas/skill.schema.json,
and checks each skill against its own example (a skill's user_prompt_template
must render without error given its example's context, and every checklist
item must be a non-empty string).

Run: python -m tests.validate_skills   (or) python tests/validate_skills.py
"""
import glob
import json
import sys
from pathlib import Path

import yaml
import jsonschema
from jinja2 import Template

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    schema = json.loads((REPO_ROOT / "schemas" / "skill.schema.json").read_text(encoding="utf-8"))
    skill_files = sorted(glob.glob(str(REPO_ROOT / "skills" / "*" / "skill.yaml")))

    if not skill_files:
        print("No skill files found under skills/*/skill.yaml", file=sys.stderr)
        return 1

    failures = []
    seen_ids = set()

    for path in skill_files:
        rel = Path(path).relative_to(REPO_ROOT)
        data = load_yaml(path)

        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            failures.append(f"{rel}: schema error: {e.message}")
            continue

        if data["id"] in seen_ids:
            failures.append(f"{rel}: duplicate id {data['id']}")
        seen_ids.add(data["id"])

        for i, example in enumerate(data.get("examples", [])):
            params = {}
            for pname, pdef in data.get("parameters", {}).items():
                params[pname] = pdef.get("default")
            params.update(example.get("context", {}).get("parameters", {}))
            try:
                Template(data["user_prompt_template"]).render(document=example["input"], **params)
            except Exception as e:
                failures.append(f"{rel}: example[{i}] failed to render user_prompt_template: {e}")

        for i, item in enumerate(data.get("checklist", [])):
            if not isinstance(item, str) or not item.strip():
                failures.append(f"{rel}: checklist[{i}] is empty or not a string")

    print(f"Checked {len(skill_files)} skill files.")
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print(f" - {f}")
        return 1

    print("All skill files valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
