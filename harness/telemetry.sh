#!/usr/bin/env bash
# telemetry.sh: log GPU state every 5 s while a run is going, so a slow or odd run can be explained.
#   harness/telemetry.sh runs/<run_id>/gpu.csv &   (note the PID; kill it when the run ends)
# Columns: time, GPU name, temperature, utilisation, memory used/total, power, SM clock, clock-event
# (throttle) reasons, uncorrected ECC errors. A rising ECC count or constant thermal/power throttling is
# worth a line in the run notes.
set -euo pipefail
out="${1:?usage: telemetry.sh OUT.csv [interval_seconds]}"
interval="${2:-5}"
mkdir -p "$(dirname "$out")"
base="timestamp,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,clocks.sm"
fields=""
# nvidia-smi renamed clocks_throttle_reasons to clocks_event_reasons; use whichever this driver knows
for extra in "clocks_event_reasons.active,ecc.errors.uncorrected.volatile.total" \
             "clocks_throttle_reasons.active,ecc.errors.uncorrected.volatile.total" ""; do
  q="$base${extra:+,$extra}"
  if nvidia-smi --query-gpu="$q" --format=csv,noheader >/dev/null 2>&1; then fields="$q"; break; fi
done
[ -n "$fields" ] || { echo "nvidia-smi query failed" >&2; exit 1; }
# exec: the logger replaces this shell, so "kill $TPID" stops nvidia-smi itself (without it the child kept
# writing into the run folder after the run ended)
exec nvidia-smi --query-gpu="$fields" --format=csv -l "$interval" >> "$out"
