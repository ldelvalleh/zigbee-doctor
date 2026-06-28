"""Collectors that turn raw backend data into a NetworkSnapshot.

Today only Zigbee2MQTT is implemented. A future ZHA collector lives here too
and produces the same :class:`NetworkSnapshot`, so nothing downstream changes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.util import dt as dt_util

from .models import DeviceModel, DeviceRole, NetworkSnapshot


def _parse_datetime(value: Any) -> datetime | None:
    """Parse common last_seen values into an aware UTC datetime."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.UTC)
    return parsed.astimezone(dt_util.UTC)


def _role(raw_type: Any) -> DeviceRole:
    """Map a Zigbee2MQTT device type to a normalized role."""
    value = str(raw_type or "").lower()
    if value == "coordinator":
        return DeviceRole.COORDINATOR
    if value == "router":
        return DeviceRole.ROUTER
    if value in {"enddevice", "end_device", "greenpower"}:
        return DeviceRole.END_DEVICE
    return DeviceRole.UNKNOWN


def _available(value: Any) -> bool | None:
    """Normalize a Zigbee2MQTT availability payload to a tri-state bool."""
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("state") or value.get("status")
    state = str(value or "").lower()
    if state == "online":
        return True
    if state == "offline":
        return False
    return None


def _battery_powered(power_source: Any) -> bool | None:
    """Return whether the device runs on battery, when known."""
    if power_source is None:
        return None
    return str(power_source).lower().startswith("battery")


def _number(value: Any) -> float | int | None:
    """Return value if it is a real number, else None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def build_z2m_snapshot(
    *,
    bridge_state: str,
    bridge_health: dict[str, Any],
    devices: dict[str, dict[str, Any]],
    availability: dict[str, Any],
    device_states: dict[str, dict[str, Any]],
    recent_warning_logs: list[dict[str, Any]],
) -> NetworkSnapshot:
    """Normalize raw Zigbee2MQTT data into a NetworkSnapshot."""
    health_by_ieee = bridge_health.get("devices") or {}
    if not isinstance(health_by_ieee, dict):
        health_by_ieee = {}

    models: list[DeviceModel] = []
    for name, raw in devices.items():
        if not isinstance(raw, dict):
            continue
        role = _role(raw.get("type"))
        if role == DeviceRole.COORDINATOR:
            continue

        ieee = str(raw.get("ieee_address") or name)
        state = device_states.get(name) or {}
        health = health_by_ieee.get(ieee) or {}
        if not isinstance(health, dict):
            health = {}
        definition = raw.get("definition") if isinstance(raw.get("definition"), dict) else {}

        models.append(
            DeviceModel(
                id=ieee,
                name=name,
                role=role,
                available=_available(availability.get(name)),
                battery=_number(state.get("battery")),
                battery_powered=_battery_powered(raw.get("power_source")),
                lqi=_number(state.get("linkquality")),
                last_seen=_parse_datetime(state.get("last_seen")),
                leave_count=int(_number(health.get("leave_count")) or 0),
                address_changes=int(_number(health.get("network_address_changes")) or 0),
                messages_per_sec=_number(health.get("messages_per_sec")),
                model=str(definition.get("model")) if definition.get("model") else None,
                vendor=str(definition.get("vendor")) if definition.get("vendor") else None,
            )
        )

    bridge_online: bool | None
    state = str(bridge_state or "").lower()
    if state == "online":
        bridge_online = True
    elif state == "offline":
        bridge_online = False
    else:
        bridge_online = None

    return NetworkSnapshot(
        source="zigbee2mqtt",
        bridge_online=bridge_online,
        devices=models,
        recent_warning_logs=recent_warning_logs,
    )
