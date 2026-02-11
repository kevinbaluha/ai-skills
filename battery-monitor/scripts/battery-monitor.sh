#!/bin/bash
# Battery voltage monitor — checks every minute, reports once when both banks < threshold
# Config: source from ~/.config/battery-monitor/config or env vars

CONFIG_FILE="${HOME}/.config/battery-monitor/config"
[[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"

HA_URL="${HA_URL:?Set HA_URL in $CONFIG_FILE or env}"
HA_TOKEN="${HA_TOKEN:?Set HA_TOKEN in $CONFIG_FILE or env}"
THRESHOLD="${THRESHOLD:-26.0}"
TARGETS="${TARGETS:-media_player.north_echo,media_player.hallway_echo}"
FLAG="/tmp/battery-low-reported"

get_voltage() {
  curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states/$1" | python3 -c "import json,sys; print(json.load(sys.stdin)['state'])" 2>/dev/null
}

V250=$(get_voltage "sensor.power_room_250ah_battery_bank_measured_voltage")
V500=$(get_voltage "sensor.power_room_500ah_battery_bank_measured_voltage")

[[ -z "$V250" || -z "$V500" ]] && exit 1

BOTH_LOW=$(python3 -c "print('yes' if float('$V250') < $THRESHOLD and float('$V500') < $THRESHOLD else 'no')")
HIGHEST=$(python3 -c "print(f'{max(float(\"$V250\"), float(\"$V500\")):.2f}')")

# Build target JSON array
TARGET_JSON=$(python3 -c "print('[' + ','.join(['\"' + t.strip() + '\"' for t in '$TARGETS'.split(',')]) + ']')")

if [[ "$BOTH_LOW" == "yes" ]]; then
  if [[ ! -f "$FLAG" ]]; then
    curl -s -X POST \
      -H "Authorization: Bearer $HA_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"The battery voltage is below ${HIGHEST} volts.\", \"target\": ${TARGET_JSON}}" \
      "$HA_URL/api/services/notify/alexa_media" > /dev/null
    touch "$FLAG"
  fi
else
  rm -f "$FLAG"
fi
