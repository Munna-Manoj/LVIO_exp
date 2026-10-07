#!/bin/bash
# Activate the tracked git hooks in scripts/hooks/ (run once per clone; CLAUDE.md §7):
#   pre-commit  no commits on main/master; chapters self-contained; no machine-specific files
#   commit-msg  Conventional Commits subject; no machine-specific text in the message
#   pre-push    no direct pushes to main/master (PRs only)
set -euo pipefail
cd "$(dirname "$0")/.."
git config core.hooksPath scripts/hooks
rm -f .git/hooks/pre-commit .git/hooks/commit-msg     # old copied hooks, now tracked in scripts/hooks/
echo "git hooks active: $(git config core.hooksPath)/{pre-commit,commit-msg,pre-push}"
