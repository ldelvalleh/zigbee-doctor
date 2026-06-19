"""Rule-based diagnostics for Zigbee Doctor."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .const import (
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    STATUS_CRITICAL,
    STATUS_OK,
    STATUS_WARNING,
)


@dataclass(slots=True)
class Problem:
    """A diagnostic problem found by Zigbee Doctor."""

    severity: str
    code: str
    title: str
    message: str
    device: str | None = None
    suggested_action: str | None = None
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""
        return asdict(self)


def parse_datetime(value: Any) -> datetime | None:
    """Parse common Zigbee2MQTT last_seen values."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.UTC)
    return parsed.astimezone(dt_util.UTC)


def _device_name(device: dict[str, Any]) -> str:
    """Return the best display name for a Zigbee2MQTT device."""
    friendly = device.get("friendly_name")
    if isinstance(friendly, str):
        return friendly
    definition = device.get("definition") or {}
    if isinstance(definition, dict) and definition.get("model"):
        return str(definition["model"])
    return str(device.get("ieee_address", "unknown"))


def _is_coordinator(device: dict[str, Any]) -> bool:
    """Return true if this device is the coordinator."""
    return str(device.get("type", "")).lower() == "coordinator"


def _is_router(device: dict[str, Any]) -> bool:
    """Return true if this device is a Zigbee router."""
    return str(device.get("type", "")).lower() == "router"


def _normalize_availability(value: Any) -> str:
    """Normalize Zigbee2MQTT availability payloads."""
    if isinstance(value, dict):
        state = value.get("state") or value.get("status")
        return str(state or "unknown").lower()
    return str(value or "unknown").lower()


