"""The git workflow is enforced by code: the Claude guard blocks hook bypasses, the git hooks block main."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "scripts" / "hooks" / "claude_guard.py"


def guard(command):
    event = json.dumps({"tool_input": {"command": f"cd {ROOT} && {command}"}, "cwd": str(ROOT)})
    return subprocess.run([sys.executable, str(GUARD)], input=event, capture_output=True, text=True).returncode


def test_guard_blocks_bypasses():
    for cmd in ("git -c core.hooksPath=/dev/null commit -m 'docs: x'",
                "git commit --no-verify -m 'docs: x'", "git commit -n -m 'docs: x'", "git push origin main",
                "git push origin HEAD:main", "git push --force origin infra/x", "git config core.hooksPath /tmp"):
        assert guard(cmd) == 2, cmd


def test_guard_allows_normal_work():
    for cmd in ("git status", "git log --oneline -3", "git push -u origin infra/x", "git diff"):
        assert guard(cmd) == 0, cmd


def test_hooks_refuse_push_to_main_and_bad_subjects(tmp_path):
    push = subprocess.run(["bash", str(ROOT / "scripts/hooks/pre-push")], input="refs/heads/x a refs/heads/main b\n",
                          capture_output=True, text=True)
    assert push.returncode == 1
    msg = tmp_path / "msg"
    for subject, ok in (("bad subject", False), ("docs(course): fine", True), ("feat(EXP-003): fine", True)):
        msg.write_text(subject + "\n")
        r = subprocess.run(["bash", str(ROOT / "scripts/hooks/commit-msg"), str(msg)], cwd=ROOT, capture_output=True)
        assert (r.returncode == 0) == ok, subject
