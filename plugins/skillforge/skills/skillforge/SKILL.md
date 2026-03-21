---
name: skillforge
description: "Autonomously optimize any Claude Code skill through a scored mutation loop. Triggers when the user wants to improve, benchmark, tune, or evaluate a skill's output quality. Use when: optimize this skill, improve this skill, run skillforge on, make this skill better, benchmark skill, eval my skill, run evals on, skill is flaky, skill needs work, tune this skill, sharpen this skill, skill keeps failing, make X skill smarter. Outputs: an improved SKILL.md, a terminal progress report, a results log, and a changelog of every mutation tried."
version: 1.0.0
---

# SkillForge

Most skills work about 70% of the time. The other 30% you get garbage. The fix isn't to rewrite the skill from scratch — it's to let an agent run it dozens of times, score every output, and tighten the prompt until that 30% disappears.

SkillForge adapts Andrej Karpathy's autoresearch methodology to Claude Code skills. Instead of optimizing ML training code, it optimizes skill prompts through an autonomous experimentation loop with parallel execution and blind scoring.

---

## before starting: gather context

**STOP. Do not run any experiments until all fields below are confirmed with the user. Ask for any missing fields before proceeding.**

1. **Target skill** — Which skill do you want to optimize? (need the exact path to SKILL.md)
2. **Test inputs** — What 3-5 different prompts/scenarios should we test the skill with? (variety matters — pick inputs that cover different use cases so we don't overfit to one scenario)
3. **Eval criteria** — What 3-6 binary yes/no checks define a good output? (see [references/eval-guide.md](references/eval-guide.md) for how to write good evals)
4. **Runs per experiment** — How many times to run the skill per mutation? Default: 5. (more runs = more reliable scores, but slower and more expensive)
5. **Budget cap** — Optional. Max number of experiment cycles before stopping. Default: no cap.

---

## how to run the skill

"Running the skill" means spawning **runner agents** — one per run, all in parallel.

Each runner agent receives:
- The full SKILL.md content as context
- One test input (the prompt to execute the skill on)

The runner executes the skill faithfully and returns only its output.

**Input cycling:** If you have 3 test inputs and N=5 runs, run each input once (3 runs), then cycle from the top (2 more runs using inputs 1 and 2). This ensures all inputs are covered while hitting the run count.

**Scoring:** After collecting all N outputs, spawn N **grader agents** in parallel. Each grader receives:
- One skill output
- The full eval criteria (pass/fail definitions)
- NO information about what mutation was attempted

**Aggregating scores:** Each grader returns a `TOTAL: X / Y` line. Read the `X` value from each grader response and sum across all N graders. That sum is the experiment score.

---

## step 1: read the skill

Before changing anything, read and understand the target skill completely.

1. Read the full SKILL.md file
2. Read any files in `references/` that the skill links to
3. Identify the skill's core job, process steps, and output format
4. Note any existing quality checks or anti-patterns already in the skill

Do NOT skip this. You need to understand what the skill does before you can improve it.

---

## step 2: build the eval suite

Convert the user's eval criteria into a structured test. Every check must be binary — pass or fail, no scales.

**Format each eval as:**

```
EVAL [number]: [Short name]
Question: [Yes/no question about the output]
Pass condition: [What "yes" looks like — be specific]
Fail condition: [What triggers a "no"]
```

**Rules for good evals:**
- Binary only. Yes or no. No "rate 1-7" scales.
- Specific enough to be consistent across different grader agents.
- Not so narrow that the skill games the eval.
- 3-6 evals is the sweet spot.

See [references/eval-guide.md](references/eval-guide.md) for detailed examples.

**Max score calculation:**
```
max_score = [number of evals] × [runs per experiment]
```

**Save the eval suite** to `skillforge-[skill-name]/evals.md` in the current working directory. This enables checkpoint/resume.

---

## step 3: checkpoint/resume check

Before establishing the baseline, check if a previous run exists.

Look for `skillforge-[skill-name]/evals.md` in the current working directory. If it exists:

1. Read `run-config.json` to get the `name` field — this is `[user-chosen-name]`
2. Read `results.tsv` — find the last row to get the current experiment number and best score
3. Read `changelog.md` — understand what mutations were tried
4. Read `[user-chosen-name].md` — this is already the best version so far

Present to the user:
> "Found an existing SkillForge run — [N] experiments completed, best score [X]%. Resume from experiment [N+1], or start fresh?"

- **Resume**: skip baseline, jump straight to the experiment loop with recovered state
- **Fresh start**: delete the existing working directory and proceed normally

If no `evals.md` exists, proceed to establish baseline.

---

## step 4: establish baseline

Run the skill AS-IS before changing anything. This is experiment #0.

1. **Ask the user what to name the new version.** Example: "What should I call the optimized version? (e.g., my-skill-v2, my-skill-optimized)"
2. Create working directory: `skillforge-[skill-name]/` in the current working directory
3. **Copy the original SKILL.md into the working directory as `[user-chosen-name].md`** — this is the copy you will mutate. NEVER edit the original SKILL.md.
4. Save `SKILL.md.baseline` in the working directory (revert target)
5. Save `run-config.json` with `{"name": "[user-chosen-name]"}` — required for checkpoint/resume
6. Create `results.tsv` with the header row
7. Run the skill N times using the runner + grader pipeline (as described in "how to run the skill")
8. Record the baseline score in results.tsv
9. Print the baseline result using the terminal progress format

**results.tsv format (tab-separated):**

```
experiment	score	max_score	pass_rate	status	description
0	14	20	70.0%	baseline	original skill — no changes
```

**After baseline, confirm the score with the user.** If baseline is already 90%+, the skill may not need optimization — ask if they want to continue.

---

## step 4b: eval discriminability check

After establishing baseline, check if each eval actually discriminates.

For each eval, look at its pass rate across the N baseline runs:

| Pass rate | Signal | Action |
|-----------|--------|--------|
| 100% always passes | Eval may not discriminate | Warn the user |
| 0% always fails | Eval may be too strict or broken | Warn the user |
| Between 20–80% | Good discrimination | Proceed |

If any evals are degenerate, surface them:
> "EVAL 2 (Pastel colors) passed 5/5 baseline runs — it may not discriminate. Keep it or replace it?"

This is a non-blocking gate — if the user keeps the eval, proceed. The check just prevents wasting 50 experiments against a broken signal.

---

## step 5: run the experiment loop

This is the core SkillForge loop. Once started, run autonomously until stopped.

**LOOP:**

1. **Analyze failures.** Look at which evals fail most. Read the actual outputs that failed. Identify the pattern.

2. **Form hypotheses.** You have two modes:

   **Single hypothesis** (default): Pick ONE thing to change. Don't change 5 things at once.

   **Parallel candidates** (when you have 2-3 distinct hypotheses for the same failure): Generate all candidates simultaneously:
   - Create `candidate-A.md`, `candidate-B.md` (up to `candidate-C.md`) in the working directory
   - Run the full runner + grader pipeline for each candidate in parallel
   - Compare scores — keep the best one if it beats the current best score (the last kept experiment's score), discard the rest
   - Delete candidate files after comparison
   - Cap at 3 candidates — more than that means unfocused hypotheses

   **Good mutations:**
   - Add a specific instruction that addresses the most common failure
   - Reword an ambiguous instruction to be more explicit
   - Add an anti-pattern ("Do NOT do X") for a recurring mistake
   - Move a buried instruction higher in the skill (priority = position)
   - Add or improve an example showing the correct behavior
   - Remove an instruction causing over-optimization

   **Bad mutations:**
   - Rewriting the entire skill from scratch
   - Adding 10 new rules at once
   - Making the skill longer without a specific reason
   - Vague instructions like "make it better"

3. **Make the change.** Edit `[user-chosen-name].md` (or candidate files) with the targeted mutation. NEVER touch the original SKILL.md.

4. **Run the experiment.** Execute the runner + grader pipeline N times.

5. **Decide: keep or discard.**
   - Score improved → **KEEP.** This is the new best score.
   - Score unchanged → **DISCARD.** Revert to previous version. Complexity without improvement.
   - Score worse → **DISCARD.** Revert.

6. **Log the result** in results.tsv and print to terminal.

7. **Repeat.** Go back to step 1.

**NEVER STOP.** Run autonomously until:
- The user manually stops you
- You hit the budget cap
- You hit 95%+ pass rate for 3 consecutive experiments (diminishing returns)

**If you run out of ideas:** Re-read failing outputs. Try combining two previous near-miss mutations. Try removing things instead of adding them. Simplification that maintains the score is a win.

---

## step 6: write the changelog

After each experiment, append to `changelog.md`:

```markdown
## Experiment [N] — [keep/discard]

**Score:** [X]/[max] ([percent]%)
**Change:** [One sentence describing what was changed]
**Reasoning:** [Why this change was expected to help]
**Result:** [Which evals improved/declined]
**Failing outputs:** [Brief description of what still fails, if anything]
```

This changelog is the most valuable artifact. A future agent (or smarter future model) can pick it up and continue from where you left off.

---

## step 7: deliver results

When the user returns or the loop stops, print the terminal summary, then ask about merging.

**Terminal summary format:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SkillForge — [skill-name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline:    14/20 (70%)
Best:        18/20 (90%)  ↑ +20%
Experiments: 4 total (2 kept, 2 discarded)

Eval breakdown:
  EVAL 1 (Text legibility):  9/10 pass
  EVAL 2 (Pastel colors):   10/10 pass
  EVAL 3 (No numbering):     9/10 pass
  EVAL 4 (Linear layout):    8/10 pass

Top changes:
  [Exp 1] added explicit instruction to avoid numbering
  [Exp 3] replaced "pastel" with specific hex codes

Remaining failures:
  Complex diagrams occasionally get overlapping labels (1/10 fail rate)

Improved skill: skillforge-[skill-name]/[user-chosen-name].md
Log:           skillforge-[skill-name]/results.tsv
Changelog:     skillforge-[skill-name]/changelog.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Print inline after each experiment during the run:

```
[Exp 0] BASELINE   14/20 (70%) — original skill — no changes
[Exp 1] KEEP       16/20 (80%) — added explicit instruction to avoid numbering
[Exp 2] DISCARD    16/20 (80%) — tried enforcing left-to-right layout — no change
[Exp 3] KEEP       18/20 (90%) — replaced "pastel" with specific hex codes
```

**After printing the summary, ask the user:**

> "Want me to merge the optimized skill into the original SKILL.md and clean up the `skillforge-[skill-name]/` directory?"

- **Yes** — overwrite the original SKILL.md with `[user-chosen-name].md`, then delete the `skillforge-[skill-name]/` directory
- **No** — leave everything as-is. Remind them the improved file is at `skillforge-[skill-name]/[user-chosen-name].md`

---

## output artifacts

All files land in `skillforge-[skill-name]/` in the current working directory:

```
skillforge-[skill-name]/
├── [user-chosen-name].md  # the improved skill (NEVER overwrite original without user approval)
├── SKILL.md.baseline      # original skill before optimization
├── run-config.json        # run metadata (enables checkpoint/resume)
├── evals.md               # saved eval definitions (enables checkpoint/resume)
├── results.tsv            # score log for every experiment
└── changelog.md           # detailed mutation log — the research record
```

**The original SKILL.md is NEVER modified** unless the user explicitly approves the merge in step 7.

---

## the test

A good SkillForge run:

1. **Started with a baseline** — never changed anything before measuring the starting point
2. **Used binary evals only** — no scales, no vibes
3. **Changed one thing at a time** — (or compared parallel candidates cleanly)
4. **Kept a complete log** — every experiment recorded, kept or discarded
5. **Improved the score** — measurable improvement from baseline to final
6. **Didn't overfit** — the skill got better at the actual job, not just at passing the specific test inputs
7. **Ran autonomously** — didn't stop to ask permission between experiments

If the skill "passes" all evals but actual output quality hasn't improved — the evals are bad, not the skill. Go back to step 2 and write better evals.

---

## attribution

Fork of [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch), MIT License.
Original concept based on Karpathy's autoresearch methodology.
