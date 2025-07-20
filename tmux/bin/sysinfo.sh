#!/bin/bash

## ======== BATTERY INFO ========
## ==============================

battery_status="N/A"
if command -v pmset &>/dev/null; then
  ## macOS
  power_source=$(pmset -g batt | grep "Now drawing from" | awk -F"'" '{print $2}')
  battery_level=$(LANG=C pmset -g batt | grep -o '[0-9]\+%' | head -1 | tr -d '%')
  if [[ "$power_source" == "AC Power" ]]; then
    battery_status="${battery_level}%+"
  else
    battery_status="${battery_level}%-"
  fi
elif [[ -d /sys/class/power_supply/ ]]; then
  ## linux (e.g., battery in /sys)
  battery_dir=$(find /sys/class/power_supply/ -maxdepth 1 -name 'BAT*' | head -n 1)
  if [[ -n "$battery_dir" ]]; then
    capacity=$(cat "$battery_dir/capacity" 2>/dev/null)
    status=$(cat "$battery_dir/status" 2>/dev/null)
    battery_status="${capacity}%"
    [[ "$status" == "Charging" ]] && battery_status="${battery_status}+"
    [[ "$status" == "Discharging" ]] && battery_status="${battery_status}-"
  fi
fi

## ======== MEMORY + CPU STATS ========
## ====================================

tmux_mem_cpu_load=$(command -v tmux-mem-cpu-load || echo "/opt/homebrew/bin/tmux-mem-cpu-load")
mem_used="N/A"
cpu_used="N/A"
if [[ -x "$tmux_mem_cpu_load" ]]; then
  system_stats=$("$tmux_mem_cpu_load" --interval 1 2>/dev/null)
  if [[ $system_stats =~ ^([0-9]+/[0-9]+GB)[[:space:]]+\[.*\][[:space:]]+([0-9.]+%) ]]; then
    mem_used="${BASH_REMATCH[1]}"
    cpu_used="${BASH_REMATCH[2]}"
  fi
fi

## ======== OUTPUT ========
## ========================

echo "Charge: $battery_status  CPU: $cpu_used  MEM: $mem_used"

## .