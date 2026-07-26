# Running These Flows via Claude Code Chat in VS Code

This repo has three independent things you can run, and they use two different mechanisms:

1. **Genres** (`skills/07-14`) and **Workplace** (`skills/19-21`) both run through the same CLI,
   `tools/apply_skills.py` -- only the `--skill` path changes.
2. **Agent Loop** (`agent-loop/`) runs through a different CLI, `agent-loop/tools/run_loop.py`, against a
   task brief instead of a raw draft.

Everything below assumes you're talking to Claude Code's chat panel in VS Code, not typing commands into a
terminal yourself. You describe what you want in plain English; Claude Code runs the actual Python commands
on your behalf (using its own Bash access) and shows you the result in the chat. The first time it runs a
command in a session, VS Code will show a permission prompt asking you to approve it -- that's expected, not
an error.

## Quick reference

| I want to... | Say this in Claude Code chat |
|---|---|
| Draft/revise a document type (proposal, report, instructions, etc.) | *"Apply the genres.proposal skill to draft.md"* |
| Format or review a workplace communication (email, resume, team plan) | *"Apply the workplace.business-communication skill to my-email.txt"* |
| Run the six-hat self-correcting loop on a task | *"Dry-run the agent-loop against this task: ..."* |

Switching between all three is just switching which of these three sentences you say next -- Claude Code
already has the repo structure in context and doesn't need the mechanism re-explained each time.

## 0. One-time setup

- Open the repo folder in VS Code (`File > Open Folder... > Technical-Writing`).
- Open Claude Code's chat panel: either click its icon in the VS Code Activity Bar, or open the Command
  Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run **Claude Code: Open Chat** (exact wording may vary by
  extension version).
- **API key**, needed for every *real* (non-dry-run) call: set `ANTHROPIC_API_KEY` as an environment
  variable before launching VS Code (e.g. in your shell profile, or via your OS's environment variable
  settings), so Claude Code's Bash tool inherits it. You can check this is set by asking Claude Code:
  *"Is ANTHROPIC_API_KEY set in this environment?"*
- You do **not** need to activate the `.venv` or run `pip install` yourself -- ask Claude Code to do it the
  first time: *"Set up this repo's Python environment if it isn't already."*

## 1. Genres -- drafting/reviewing a document type

Available skills (see the top-level README's Genres table for the full list): `genres.instructions`,
`genres.proposal`, `genres.progress-report`, `genres.feasibility-recommendation-report`,
`genres.lab-project-report`, `genres.research-report`, `genres.a3-report`, `genres.abstract-summary`.

**Steps:**

1. Save your rough draft as a file anywhere in (or outside) the repo, e.g. `drafts/my-proposal.md`.
2. In Claude Code chat, name the skill and the file:
   > Using `tools/apply_skills.py` in this repo, dry-run the `genres.proposal` skill
   > (`skills/08-proposal/skill.yaml`) against `drafts/my-proposal.md` with `formality=informal`, and show
   > me the rendered prompt.
3. Review what Claude Code shows you -- this costs nothing, since `--dry-run` never calls the API.
4. When you're ready to actually generate a revision:
   > Now run that for real (drop --dry-run) and write the result to `drafts/my-proposal-revised.md`.
5. To try a **different** Genre skill on the same or another draft, just say which one next:
   > Now run `genres.progress-report` on the same file instead.

   That's the "easy toggle": you don't repeat the setup, just name the next skill.

Each skill has its own parameters (see its `skills/NN-slug/skill.yaml` or `README.md`) -- e.g.
`genres.abstract-summary` takes `output_kind` and `word_limit`. If you don't know a skill's parameters, ask:
*"What parameters does genres.abstract-summary take?"* and Claude Code will read the file and tell you.

## 2. Workplace -- communicating with people

Available skills: `workplace.business-communication`, `workplace.job-application-materials`,
`workplace.team-writing`. Mechanically identical to Genres above -- same CLI, different `--skill` path.

**Steps:**

1. Save your draft, e.g. `drafts/my-email.txt`.
2. In chat:
   > Dry-run the `workplace.business-communication` skill (`skills/19-business-communication/skill.yaml`)
   > against `drafts/my-email.txt` with `medium=email`.
3. Review, then run for real the same way as step 4 above.
4. To toggle to a different Workplace skill:
   > Now run `workplace.job-application-materials` with `document_kind=cover-letter` against
   > `drafts/my-cover-letter.md` instead.

**One thing to expect, not a bug:** `workplace.business-communication`'s whole point is that it sometimes
recommends *not* writing an email at all (see `docs/example-use-case.md`'s discussion of this). If Claude
Code tells you to make a phone call instead of sending a draft, that's the skill working correctly.

## 3. Agent Loop -- the self-correcting six-hat loop

This is a different CLI (`agent-loop/tools/run_loop.py`) against a **task brief**, not a raw draft. A task
brief is a small YAML file: what to write, the audience, the medium, which hats draft it, and (optionally)
a hard constraint like a word limit. See `agent-loop/tasks/deployment-delay-email.yaml` for a real example.

**Steps:**

1. Either reuse an existing task file, or describe a new one in plain English and let Claude Code write it:
   > Create an agent-loop task file at `agent-loop/tasks/my-task.yaml` for: an email telling a customer
   > their refund was denied. Audience: an upset customer. Medium: email. Use red and black as the
   > generate hats.
2. Dry-run it first (no API cost):
   > Dry-run `agent-loop/tools/run_loop.py` with `loop-config.example.yaml` against
   > `agent-loop/tasks/my-task.yaml`, and show me the Generate and Evaluate prompts.
3. Review what it shows you.
4. Run for real:
   > Now run that for real and write the transcript to `transcript.json`.
5. Don't read the raw JSON yourself -- ask for a summary:
   > Summarize `transcript.json`: how many iterations ran, which hat(s) failed and why, what got fixed,
   > and what the final status was.
6. To toggle to a **different loop configuration** (e.g. stricter safety, or a different set of
   participating hats), describe the change and let Claude Code create a variant rather than hand-editing
   YAML yourself:
   > Make a copy of `loop-config.example.yaml` called `loop-config-strict.yaml` with black's
   > `pass_threshold` raised to 9, and rerun the same task against it.

See `agent-loop/README.md` for what each of the six hats actually checks, and
`agent-loop/docs/foundations-elements-style-merge.md` for which book chapters four of them already draw on.

## Fewer permission prompts

If VS Code asking to approve each Bash command gets tedious, ask Claude Code to reduce that:

> Use the fewer-permission-prompts skill to allow the read-only commands this repo's tools commonly need.

This still won't silently approve things like overwriting a file or calling a paid API without asking first
by default -- it just stops re-prompting for the same safe, repeated read-only commands.
