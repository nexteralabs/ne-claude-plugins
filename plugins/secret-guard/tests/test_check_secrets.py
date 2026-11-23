"""Runs the hook the way Claude Code does: a JSON payload on stdin, in a git repo.

python3 -m unittest discover -s plugins/secret-guard/tests
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "check_secrets.py"
FAKE_KEY = 'api_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"\n'


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


class CheckSecretsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "test")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_hook(self, command: str | None = None, raw: str | None = None) -> subprocess.CompletedProcess:
        payload = raw if raw is not None else json.dumps(
            {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(self.repo)}
        )
        return subprocess.run(
            [sys.executable, str(HOOK)], input=payload, cwd=self.repo, capture_output=True, text=True
        )

    def write(self, name: str, content: str) -> None:
        (self.repo / name).write_text(content)

    def test_blocks_a_staged_secret_with_the_payload_claude_code_sends(self) -> None:
        self.write("config.py", FAKE_KEY)
        git(self.repo, "add", "config.py")
        result = self.run_hook('git commit -m "feat: config"')
        self.assertEqual(result.returncode, 2)
        self.assertIn("config.py", result.stderr)

    def test_blocks_a_secret_added_on_the_same_line_as_the_commit(self) -> None:
        self.write("config.py", FAKE_KEY)
        result = self.run_hook('git add . && git commit -m "feat: config"')
        self.assertEqual(result.returncode, 2)

    def test_blocks_a_commit_all_of_a_tracked_file(self) -> None:
        self.write("config.py", "debug = True\n")
        git(self.repo, "add", "config.py")
        git(self.repo, "commit", "-q", "-m", "init")
        self.write("config.py", FAKE_KEY)
        result = self.run_hook('git commit -am "feat: config"')
        self.assertEqual(result.returncode, 2)

    def test_blocks_a_commit_after_another_command(self) -> None:
        self.write("config.py", FAKE_KEY)
        git(self.repo, "add", "config.py")
        result = self.run_hook(f'cd {self.repo} && git commit -m "feat: config"')
        self.assertEqual(result.returncode, 2)

    def test_lets_a_clean_commit_through(self) -> None:
        self.write("config.py", "debug = True\n")
        git(self.repo, "add", "config.py")
        self.assertEqual(self.run_hook('git commit -m "feat: config"').returncode, 0)

    def test_lets_the_removal_of_a_secret_through(self) -> None:
        self.write("config.py", FAKE_KEY)
        git(self.repo, "add", "config.py")
        git(self.repo, "commit", "-q", "-m", "init")
        self.write("config.py", "debug = True\n")
        git(self.repo, "add", "config.py")
        self.assertEqual(self.run_hook('git commit -m "fix: drop key"').returncode, 0)

    def test_ignores_commands_that_are_not_commits(self) -> None:
        self.write("config.py", FAKE_KEY)
        git(self.repo, "add", "config.py")
        self.assertEqual(self.run_hook('git log --grep "commit"').returncode, 0)

    def test_escape_hatch_lets_a_reviewed_commit_through(self) -> None:
        self.write("config.py", FAKE_KEY)
        git(self.repo, "add", "config.py")
        result = self.run_hook('ALLOW_SECRET=1 git commit -m "test: fixture key"')
        self.assertEqual(result.returncode, 0)

    def test_blocks_when_the_payload_cannot_be_read(self) -> None:
        result = self.run_hook(raw="not json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not checked", result.stderr)


if __name__ == "__main__":
    unittest.main()