def build_diagnostics(
    *,
    bridge_state: str,
    bridge_health: dict[str, Any],
    devices: dict[str, dict[str, Any]],
    availability: dict[str, Any],
    device_states: dict[str, dict[str, Any]],
    recent_logs: list[dict[str, Any]],
    low_battery_threshold: int,
    passive_timeout_hours: int,
    active_timeout_minutes: int,
) -> dict[str, Any]:
    """Build a complete diagnostic snapshot."""
    now = dt_util.utcnow()
    problems: list[Problem] = []

    known_devices = {
        name: device for name, device in devices.items() if not _is_coordinator(device)
    }
    routers = [name for name, device in known_devices.items() if _is_router(device)]

    if bridge_state == "offline":
        problems.append(
            Problem(
                severity=SEVERITY_CRITICAL,
                code="bridge_offline",
                title="Zigbee2MQTT bridge is offline",
                message="Zigbee2MQTT reports that the bridge is offline.",
                suggested_action="Check the Zigbee2MQTT add-on, MQTT broker and coordinator connection first.",
                confidence="high",
            )
        )
    elif bridge_state in {"unknown", ""}:
        problems.append(
            Problem(
                severity=SEVERITY_WARNING,
                code="bridge_unknown",
                title="Zigbee2MQTT bridge state is unknown",
                message="Zigbee Doctor has not received a clear bridge state yet.",
                suggested_action="Make sure Home Assistant MQTT and Zigbee2MQTT use the same broker and base topic.",
                confidence="medium",
            )
        )

    offline_devices: list[str] = []
    for name in sorted(known_devices):
        state = _normalize_availability(availability.get(name))
        if state == "offline":
            offline_devices.append(name)
            device = known_devices[name]
            severity = SEVERITY_CRITICAL if _is_router(device) else SEVERITY_WARNING
            problems.append(
                Problem(
                    severity=severity,
                    code="device_offline",
                    title="Device offline",
                    message=f"{name} is reported as offline by Zigbee2MQTT.",
                    device=name,
                    suggested_action=(
                        "If it is a powered router, check power first. If it is a battery device, check battery and wake it up before re-pairing."
                    ),
                    confidence="high",
                )
            )

    low_battery_devices: list[str] = []
    stale_devices: list[str] = []

    for name, state in device_states.items():
        battery = state.get("battery")
        if isinstance(battery, (int, float)) and battery <= low_battery_threshold:
            low_battery_devices.append(name)
            problems.append(
                Problem(
                    severity=SEVERITY_WARNING,
                    code="low_battery",
                    title="Low battery",
                    message=f"{name} battery is at {battery}%.",
                    device=name,
                    suggested_action="Replace or recharge the battery before investigating deeper network problems.",
                    confidence="high",
                )
            )

        last_seen = parse_datetime(state.get("last_seen"))
        if last_seen is None:
            continue

        device_type = str(known_devices.get(name, {}).get("type", "")).lower()
        timeout = (
            timedelta(minutes=active_timeout_minutes)
            if device_type == "router"
            else timedelta(hours=passive_timeout_hours)
        )
        if now - last_seen > timeout:
            stale_devices.append(name)
            problems.append(
                Problem(
                    severity=SEVERITY_WARNING,
                    code="stale_last_seen",
                    title="Device has not reported recently",
                    message=f"{name} has not reported since {last_seen.isoformat()}.",
                    device=name,
                    suggested_action="Do not re-pair immediately. First check battery, distance and nearby Zigbee routers.",
                    confidence="medium",
                )
            )

    health_devices = bridge_health.get("devices")
    if isinstance(health_devices, dict):
        for name, health in health_devices.items():
            if not isinstance(health, dict):
                continue

            leave_count = health.get("leave_count", 0) or 0
            if isinstance(leave_count, (int, float)) and leave_count > 0:
                problems.append(
                    Problem(
                        severity=SEVERITY_WARNING,
                        code="device_left_network",
                        title="Device left the network",
                        message=f"{name} has left the Zigbee network {int(leave_count)} time(s) during the current health window.",
                        device=name,
                        suggested_action="Check power stability, battery and signal path before re-pairing.",
                        confidence="medium",
                    )
                )

            address_changes = health.get("network_address_changes", 0) or 0
            if isinstance(address_changes, (int, float)) and address_changes > 0:
                problems.append(
                    Problem(
                        severity=SEVERITY_WARNING,
                        code="network_address_changes",
                        title="Network address changed",
                        message=f"{name} changed Zigbee network address {int(address_changes)} time(s).",
                        device=name,
                        suggested_action="This can indicate instability. Watch this device and nearby routers.",
                        confidence="low",
                    )
                )

            messages_per_sec = health.get("messages_per_sec", 0) or 0
            if isinstance(messages_per_sec, (int, float)) and messages_per_sec >= 1:
                problems.append(
                    Problem(
                        severity=SEVERITY_WARNING,
                        code="chatty_device",
                        title="Very chatty device",
                        message=f"{name} is publishing {messages_per_sec:.2f} messages per second.",
                        device=name,
                        suggested_action="Review reporting settings or firmware. A noisy device can make the network feel unstable.",
                        confidence="medium",
                    )
                )

    warning_logs = []
    for log in recent_logs[-20:]:
        level = str(log.get("level", "")).lower()
        if level in {"warning", "warn", "error"}:
            warning_logs.append(log)

    if warning_logs:
        problems.append(
            Problem(
                severity=SEVERITY_WARNING,
                code="recent_z2m_warnings",
                title="Recent Zigbee2MQTT warnings or errors",
                message=f"There are {len(warning_logs)} recent warning/error log entries from Zigbee2MQTT.",
                suggested_action="Open Zigbee2MQTT logs and look for repeated device names or radio errors.",
                confidence="medium",
            )
        )

    critical_count = sum(1 for problem in problems if problem.severity == SEVERITY_CRITICAL)
    warning_count = sum(1 for problem in problems if problem.severity == SEVERITY_WARNING)

    if critical_count:
        status = STATUS_CRITICAL
    elif warning_count:
        status = STATUS_WARNING
    else:
        status = STATUS_OK

    health_score = max(0, 100 - critical_count * 25 - warning_count * 8)

    summary = {
        "status": status,
        "health_score": health_score,
        "device_count": len(known_devices),
        "router_count": len(routers),
        "offline_count": len(offline_devices),
        "low_battery_count": len(low_battery_devices),
        "stale_count": len(stale_devices),
        "problem_count": len(problems),
        "critical_count": critical_count,
        "warning_count": warning_count,
    }

    if not problems:
        problems.append(
            Problem(
                severity=SEVERITY_INFO,
                code="network_ok",
                title="No obvious problems detected",
                message="Zigbee Doctor has not detected major problems with the currently available data.",
                suggested_action="Keep collecting data. Zigbee diagnostics become more useful with history.",
                confidence="medium",
            )
        )

    return {
        "summary": summary,
        "problems": [problem.to_dict() for problem in problems],
        "offline_devices": offline_devices,
        "low_battery_devices": low_battery_devices,
        "stale_devices": stale_devices,
        "routers": routers,
        "recent_warning_logs": warning_logs,
        "bridge_state": bridge_state,
        "bridge_health": bridge_health,
        "updated_at": now.isoformat(),
    }
