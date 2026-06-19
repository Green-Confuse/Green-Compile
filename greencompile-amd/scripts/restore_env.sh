#!/usr/bin/env bash
set -euo pipefail

echo "[GREENCOMPILE] Restoring system environment..."

STATE_DIR="${STATE_DIR:-/tmp/greencompile}"
STATE_FILE="${STATE_FILE:-$STATE_DIR/env_state.sh}"

try() { "$@" >/dev/null 2>&1 || true; }

if [[ ! -f "$STATE_FILE" ]]; then
  echo "[GREENCOMPILE] No state file found at: $STATE_FILE"
  echo "[GREENCOMPILE] Nothing to restore."
  exit 0
fi

# Ensure sudo is available
if ! sudo -n true 2>/dev/null; then
  echo "[GREENCOMPILE] sudo permission is required (you may be prompted)."
  sudo true
fi

# Load saved state
# shellcheck disable=SC1090
source "$STATE_FILE"

# --- Restore CPU governors ---
echo "[GREENCOMPILE] Restoring CPU governor settings..."
if [[ ${#GOV_PATHS[@]} -eq ${#GOV_VALS[@]} ]]; then
  for i in "${!GOV_PATHS[@]}"; do
    p="${GOV_PATHS[$i]}"
    v="${GOV_VALS[$i]}"
    [[ -e "$p" ]] || continue
    [[ -n "$v" ]] || continue
    try sudo bash -c "echo '$v' > '$p'"
  done
fi

# --- Restore APT services/timers ---
echo "[GREENCOMPILE] Restoring APT services/timers..."

# Restore enable/disable and active state for all recorded units
for unit in "${!UNIT_ENABLED[@]}"; do
  enabled="${UNIT_ENABLED[$unit]}"
  active="${UNIT_ACTIVE[$unit]}"

  # enablement
  if [[ "$enabled" == "enabled" ]]; then
    try sudo systemctl enable "$unit"
  elif [[ "$enabled" == "disabled" ]]; then
    try sudo systemctl disable "$unit"
  fi

  # active state
  if [[ "$active" == "active" ]]; then
    try sudo systemctl start "$unit"
  else
    try sudo systemctl stop "$unit"
  fi
done

# --- Restore radios ---
if command -v nmcli >/dev/null 2>&1; then
  echo "[GREENCOMPILE] Restoring radio states (nmcli)..."
  case "${NMCLI_WIFI_STATE:-}" in
    enabled)  try nmcli radio wifi on ;;
    disabled) try nmcli radio wifi off ;;
  esac
  case "${NMCLI_WWAN_STATE:-}" in
    enabled)  try nmcli radio wwan on ;;
    disabled) try nmcli radio wwan off ;;
  esac
fi

echo "[GREENCOMPILE] Restore complete."
