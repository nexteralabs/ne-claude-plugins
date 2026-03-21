#!/usr/bin/env python3
"""
Pre-tool hook that scans staged files for potential secrets before committing.
Only runs on git commit commands — exits immediately for anything else.
"""

import json
import re
import subprocess
import sys

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


def is_git_commit(command: str) -> bool:
    """Check if the command is a git commit."""
    return bool(re.match(r'^\s*git\s+commit\b', command))


def get_staged_diff() -> str:
    """Get the staged diff content."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--diff-filter=ACMR"],
        capture_output=True, text=True
    )
    return result.stdout


def check_for_secrets(content: str) -> list[str]:
    """Scan content for potential secrets."""
    findings = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, content):
            findings.append(label)
    return findings


def main():
    tool_input = json.loads(sys.stdin.read())
    command = tool_input.get("command", "")

    if not is_git_commit(command):
        sys.exit(0)

    diff = get_staged_diff()
    if not diff:
        sys.exit(0)

    findings = check_for_secrets(diff)
    if findings:
        types = ", ".join(set(findings))
        print(f"⚠️  secret-guard: Potential secret detected in staged files ({types}). Review before committing.", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
