#!/usr/bin/env bash
# secrets_not_in_git.sh: executable hygiene checks that fail closed
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

# 1) .env must be ignored
if ! git check-ignore -v .env >/dev/null 2>&1; then
  fail ".env is not gitignored"
fi

# 2) .env must never appear in history
if git log --all --full-history -- .env 2>/dev/null | grep -q .; then
  fail ".env appears in git history: rotate the secrets"
fi

# 3) Compose must not inline quoted JWT-like values
python3 check_gitignore.py || fail "check_gitignore.py reported a problem"

echo "OK: secrets_not_in_git.sh passed"