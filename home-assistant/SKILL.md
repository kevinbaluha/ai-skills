---
name: home-assistant
description: Control Home Assistant devices and automations via REST API. Use when asked to control lights, thermostats, switches, sensors, media players, automations, or Alexa TTS announcements. Also use for HA entity discovery, state queries, and scene/automation management.
---

# Home Assistant

Control HA via REST API. Base URL and token are in TOOLS.md (always-loaded context).

## Quick Reference

```bash
# Headers for all requests
AUTH="Authorization: Bearer $HA_TOKEN"
BASE="http://192.168.102.30:8123/api"
```

### Get entity state
```bash
curl -s -H "$AUTH" "$BASE/states/ENTITY_ID"
```

### Set state / call service
```bash
# Turn on/off
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.kitchen_sink"}' \
  "$BASE/services/light/turn_on"

# Set brightness (0-255)
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.kitchen_sink", "brightness": 128}' \
  "$BASE/services/light/turn_on"

# Set thermostat
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"entity_id": "climate.north_thermostat", "temperature": 72}' \
  "$BASE/services/climate/set_temperature"

# Trigger automation
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.AUTOMATION_ID"}' \
  "$BASE/services/automation/trigger"
```

### Discover entities
```bash
# List all entities of a domain
curl -s -H "$AUTH" "$BASE/states" | python3 -c "
import json,sys
states=json.load(sys.stdin)
for s in states:
    if s['entity_id'].startswith('DOMAIN.'):
        print(s['entity_id'], '-', s['attributes'].get('friendly_name',''), '-', s['state'])
"
```

### List available services
```bash
curl -s -H "$AUTH" "$BASE/services" | python3 -c "
import json,sys
[print(f\"{s['domain']}.{k}\") for s in json.load(sys.stdin) for k in s.get('services',{})]
"
```

## Entity Inventory

For known entities (lights, thermostats, sensors, switches, media players), use `memory_search` for "home assistant entities" or read `memory/tools-homeassistant.md`.

## Key Patterns

- **Dining room lights:** Use `light.pancake` (groups Down One/Two/Three)
- **All kitchen:** `light.all_kitchen` (group)
- **Garage:** `switch.all_garage` (switch, not light)
- **Cistern:** `sensor.cistern_gallons` (water level)
- **Thermostats:** 5 zones — north, south, power_heat, water_room, om_shack

## Alexa TTS (via Alexa Media Player)

Requires Alexa Media Player custom component (HACS). Once configured:

```bash
# Announce to specific Echo
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.ECHO_NAME", "message": "Hello from Emma"}' \
  "$BASE/services/notify/alexa_media"

# Announce to all Echos
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"message": "Hello from Emma", "data": {"type": "announce"}}' \
  "$BASE/services/notify/alexa_media"

# TTS (plays, doesn't announce)
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.ECHO_NAME", "message": "Hello"}' \
  "$BASE/services/tts/cloud_say"
```

**Status:** HACS installed, Alexa Media Player installed, awaiting Amazon account linking.
Once linked, discover Echo entities with domain `media_player` or `notify`.

## Troubleshooting

- 401 → Check token in TOOLS.md
- Entity not found → Run discovery query above
- Automation not triggering → Check `automation.` prefix, verify entity exists
- Alexa not responding → Verify Alexa Media Player integration is authenticated
