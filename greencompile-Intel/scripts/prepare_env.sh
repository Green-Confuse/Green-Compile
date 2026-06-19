#!/usr/bin/env bash
set -euo pipefail

echo "[GREENCOMPILE] Preparing system for measurements..."

STATE_DIR="${STATE_DIR:-/tmp/greencompile}"
STATE_FILE="${STATE_FILE:-$STATE_DIR/env_state.sh}"
mkdir -p "$STATE_DIR"

try() { "$@" >/dev/null 2>&1 || true; }

# Ensure sudo is available early
if ! sudo -n true 2>/dev/null; then
  echo "[GREENCOMPILE] sudo permission is required (you may be prompted)."
  sudo true
fi

# Write a source-able bash state file
cat > "$STATE_FILE" <<'EOF'
# GREENCOMPILE ENV STATE (source-able)
STATE_VERSION="2"
TIMESTAMP_UTC="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

declare -A UNIT_ENABLED
declare -A UNIT_ACTIVE

NMCLI_WIFI_STATE=""
NMCLI_WWAN_STATE=""

declare -a GOV_PATHS=()
declare -a GOV_VALS=()
EOF

# --- Network radios ---
if command -v nmcli >/dev/null 2>&1; then
  WIFI_STATE="$(nmcli -t -f WIFI general 2>/dev/null | head -n1 | cut -d: -f2 || true)"
  WWAN_STATE="$(nmcli -t -f WWAN general 2>/dev/null | head -n1 | cut -d: -f2 || true)"

  {
    echo "NMCLI_WIFI_STATE=$(printf %q "${WIFI_STATE:-}")"
    echo "NMCLI_WWAN_STATE=$(printf %q "${WWAN_STATE:-}")"
  } >> "$STATE_FILE"

  echo "[GREENCOMPILE] Turning radios off (nmcli)..."
  try nmcli radio all off
fi

# --- APT services/timers ---
SERVICES=(
  apt-daily.service
  apt-daily-upgrade.service
  unattended-upgrades.service
)
TIMERS=(
  apt-daily.timer
  apt-daily-upgrade.timer
)

for unit in "${SERVICES[@]}" "${TIMERS[@]}"; do
  enabled="$(systemctl is-enabled "$unit" 2>/dev/null || true)"
  active="$(systemctl is-active "$unit" 2>/dev/null || true)"
  {
    printf 'UNIT_ENABLED[%q]=%q\n' "$unit" "$enabled"
    printf 'UNIT_ACTIVE[%q]=%q\n' "$unit" "$active"
  } >> "$STATE_FILE"
done

echo "[GREENCOMPILE] Stopping APT related services/timers..."
for unit in "${TIMERS[@]}"; do try sudo systemctl stop "$unit"; done
for unit in "${SERVICES[@]}"; do try sudo systemctl stop "$unit"; done
for unit in "${TIMERS[@]}"; do try sudo systemctl disable "$unit"; done

# --- CPU governor (policy preferred; fallback per-cpu) ---
echo "[GREENCOMPILE] Setting CPU governor to performance..."

gov_paths=()
gov_vals=()

if ls /sys/devices/system/cpu/cpufreq/policy*/scaling_governor >/dev/null 2>&1; then
  while IFS= read -r -d '' p; do
    gov_paths+=("$p")
    gov_vals+=("$(cat "$p" 2>/dev/null || true)")
  done < <(find /sys/devices/system/cpu/cpufreq -path '*/policy*/scaling_governor' -print0 2>/dev/null)

  for p in "${gov_paths[@]}"; do
    try sudo bash -c "echo performance > '$p'"
  done
else
  while IFS= read -r -d '' p; do
    gov_paths+=("$p")
    gov_vals+=("$(cat "$p" 2>/dev/null || true)")
  done < <(find /sys/devices/system/cpu -path '*/cpufreq/scaling_governor' -print0 2>/dev/null)

  for p in "${gov_paths[@]}"; do
    try sudo bash -c "echo performance > '$p'"
  done
fi

# Save governor arrays into state file safely
{
  echo "GOV_PATHS=()"
  for p in "${gov_paths[@]}"; do printf 'GOV_PATHS+=(%q)\n' "$p"; done
  echo "GOV_VALS=()"
  for v in "${gov_vals[@]}"; do printf 'GOV_VALS+=(%q)\n' "$v"; done
} >> "$STATE_FILE"

# --- Thermal stabilization ---
STABILIZE_SECONDS="${STABILIZE_SECONDS:-180}"
echo "[GREENCOMPILE] Waiting for thermal stabilization (${STABILIZE_SECONDS}s)..."
sleep "$STABILIZE_SECONDS"

echo "[GREENCOMPILE] Environment prepared."
echo "[GREENCOMPILE] State saved to: $STATE_FILE"
