#!/usr/bin/env python3
"""Claude Code PreToolUse hook (.claude/settings.json): block what git hooks cannot stop on their own.

The git hooks in this folder refuse commits on main, bad commit messages and pushes to main. A tool
call can still bypass them, so for any Bash command that touches this repository this guard blocks:
  - `git commit` / `git push` with --no-verify (or `commit -n`)
  - force pushes, and pushes that name main/master as the target
  - turning the hooks off (changing or unsetting core.hooksPath)
  - `git commit` while the hooks are inactive, or while on main/master

Exit 2 = block (the message goes back to Claude); exit 0 = allow.
"""
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HOOKS = "scripts/hooks"


def git(repo, *args):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return out.stdout.strip()


def repos_touched(command, cwd):
    """Directories the command runs git in: `cd X`, `git -C X`, else the session's cwd."""
    dirs = re.findall(r"(?:\bcd|\bgit\s+-C)\s+(\"[^\"]+\"|'[^']+'|\S+)", command)
    dirs = [Path(shlex.split(d)[0]).expanduser() for d in dirs] or [Path(cwd)]
    for d in dirs:
        d = d if d.is_absolute() else Path(cwd) / d
        top = git(d, "rev-parse", "--show-toplevel") if d.is_dir() else ""
        if top and (Path(top) / "tools" / "check_chapters.py").exists():   # this repository
            yield Path(top)


def problems(command, repo):
    found = []
    for part in re.split(r"&&|\|\||;|\n", command):
        words = part.split()
        if "git" not in words:
            continue
        verb = next((w for w in words[words.index("git") + 1:] if not w.startswith("-") and "/" not in w), "")
        if verb in ("commit", "push") and ("--no-verify" in words or (verb == "commit" and "-n" in words)):
            found.append(f"`git {verb} --no-verify` skips the repo's hooks; fix what the hook reports instead")
        if verb == "push" and any(w in ("-f", "--force", "--force-with-lease") or w.startswith("--force")
                                  for w in words):
            found.append("force pushes are not allowed")
        if verb == "push" and any(re.fullmatch(r"(\S*:)?(refs/heads/)?(main|master)", w) for w in words[2:]):
            found.append("never push to main/master: push the branch and open a PR")
        if "core.hooksPath" in part and HOOKS not in part and (verb == "config" or "-c" in words):
            found.append(f"core.hooksPath must stay '{HOOKS}' (run scripts/install_hooks.sh)")
        if verb == "commit":
            if git(repo, "config", "core.hooksPath") != HOOKS:
                found.append("git hooks are not active here: run `bash scripts/install_hooks.sh` first")
            if git(repo, "symbolic-ref", "--short", "-q", "HEAD") in ("main", "master"):
                found.append("you are on main: `git switch -c <exp/…|infra/…|docs/…>` before committing")
    return found


def main():
    event = json.load(sys.stdin)
    command = (event.get("tool_input") or {}).get("command", "")
    if "git" not in command:
        return 0
    found = []
    for repo in repos_touched(command, event.get("cwd", ".")):
        found += problems(command, repo)
    if found:
        print("Blocked by scripts/hooks/claude_guard.py (CLAUDE.md §7):\n- " + "\n- ".join(dict.fromkeys(found)),
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
