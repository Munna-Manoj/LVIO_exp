#!/bin/bash
# Install a git pre-commit hook that refuses commits with machine-specific paths or private tokens
# (tools/check_tree.py, which reads private_tokens from your git-ignored lvx.local.yaml).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cat > "$REPO/.git/hooks/pre-commit" <<'HOOK'
#!/bin/bash
python3 tools/check_chapters.py && python3 tools/check_tree.py || { echo "pre-commit: fix the problems above (or remove the file from the commit)"; exit 1; }
HOOK
chmod +x "$REPO/.git/hooks/pre-commit"
echo "installed .git/hooks/pre-commit"
cat > "$REPO/.git/hooks/commit-msg" <<'HOOK'
#!/bin/bash
python3 - "$1" <<'PY'
import re, sys
sys.path.insert(0, ".")
from lvx import config
msg = open(sys.argv[1]).read()
bad = [t for t in config.private_tokens() if re.search(re.escape(t), msg, re.I)]
if bad or re.search(r"/(home|hdd|Users|mnt|media|srv)/\w", msg):
    sys.exit(f"commit-msg: message contains machine-specific text {bad or '(an absolute path)'}")
PY
HOOK
chmod +x "$REPO/.git/hooks/commit-msg"
echo "installed .git/hooks/commit-msg"
