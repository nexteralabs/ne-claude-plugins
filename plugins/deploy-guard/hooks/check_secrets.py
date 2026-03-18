#!/usr/bin/env python3
"""
Pre-tool hook that scans file content for potential secrets before writing.
Runs on Edit/Write/MultiEdit tool uses.
"""

import json
import re
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

def check_for_secrets(content: str) -> list[str]:
    """Scan content for potential secrets."""
    findings = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, content):
            findings.append(label)
    return findings


def main():
    tool_input = json.loads(sys.stdin.read())
    content = tool_input.get("new_string", "") or tool_input.get("content", "")

    if not content:
        sys.exit(0)

    findings = check_for_secrets(content)
    if findings:
        types = ", ".join(set(findings))
        print(f"⚠️  deploy-guard: Potential secret detected ({types}). Review before proceeding.", file=sys.stderr)
        # Exit 2 = block the tool use
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
