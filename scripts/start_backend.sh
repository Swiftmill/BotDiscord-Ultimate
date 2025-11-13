#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
source "$ROOT_DIR/venv_backend/bin/activate"
uvicorn backend.app:app --host 0.0.0.0 --port 8000
