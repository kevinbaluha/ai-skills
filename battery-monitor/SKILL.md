---
name: battery-monitor
description: Monitor battery bank voltages via Home Assistant sensors. Announces on Alexa Echo when banks drop below threshold or individual cells hit overvoltage. Use when setting up battery alerts, cell monitoring, or voltage cron jobs.
---

# Battery Monitor

Monitors HA battery voltage sensors every minute via cron. Announces on Alexa Echo devices.

## Scripts

### battery-monitor.sh
Checks both 250Ah and 500Ah bank measured voltages. Announces when **both** drop below threshold.
- Reports **once** (flag: `/tmp/battery-low-reported`)
- Resets when either bank recovers above threshold

### cell-overvoltage-monitor.sh
Checks all 16 cells (8 per bank: 150Ah + 500Ah). Announces when **any cell** hits high threshold.
- Reports **once per bank** (flags: `/tmp/cell-overvoltage-150ah`, `/tmp/cell-overvoltage-500ah`)
- Resets when **all cells** in that bank drop to reset threshold or below

## Setup

```bash
# Create config (no secrets in scripts)
mkdir -p ~/.config/battery-monitor
cp config.example ~/.config/battery-monitor/config
# Edit with your HA URL, token, thresholds, and target Echo devices
chmod 600 ~/.config/battery-monitor/config

# Install crons
chmod +x scripts/*.sh
(crontab -l 2>/dev/null; echo "* * * * * /path/to/scripts/battery-monitor.sh") | crontab -
(crontab -l 2>/dev/null; echo "* * * * * /path/to/scripts/cell-overvoltage-monitor.sh") | crontab -
```

## Configuration

Edit `~/.config/battery-monitor/config`:
- `HA_URL` — Home Assistant base URL
- `HA_TOKEN` — Long-lived access token
- `THRESHOLD` — Bank voltage alert level (default: `26.0`)
- `HIGH_THRESHOLD` — Cell overvoltage level (default: `3.6`)
- `RESET_THRESHOLD` — Cell reset level (default: `3.39`)
- `TARGETS` — Comma-separated Echo media_player entities
