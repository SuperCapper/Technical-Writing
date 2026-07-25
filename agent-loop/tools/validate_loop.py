#!/usr/bin/env python
"""Validates agent-loop/hats/*.yaml against schemas/hat.schema.json and any agent-loop/*.yaml loop
config (e.g. loop-config.example.yaml) against schemas/loop-config.schema.json, then cross-checks
references between them: a loop's `hats` and `strategy_map` must point at hat ids that actually exist,
`veto_hats` must match what each referenced hat's own `veto` field declares, and every lens used by a
loop's hats should have a strategy_map entry so a failing axis always has somewhere to route to.

Run: python agent-loop/tools/validate_loop.py
"""
import glob
import json
import sys
from pathlib import Path

import yaml
import jsonschema

AGENT_LOOP_ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    hat_schema = json.loads((AGENT_LOOP_ROOT / "schemas" / "hat.schema.json").read_text(encoding="utf-8"))
    loop_schema = json.loads((AGENT_LOOP_ROOT / "schemas" / "loop-config.schema.json").read_text(encoding="utf-8"))

    failures = []

    hat_files = sorted(glob.glob(str(AGENT_LOOP_ROOT / "hats" / "*.yaml")))
    if not hat_files:
        print("No hat cards found under agent-loop/hats/*.yaml", file=sys.stderr)
        return 1

    hats_by_id = {}
    for path in hat_files:
        rel = Path(path).relative_to(AGENT_LOOP_ROOT.parent)
        data = load_yaml(path)
        try:
            jsonschema.validate(data, hat_schema)
        except jsonschema.ValidationError as e:
            failures.append(f"{rel}: schema error: {e.message}")
            continue
        if data["id"] in hats_by_id:
            failures.append(f"{rel}: duplicate hat id {data['id']}")
        hats_by_id[data["id"]] = data

    loop_files = sorted(glob.glob(str(AGENT_LOOP_ROOT / "*.yaml")))
    if not loop_files:
        print("No loop configs found under agent-loop/*.yaml", file=sys.stderr)
        return 1

    for path in loop_files:
        rel = Path(path).relative_to(AGENT_LOOP_ROOT.parent)
        data = load_yaml(path)
        try:
            jsonschema.validate(data, loop_schema)
        except jsonschema.ValidationError as e:
            failures.append(f"{rel}: schema error: {e.message}")
            continue

        loop_hats = data.get("hats", [])
        for hat_id in loop_hats:
            if hat_id not in hats_by_id:
                failures.append(f"{rel}: references undeclared hat id '{hat_id}' in `hats`")

        for veto_id in data.get("veto_hats", []):
            if veto_id not in hats_by_id:
                failures.append(f"{rel}: veto_hats references undeclared hat id '{veto_id}'")
            elif not hats_by_id[veto_id].get("veto", False):
                failures.append(
                    f"{rel}: veto_hats lists '{veto_id}' but that hat's own `veto` field is not true "
                    f"-- the loop-level list and the hat card have drifted out of sync"
                )
        for hat_id, hat in hats_by_id.items():
            if hat.get("veto", False) and hat_id in loop_hats and hat_id not in data.get("veto_hats", []):
                failures.append(
                    f"{rel}: hat '{hat_id}' declares veto: true but is not listed in this loop's veto_hats"
                )

        strategy_map = data.get("strategy_map", {})
        for hat_id in loop_hats:
            lens = hats_by_id.get(hat_id, {}).get("lens")
            if lens and lens not in strategy_map:
                failures.append(
                    f"{rel}: hat '{hat_id}' has lens '{lens}' but strategy_map has no entry for it "
                    f"-- a failure on this axis would have nowhere to route"
                )
        for lens, target_hat_id in strategy_map.items():
            if target_hat_id not in hats_by_id:
                failures.append(f"{rel}: strategy_map['{lens}'] references undeclared hat id '{target_hat_id}'")

    print(f"Checked {len(hat_files)} hat cards and {len(loop_files)} loop config(s).")
    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print(f" - {f}")
        return 1

    print("All hat cards and loop configs valid and cross-referenced correctly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
