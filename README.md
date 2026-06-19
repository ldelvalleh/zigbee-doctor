# Zigbee Doctor

Zigbee Doctor is an unofficial Home Assistant custom integration for Zigbee2MQTT health diagnostics.

Its goal is simple: make Zigbee networks understandable for normal people.

Instead of forcing users to read raw MQTT topics, LQI values, logs and network maps, Zigbee Doctor collects Zigbee2MQTT health data, detects common problems and exposes a clean Home Assistant sidebar panel with actionable information.

> Current status: early development. Phase 0, Phase 1 and Phase 2 are being implemented first. AI reports are planned as a core feature after the rule-based diagnostic engine is stable.

## What Zigbee Doctor will do

- Listen to Zigbee2MQTT MQTT topics.
- Track bridge status, device availability, device count and recent logs.
- Detect common Zigbee network problems.
- Expose Home Assistant sensors and binary sensors.
- Add a minimal Home Assistant sidebar panel.
- Support English and Spanish.
- Generate AI-assisted diagnostic reports in a future phase.

## Requirements

- Home Assistant.
- MQTT integration configured in Home Assistant.
- Zigbee2MQTT using the same MQTT broker.
- HACS for easy installation.

## Recommended Zigbee2MQTT configuration

Zigbee Doctor works best when Zigbee2MQTT publishes availability, last seen data and bridge health.

Add or review these options in your Zigbee2MQTT `configuration.yaml`:

```yaml
availability:
  enabled: true

health:
  interval: 10
  reset_on_check: true

advanced:
  last_seen: ISO_8601
```

Depending on your Zigbee2MQTT version, `availability: true` may also be valid. The important part is that Zigbee2MQTT publishes device availability topics like:

```text
zigbee2mqtt/<friendly_name>/availability
```

And bridge health data like:

```text
zigbee2mqtt/bridge/health
```

After changing Zigbee2MQTT configuration, restart Zigbee2MQTT.

## Installation through HACS

This repository is designed as a HACS custom repository.

1. Open HACS.
2. Go to Integrations.
3. Open the three-dot menu.
4. Select Custom repositories.
5. Add this repository URL:

```text
https://github.com/ldelvalleh/zigbee-doctor
```

6. Category: Integration.
7. Install Zigbee Doctor.
8. Restart Home Assistant.
9. Go to Settings > Devices & services > Add integration.
10. Search for Zigbee Doctor.

## Initial configuration

During setup, Zigbee Doctor asks for:

- Zigbee2MQTT base topic. Default: `zigbee2mqtt`.
- Whether to enable the sidebar panel. Default: enabled.
- Low battery threshold. Default: `20%`.
- Passive device timeout. Default: `25 hours`.
- Active device timeout. Default: `10 minutes`.

## Entities created

The first versions expose entities like:

- `sensor.zigbee_doctor_network_status`
- `sensor.zigbee_doctor_health_score`
- `sensor.zigbee_doctor_device_count`
- `sensor.zigbee_doctor_offline_devices`
- `sensor.zigbee_doctor_problem_count`
- `sensor.zigbee_doctor_low_battery_devices`
- `binary_sensor.zigbee_doctor_problem_detected`
- `binary_sensor.zigbee_doctor_bridge_connected`

## Sidebar panel

Zigbee Doctor adds a Home Assistant sidebar item called **Zigbee Doctor**.

The panel is intentionally minimal:

- Overall network status.
- Health score.
- Offline devices.
- Problems found.
- Low battery devices.
- Simple action buttons.

No complicated network jargon unless it is needed.

## Roadmap

### Phase 0 — HACS skeleton

- Custom integration structure.
- Config flow.
- HACS metadata.
- Translations.
- Basic sidebar panel.

### Phase 1 — Zigbee2MQTT data collection

- Subscribe to Zigbee2MQTT MQTT topics.
- Track bridge state.
- Track bridge health.
- Track devices.
- Track availability.
- Track recent logs.

### Phase 2 — Rule-based diagnostics

- Detect bridge offline.
- Detect unavailable devices.
- Detect low batteries.
- Detect device leave events.
- Detect network address changes.
- Detect noisy devices.
- Detect recent warnings/errors.

### Phase 3 — AI reports

- Generate human-readable reports.
- Explain likely causes.
- Suggest first actions.
- Avoid making unsupported claims.
- Support Home Assistant AI providers where possible.

### Phase 4 — Smart notifications

- Notify only when something meaningful happens.
- Avoid notification spam.
- Include clear recommended action.

### Phase 5 — Advanced dashboard

- Better visual timeline.
- Router/device dependency view.
- Network map integration.
- Historical trends.

## Design principles

1. Be understandable for non-technical users.
2. Be honest about Zigbee uncertainty.
3. Use rule-based diagnostics before AI.
4. Explain what changed, what matters and what to do first.
5. Do not pretend LQI alone tells the full story.

## License

MIT
