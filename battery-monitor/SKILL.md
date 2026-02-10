---
name: battery-monitor
description: Monitor battery bank voltages via Home Assistant sensors. Announces on Alexa Echo when both banks drop below threshold. Reports once with hysteresis — resets when voltage recovers. Use when setting up battery alerts or voltage monitoring cron jobs.
---

# Battery Monitor

Monitors HA battery voltage sensors every minute via cron. Announces on Alexa Echo when both banks are low.

## Behavior

1. Reads `sensor.power_room_250ah_battery_bank_measured_voltage` and `sensor.power_room_500ah_battery_bank_measured_voltage`
2. If **both** below threshold → announces highest voltage on target Echo
3. Reports **once** (flag file at `/tmp/battery-low-reported`)
4. When either voltage recovers above threshold → resets flag

## Setup

```bash
# Install cron (every minute)
chmod +x scripts/battery-monitor.sh
(crontab -l 2>/dev/null; echo "* * * * * /path/to/scripts/battery-monitor.sh") | crontab -
```

## Configuration

Edit `scripts/battery-monitor.sh`:
- `THRESHOLD` — voltage trigger (default: `26.0`)
- `target` — Echo device entity (default: `media_player.north_echo`)
- `HA_TOKEN` — Home Assistant long-lived access token
