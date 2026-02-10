#!/bin/bash
# Battery voltage monitor — checks every minute, reports once when both banks < 26.3V

HA_URL="http://192.168.102.30:8123/api"
HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxOTI2MDcxODM2MmI0MjE1YjhlNzhmOTNlMzAzOWZhNCIsImlhdCI6MTc2OTYwNDcxNCwiZXhwIjoyMDg0OTY0NzE0fQ.2aQ9CB2BCN4S-dcvHCpScWKR-d1yPhrWCSDTKXPwQIQ"
FLAG="/tmp/battery-low-reported"
THRESHOLD="26.0"

get_voltage() {
  curl -s -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/states/$1" | python3 -c "import json,sys; print(json.load(sys.stdin)['state'])" 2>/dev/null
}

V250=$(get_voltage "sensor.power_room_250ah_battery_bank_measured_voltage")
V500=$(get_voltage "sensor.power_room_500ah_battery_bank_measured_voltage")

# Exit if we can't read voltages
[[ -z "$V250" || -z "$V500" ]] && exit 1

BOTH_LOW=$(python3 -c "print('yes' if float('$V250') < $THRESHOLD and float('$V500') < $THRESHOLD else 'no')")
HIGHEST=$(python3 -c "print(f'{max(float(\"$V250\"), float(\"$V500\")):.2f}')")

if [[ "$BOTH_LOW" == "yes" ]]; then
  if [[ ! -f "$FLAG" ]]; then
    # Report and set flag
    curl -s -X POST \
      -H "Authorization: Bearer $HA_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"The battery voltage is below ${HIGHEST} volts.\", \"target\": [\"media_player.north_echo\"]}" \
      "$HA_URL/services/notify/alexa_media" > /dev/null
    touch "$FLAG"
  fi
else
  # Reset flag when either goes above threshold
  rm -f "$FLAG"
fi
