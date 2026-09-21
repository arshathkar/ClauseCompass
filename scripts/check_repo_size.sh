#!/usr/bin/env bash
# Check that the repository stays under the size budget.
# Fails CI at > 8 MB (internal target ≤ 5 MB).

set -euo pipefail

MAX_SIZE_KB=8192  # 8 MB

# Working tree size (excluding .git)
TREE_SIZE_KB=$(du -sk --exclude=.git --exclude=node_modules --exclude=.venv --exclude=__pycache__ . | cut -f1)

echo "Working tree size: ${TREE_SIZE_KB} KB"

if [ "$TREE_SIZE_KB" -gt "$MAX_SIZE_KB" ]; then
  echo "ERROR: Repository working tree (${TREE_SIZE_KB} KB) exceeds budget (${MAX_SIZE_KB} KB)"
  echo "Largest files:"
  find . -not -path './.git/*' -not -path './node_modules/*' -not -path './.venv/*' \
    -type f -size +100k -exec ls -lhS {} + | head -20
  exit 1
fi

echo "OK: Repository size within budget"

# Check for common bloat
echo ""
echo "Checking for accidentally committed binaries..."
BINARY_EXTS="pdf|png|jpg|jpeg|gif|mp4|zip|tar|gz|whl|egg|so|dll|exe|pyc|pyo"
FOUND=$(find . -not -path './.git/*' -not -path './node_modules/*' -not -path './.venv/*' \
  -type f -regextype posix-extended -regex ".*\.(${BINARY_EXTS})$" 2>/dev/null | head -5)

if [ -n "$FOUND" ]; then
  echo "WARNING: Found binary files that probably shouldn't be committed:"
  echo "$FOUND"
fi

echo "Done."
