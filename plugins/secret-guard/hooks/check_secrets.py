#!/usr/bin/env python3
"""
Pre-tool hook that scans what a git commit would hold for potential secrets.
Only runs on commands containing a git commit — exits immediately for anything else.

Exit 2 blocks the command and shows stderr to Claude; any other non-zero exit
would let the command run, so every failure here exits 2.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}', "API key"),
    (r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*["\']?[^\s"\']{8,}', "Secret/password"),
    (r'(?i)(token)\s*[:=]\s*["\']?[A-Za-z0-9_\-\.]{20,}', "Token"),
    (r'(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key"),
    (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]', "AWS credential"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub PAT"),
    (r'sk-[A-Za-z0-9]{48}', "OpenAI/Anthropic key"),
    (r'xoxb-[0-9]{10,}-[A-Za-z0-9]+', "Slack bot token"),
]

HATCH = "ALLOW_SECRET=1"
# A command starts the line or follows ; & | ( — env assignments may precede git.
COMMAND_START = r"(?:^|[;&|(]|\n)\s*(?P<env>(?:[A-Za-z_]\w*=\S*\s+)*)git\s+(?:-[Cc]\s+\S+\s+)*"
GIT_COMMIT = re.compile(COMMAND_START + r"commit\b(?P<args>[^;&|\n]*)")
GIT_ADD = re.compile(COMMAND_START + r"add\b")
COMMIT_ALL = re.compile(r"(?:^|\s)(?:--all|-[A-Za-z]*a[A-Za-z]*)(?=\s|$)")
MAX_UNTRACKED_BYTES = 1_000_000


def git(cwd: str | None, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).stdout


def added_lines(diff: str) -> list[tuple[str, str]]:
    """(path, line) for each line a diff adds: a removed secret is not a leak."""
    lines = []
    path = ""
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+"):
            lines.append((path, line[1:]))
    return lines


def untracked_lines(cwd: str | None) -> list[tuple[str, str]]:
    lines = []
    root = git(cwd, "rev-parse", "--show-toplevel").strip()
    for name in git(cwd, "ls-files", "--others", "--exclude-standard", "--full-name").splitlines():
        file = Path(root) / name
        if not file.is_file() or file.stat().st_size > MAX_UNTRACKED_BYTES:
            continue
        content = file.read_bytes()
        if b"\0" in content:
            continue
        lines += [(name, line) for line in content.decode(errors="replace").splitlines()]
    return lines


def committed_lines(command: str, commit: re.Match, cwd: str | None) -> list[tuple[str, str]]:
    """What the commit would hold, including what a `git add` or `-a` on the line stages first.

    A `git add` is assumed to stage every change: scanning too much beats missing a key.
    """
    lines = added_lines(git(cwd, "diff", "--cached", "-U0", "--diff-filter=ACMR"))
    adds_first = GIT_ADD.search(command[: commit.start() + 1]) is not None
    if adds_first or COMMIT_ALL.search(commit.group("args")):
        lines += added_lines(git(cwd, "diff", "-U0", "--diff-filter=ACMR"))
    if adds_first:
        lines += untracked_lines(cwd)
    return lines


def check_for_secrets(lines: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Secret types found, by file."""
    findings: dict[str, set[str]] = {}
    for path, line in lines:
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.setdefault(path, set()).add(label)
    return findings


def block(message: str) -> int:
    print(f"secret-guard: {message}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        command = payload["tool_input"].get("command", "")
        cwd = payload.get("cwd")
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        return block(f"the hook payload could not be read ({error}), so this command was not checked.")

    commit = GIT_COMMIT.search(command)
    if commit is None or HATCH in commit.group("env").split():
        return 0

    try:
        findings = check_for_secrets(committed_lines(command, commit, cwd))
    except Exception as error:
        return block(
            f"the scan crashed ({type(error).__name__}: {error}), so this commit was not checked. "
            f"To commit anyway: {HATCH} git commit ..."
        )
    if not findings:
        return 0

    details = "\n".join(f"  {path}: {', '.join(sorted(labels))}" for path, labels in sorted(findings.items()))
    return block(
        f"potential secrets in what this commit would hold:\n{details}\n"
        "Move them to an ignored file (.env) or a secret manager. If it is a false positive "
        f"(a test fixture, a placeholder), say so and commit with: {HATCH} git commit ..."
    )


if __name__ == "__main__":
    sys.exit(main())
