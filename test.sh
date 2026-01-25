#!/usr/bin/env bash
set -euo pipefail

# Test runner for python-socketio repository
# Usage:
#   ./test.sh base   # run existing tests (should pass at base commit)
#   ./test.sh new    # run only the newly added tests

cmd_exists() {
  command -v "$1" >/dev/null 2>&1
}

run_pytest() {
  if cmd_exists pytest; then
    pytest -q "$@"
  else
    python -m pytest -q "$@"
  fi
}

# Ensure an argument is provided before entering case
if [ $# -lt 1 ]; then
  echo "Usage: ./test.sh {base|new}" >&2
  exit 1
fi

case "$1" in
  base)
    # Run the repository's existing test suite only
    if [ -d tests ]; then
      run_pytest tests/
    else
      echo "ERROR: Base suite not found at ./tests/. Provide baseline tests or adjust runner." >&2
      exit 2
    fi
    ;;
  new)
    if [ -f new_tests/test_message_history.py ]; then
      run_pytest new_tests/test_message_history.py
    else
      echo "ERROR: New test file not found: new_tests/test_message_history.py" >&2
      exit 2
    fi
    ;;
  *)
    echo "Usage: ./test.sh {base|new}" >&2
    exit 1
    ;;
esac
