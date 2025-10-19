#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
RUNNER="${ROOT_DIR}/scripts/Run-VoiceEnginesUpdate.ps1"

if ! command -v pwsh >/dev/null 2>&1; then
  echo "Error: pwsh (PowerShell) is required." >&2
  exit 1
fi

if [[ $# -gt 0 ]]; then
  if [[ "$1" == "--handshake" && -n "${2-}" ]]; then
    exec pwsh -File "$RUNNER" -HandshakeFile "$2"
  elif [[ "$1" == "--stdin" ]]; then
    exec pwsh -File "$RUNNER" -FromStdin
  elif [[ "$1" == "--list" ]]; then
    exec pwsh -File "$RUNNER" -List
  else
    echo "Usage: $0 [--handshake path.json | --stdin | --list]" >&2
    exit 2
  fi
else
  exec pwsh -File "$RUNNER" -ApplyPending
fi
