# Autoresearch Skill — Brainstorm Notes

**Date:** 2026-03-21
**Source:** [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch) — MIT License
**Intent:** Fork, improve, and redistribute as part of ne-claude-plugins

---

## What the original does well

- Solid autonomous loop: baseline → mutate → score → keep/discard → repeat
- Binary evals only (no scales) — good principle, reduces noise
- One change at a time — clean causal attribution
- Live HTML dashboard with Chart.js
- Changelog as a research log artifact
- Worked example (diagram generator) is concrete and useful
- Inline credit to Karpathy's methodology

---

## Gaps identified in the original

### 1. Self-grading bias
The same agent that runs experiments also scores them. It has full context of what it was "trying" to achieve, which biases scoring toward keeping mutations. A separate grader subagent with no context of the current mutation would score more reliably. The codesmith/skill-creator plugin does this with a dedicated grader agent.

### 2. Invocation mechanics are implied, not specified
The skill says "run the skill N times" but never explains *how* — spawn a subagent with the skill path? Call `claude -p` in subprocess? This gap causes real-world failures since Claude has to improvise.

### 3. No parallel mutation testing
Strictly sequential: one mutation → N runs → score → decide. Running 2-3 candidate mutations simultaneously (separate subagents) would converge 2-3x faster.

### 4. No checkpoint/resume
If the loop gets interrupted (context limit, session dies), there's no way to pick back up. The artifacts exist (`results.tsv`, `changelog.md`) but the skill doesn't say how to resume from them.

### 5. Eval quality validation is missing
No step to check if evals actually discriminate before running 50 experiments. If 3 of 5 evals trivially pass 100% of the time, you're optimizing against noise. Skill-creator's `run_loop.py` splits train/test to catch overfitting — autoresearch doesn't.

### 6. Overlap with skill-creator
Both skill-creator and autoresearch optimize skills with evals. They share no infrastructure. The `run_loop.py` script in skill-creator might already do 80% of what autoresearch describes.

---

## Priorities for the fork

**High impact / practical:**
- Explicit invocation mechanics (how to actually run the target skill)
- Separate grader agent (accuracy of scoring)
- Checkpoint/resume support

**Higher effort / architectural:**
- Parallel mutation testing (speed)
- Eval discriminability check before starting the loop

---

## Attribution

Fork of [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch), MIT License.
Original concept based on Karpathy's autoresearch methodology.
