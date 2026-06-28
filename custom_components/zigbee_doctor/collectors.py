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


# --- ZHA collector -------------------------------------------------------
#
# ZHA has no MQTT. Device data lives in the in-memory ZHA gateway. ZHA's
# internals change between Home Assistant versions, so every access here is
# defensive: if anything is missing we degrade to "unknown" instead of
# crashing. Names and battery come from the HA registries, which are stable.


def build_zha_snapshot(hass: Any) -> NetworkSnapshot:
    """Normalize the running ZHA gateway into a NetworkSnapshot."""
    gateway = _get_zha_gateway(hass)
    if gateway is None:
        return NetworkSnapshot(source="zha", bridge_online=None, devices=[])

    names = _zha_names(hass)
    batteries = _zha_batteries(hass)

    models: list[DeviceModel] = []
    coordinator_available: bool | None = None

    for dev in _zha_devices(gateway):
        try:
            ieee = str(_getattr(dev, "ieee", "") or "")
            if not ieee:
                continue
            role = _zha_role(dev)
            available = _bool_or_none(_getattr(dev, "available"))
            if role == DeviceRole.COORDINATOR:
                coordinator_available = available if available is not None else True
                continue

            mains = _zha_is_mains(dev)
            models.append(
                DeviceModel(
                    id=ieee,
                    name=names.get(ieee) or str(_getattr(dev, "name", ieee) or ieee),
                    role=role,
                    available=available,
                    battery=batteries.get(ieee),
                    battery_powered=None if mains is None else not mains,
                    lqi=_number(_getattr(dev, "lqi")),
                    last_seen=_zha_last_seen(_getattr(dev, "last_seen")),
                    model=_str_or_none(_getattr(dev, "model")),
                    vendor=_str_or_none(_getattr(dev, "manufacturer")),
                )
            )
        except Exception:  # noqa: BLE001 - one odd device must not break the snapshot
            continue

    if coordinator_available is not None:
        bridge_online: bool | None = coordinator_available
    else:
        bridge_online = True if models else None

    return NetworkSnapshot(source="zha", bridge_online=bridge_online, devices=models)


def _get_zha_gateway(hass: Any) -> Any:
    """Return the ZHA gateway object, or None if ZHA is not running."""
    try:
        from homeassistant.components.zha.helpers import get_zha_gateway
    except Exception:  # noqa: BLE001 - ZHA not installed
        return None
    try:
        return get_zha_gateway(hass)
    except Exception:  # noqa: BLE001 - ZHA not set up yet
        return None


def _zha_devices(gateway: Any) -> list[Any]:
    """Return the gateway's devices as a list, across ZHA versions."""
    devices = _getattr(gateway, "devices")
    if devices is None:
        return []
    try:
        return list(devices.values()) if isinstance(devices, dict) else list(devices)
    except Exception:  # noqa: BLE001
        return []


def _getattr(obj: Any, name: str, default: Any = None) -> Any:
    """getattr that also survives properties raising at read time."""
    try:
        return getattr(obj, name, default)
    except Exception:  # noqa: BLE001
        return default


def _zha_role(dev: Any) -> DeviceRole:
    """Best-effort device role from a ZHA device object."""
    raw = _getattr(dev, "device_type")
    text = str(_getattr(raw, "name", raw) or "").lower()
    if "coordinator" in text:
        return DeviceRole.COORDINATOR
    if "router" in text:
        return DeviceRole.ROUTER
    if "end" in text:
        return DeviceRole.END_DEVICE
    if _getattr(dev, "is_coordinator"):
        return DeviceRole.COORDINATOR
    if _getattr(dev, "is_router"):
        return DeviceRole.ROUTER
    if _getattr(dev, "is_end_device"):
        return DeviceRole.END_DEVICE
    return DeviceRole.UNKNOWN


def _zha_is_mains(dev: Any) -> bool | None:
    """Return whether the device is mains powered, when known."""
    value = _getattr(dev, "is_mains_powered")
    if isinstance(value, bool):
        return value
    power_source = str(_getattr(dev, "power_source", "") or "").lower()
    if "main" in power_source:
        return True
    if "battery" in power_source:
        return False
    return None


def _zha_last_seen(value: Any) -> datetime | None:
    """Parse ZHA last_seen (epoch float, datetime or string)."""
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, (int, float)):
        try:
            parsed = datetime.fromtimestamp(value, tz=dt_util.UTC)
        except (OSError, OverflowError, ValueError):
            return None
    elif isinstance(value, str):
        return _parse_datetime(value)
    else:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.UTC)
    return parsed.astimezone(dt_util.UTC)


def _ieee_from_identifiers(identifiers: Any) -> str | None:
    """Pull the ieee address out of a device registry identifiers set."""
    for identifier in identifiers or []:
        try:
            domain, ident = identifier
        except (ValueError, TypeError):
            continue
        if domain == "zha":
            return str(ident)
    return None


def _zha_names(hass: Any) -> dict[str, str]:
    """Map ieee -> friendly name from the device registry."""
    out: dict[str, str] = {}
    try:
        from homeassistant.helpers import device_registry as dr

        registry = dr.async_get(hass)
    except Exception:  # noqa: BLE001
        return out
    for device in registry.devices.values():
        ieee = _ieee_from_identifiers(device.identifiers)
        if not ieee:
            continue
        name = device.name_by_user or device.name
        if name:
            out[ieee] = name
    return out


def _zha_batteries(hass: Any) -> dict[str, float]:
    """Map ieee -> battery percent from ZHA battery sensors."""
    out: dict[str, float] = {}
    try:
        from homeassistant.helpers import device_registry as dr
        from homeassistant.helpers import entity_registry as er

        ent_reg = er.async_get(hass)
        dev_reg = dr.async_get(hass)
    except Exception:  # noqa: BLE001
        return out

    for entry in ent_reg.entities.values():
        if entry.platform != "zha" or entry.domain != "sensor" or not entry.device_id:
            continue
        device_class = entry.original_device_class or entry.device_class
        if device_class != "battery":
            continue
        device = dev_reg.async_get(entry.device_id)
        if not device:
            continue
        ieee = _ieee_from_identifiers(device.identifiers)
        if not ieee:
            continue
        state = hass.states.get(entry.entity_id)
        if not state:
            continue
        try:
            out[ieee] = float(state.state)
        except (TypeError, ValueError):
            continue
    return out


def _str_or_none(value: Any) -> str | None:
    """Return a non-empty string or None."""
    if value is None:
        return None
    text = str(value)
    return text or None


def _bool_or_none(value: Any) -> bool | None:
    """Return value only when it is an actual bool, else None (unknown)."""
    return value if isinstance(value, bool) else None
