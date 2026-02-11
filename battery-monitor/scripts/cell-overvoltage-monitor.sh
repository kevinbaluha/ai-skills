#!/bin/bash
# Cell overvoltage monitor — alerts when any cell hits high threshold
# Config: source from ~/.config/battery-monitor/config or env vars

CONFIG_FILE="${HOME}/.config/battery-monitor/config"
[[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"

HA_URL="${HA_URL:?Set HA_URL in $CONFIG_FILE or env}"
HA_TOKEN="${HA_TOKEN:?Set HA_TOKEN in $CONFIG_FILE or env}"
HIGH_THRESHOLD="${HIGH_THRESHOLD:-3.6}"
RESET_THRESHOLD="${RESET_THRESHOLD:-3.39}"
TARGETS="${TARGETS:-media_player.north_echo,media_player.hallway_echo}"
FLAG_150="/tmp/cell-overvoltage-150ah"
FLAG_500="/tmp/cell-overvoltage-500ah"

get_voltage() {
  curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/$1" | python3 -c "import json,sys; print(json.load(sys.stdin)['state'])" 2>/dev/null
}

TARGET_JSON=$(python3 -c "print('[' + ','.join(['\"' + t.strip() + '\"' for t in '$TARGETS'.split(',')]) + ']')")

check_bank() {
  local bank_name="$1"
  local sensor_prefix="$2"
  local flag_file="$3"

  local high_cells=""
  local all_below_reset="yes"

  for i in $(seq 1 8); do
    local v=$(get_voltage "${sensor_prefix}${i}")
    [[ -z "$v" ]] && continue

    local is_high=$(python3 -c "print('yes' if float('$v') >= $HIGH_THRESHOLD else 'no')")
    local is_below_reset=$(python3 -c "print('yes' if float('$v') <= $RESET_THRESHOLD else 'no')")

    if [[ "$is_high" == "yes" ]]; then
      high_cells="${high_cells}Cell ${i} at $(python3 -c "print(f'{float(\"$v\"):.3f}')") volts. "
    fi
    if [[ "$is_below_reset" != "yes" ]]; then
      all_below_reset="no"
    fi
  done

  if [[ -n "$high_cells" ]]; then
    if [[ ! -f "$flag_file" ]]; then
      curl -s -X POST \
        -H "Authorization: Bearer $HA_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Warning! ${bank_name} bank overvoltage. ${high_cells}\", \"target\": ${TARGET_JSON}}" \
        "$HA_URL/api/services/notify/alexa_media" > /dev/null
      touch "$flag_file"
    fi
  elif [[ "$all_below_reset" == "yes" ]]; then
    rm -f "$flag_file"
  fi
}

check_bank "150 amp hour" "sensor.bms_battery_150ah_cell_voltage_" "$FLAG_150"
check_bank "500 amp hour" "sensor.bms_battery_500ah_cell_voltage_" "$FLAG_500"
