# skillforge

Autonomous skill optimizer for Claude Code. Point it at any skill, define what "good output" looks like as binary checks, and it runs an experiment loop — mutating the prompt, scoring every output, and keeping only improvements.

Fits the codesmith family: codesmith builds code, skillforge sharpens the tools.

## How it works

Say "run skillforge on my X skill" or "this skill is flaky, let's optimize it". SkillForge:

1. Reads the target skill and understands what it does
2. Confirms test inputs and eval criteria with you
3. Establishes a baseline score using parallel runner agents + blind grader agents
4. Checks eval discriminability — flags evals that trivially pass or fail 100% of the time
5. Runs an autonomous mutation loop: one targeted change at a time, scored by blind graders
6. Keeps mutations that improve the score, discards the rest
7. Prints a terminal summary — then asks if you want to merge the result into the original skill and clean up

## Agents

| Agent | Job |
|-------|-----|
| **runner** | Executes the target skill on a test input. Returns only the skill output — no meta-commentary. Spawned N at a time in parallel. |
| **grader** | Scores a skill output against binary eval criteria. Never told what mutation was attempted. Strict: if unsure, FAIL. |

## Improvements over upstream

SkillForge fixes five structural gaps in the original autoresearch methodology:

| Gap | Fix |
|-----|-----|
| Self-grading bias | Separate blind grader agent — no mutation context |
| Unclear invocation | Explicit runner agent — N parallel spawns per experiment |
| No checkpoint/resume | Detects existing `skillforge-[name]/` artifacts, offers to resume |
| Sequential only | Parallel candidate mutations when 2-3 hypotheses exist |
| No eval validation | Discriminability check after baseline — flags degenerate evals |

## Outputs

All artifacts land in `skillforge-[skill-name]/` in the current working directory:

```
skillforge-[skill-name]/
├── [user-chosen-name].md  # the improved skill
├── SKILL.md.baseline      # original skill before optimization
├── run-config.json        # run metadata (enables checkpoint/resume)
├── evals.md               # saved eval definitions (enables checkpoint/resume)
├── results.tsv            # score log for every experiment
└── changelog.md           # detailed mutation log — the research record
```

The original SKILL.md is never modified unless you explicitly approve the merge at the end.

## Trigger phrases

> optimize this skill, improve this skill, run skillforge on, make this skill better, benchmark skill, eval my skill, run evals on, skill is flaky, skill needs work, tune this skill, sharpen this skill, skill keeps failing, make X skill smarter

## Installation

```
/plugin install skillforge@ne-claude-plugins
```

## License

MIT — fork of [uditgoenka/autoresearch](https://github.com/uditgoenka/autoresearch).
Original concept based on Karpathy's autoresearch methodology.
