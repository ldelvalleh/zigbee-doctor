# Zigbee Doctor architecture

Zigbee Doctor is designed as a Home Assistant custom integration installed through HACS.

The project is intentionally split into phases so the AI layer is built on top of reliable data instead of guessing from raw MQTT noise.

## Phase 0: HACS integration foundation

The integration provides:

- Home Assistant manifest.
- Config flow.
- Options flow.
- HACS metadata.
- Translations in English and Spanish.
- A sidebar panel.
- GitHub validation workflow.

## Phase 1: Zigbee2MQTT data collection

The integration subscribes to Zigbee2MQTT MQTT topics:

```text
zigbee2mqtt/bridge/state
zigbee2mqtt/bridge/health
zigbee2mqtt/bridge/devices
zigbee2mqtt/bridge/logging
zigbee2mqtt/bridge/event
zigbee2mqtt/+/availability
zigbee2mqtt/+
```

The base topic is configurable. `zigbee2mqtt` is only the default.

Collected data:

- Bridge state.
- Bridge health payload.
- Device list.
- Device availability.
- Recent logs.
- Recent events.
- Device state payloads such as battery, linkquality and last_seen.

## Phase 2: Rule-based diagnostics

The rule engine is the first source of truth.

It detects symptoms such as:

- Bridge offline.
- Bridge state unknown.
- Device offline.
- Powered router offline.
- Low battery.
- Device has not reported recently.
- Device left the network.
- Network address changes.
- Very chatty devices.
- Recent Zigbee2MQTT warnings/errors.

Each finding includes:

- Severity.
- Code.
- Title.
- Message.
- Device, when available.
- Suggested action.
- Confidence level.

## Phase 3: AI reports

AI is planned as an explanation layer, not as the only diagnostic engine.

The AI should receive a compact payload like:

```json
{
  "summary": {
    "status": "warning",
    "health_score": 76,
    "device_count": 42,
    "problem_count": 3
  },
  "problems": [
    {
      "severity": "warning",
      "code": "device_offline",
      "title": "Device offline",
      "message": "sensor_hall is reported as offline by Zigbee2MQTT.",
      "suggested_action": "Check battery and nearby routers before re-pairing."
    }
  ]
}
```

The AI report should answer:

- What happened?
- How serious is it?
- What is the most likely cause?
- What should the user check first?
- What should the user avoid doing too early?

The report must be honest about uncertainty. Zigbee radio diagnosis is not exact without deeper radio-level tools.

## Phase 4: Smart notifications

Notifications should be meaningful and sparse.

Good notifications:

- Bridge offline.
- Powered router offline.
- Several devices offline at once.
- Repeated device leave events.
- Excessive Zigbee2MQTT errors.

Bad notifications:

- Every small LQI change.
- Every sleeping battery device that has not spoken for a few minutes.
- Repeated alerts with no new information.

## Phase 5: Advanced dashboard

The panel should remain simple by default.

Future advanced views may include:

- Timeline of events.
- Router dependency view.
- Network map integration.
- Trends by device.
- AI-generated action plan.

## Design rules

1. Explain first, expose raw data second.
2. Avoid Zigbee jargon unless it helps the user decide.
3. Never pretend a single metric proves the cause.
4. Prefer actionable guidance over beautiful but confusing charts.
5. Keep the default UI useful for non-technical users.
