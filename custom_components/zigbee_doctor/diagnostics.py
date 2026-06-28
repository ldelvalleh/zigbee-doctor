"""Rule-based diagnostics for Zigbee Doctor.

The engine works on a source-agnostic :class:`NetworkSnapshot`, so the same
rules apply to Zigbee2MQTT today and ZHA later. Findings are emitted as a
stable ``code`` plus parameters and rendered into the install language by
:mod:`.localization`.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from . import localization as loc
from .const import (
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    STATUS_CRITICAL,
    STATUS_OK,
    STATUS_WARNING,
)
from .models import DeviceModel, NetworkSnapshot

# Order in which grouped actions are shown (most actionable first).
_PRIORITY = [
    "bridge_offline",
    "router_offline",
    "device_offline",
    "low_battery",
    "device_left_network",
    "chatty_device",
    "stale_last_seen",
    "network_address_changes",
    "recent_z2m_warnings",
    "bridge_unknown",
    "network_ok",
]
_SEVERITY_RANK = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}


def _bridge_state_str(online: bool | None) -> str:
    if online is True:
        return "online"
    if online is False:
        return "offline"
    return "unknown"


def analyze(
    snapshot: NetworkSnapshot,
    *,
    low_battery_threshold: int,
    passive_timeout_hours: int,
    active_timeout_minutes: int,
    language: str | None = "en",
) -> dict[str, Any]:
    """Run all rules on a snapshot and return a localized result."""
    lang = loc.normalize_lang(language)
    now = dt_util.utcnow()
    devices = snapshot.devices

    # Each raw finding: (code, severity, device_name|None, params, confidence)
    raw: list[tuple[str, str, str | None, dict[str, Any], str]] = []

    if snapshot.bridge_online is False:
        raw.append(("bridge_offline", SEVERITY_CRITICAL, None, {}, "high"))
    elif snapshot.bridge_online is None and devices:
        raw.append(("bridge_unknown", SEVERITY_WARNING, None, {}, "medium"))

    offline_devices: list[str] = []
    low_battery_devices: list[str] = []
    stale_devices: list[str] = []

    for device in sorted(devices, key=lambda d: d.name.lower()):
        if device.available is False:
            offline_devices.append(device.name)
            if device.is_router:
                raw.append(("router_offline", SEVERITY_CRITICAL, device.name, {}, "high"))
            else:
                raw.append(("device_offline", SEVERITY_WARNING, device.name, {}, "high"))

        if device.battery is not None and device.battery <= low_battery_threshold:
            low_battery_devices.append(device.name)
            raw.append(
                ("low_battery", SEVERITY_WARNING, device.name, {"battery": _fmt_num(device.battery)}, "high")
            )

        if device.last_seen is not None:
            timeout = (
                timedelta(minutes=active_timeout_minutes)
                if device.is_router
                else timedelta(hours=passive_timeout_hours)
            )
            if now - device.last_seen > timeout:
                stale_devices.append(device.name)
                raw.append(("stale_last_seen", SEVERITY_WARNING, device.name, {}, "medium"))

        if device.leave_count > 0:
            raw.append(
                ("device_left_network", SEVERITY_WARNING, device.name, {"count": device.leave_count}, "medium")
            )

        if device.address_changes > 0:
            raw.append(
                (
                    "network_address_changes",
                    SEVERITY_WARNING,
                    device.name,
                    {"count": device.address_changes},
                    "low",
                )
            )

        if device.messages_per_sec is not None and device.messages_per_sec >= 1:
            raw.append(
                (
                    "chatty_device",
                    SEVERITY_WARNING,
                    device.name,
                    {"rate": f"{device.messages_per_sec:.1f}"},
                    "medium",
                )
            )

    if snapshot.recent_warning_logs:
        raw.append(
            ("recent_z2m_warnings", SEVERITY_WARNING, None, {"count": len(snapshot.recent_warning_logs)}, "medium")
        )

    critical_count = sum(1 for _, sev, *_ in raw if sev == SEVERITY_CRITICAL)
    warning_count = sum(1 for _, sev, *_ in raw if sev == SEVERITY_WARNING)

    total = len(devices)
    if total == 0:
        status = "unknown"
    elif critical_count:
        status = STATUS_CRITICAL
    elif warning_count:
        status = STATUS_WARNING
    else:
        status = STATUS_OK

    if not raw and total:
        raw.append(("network_ok", SEVERITY_INFO, None, {}, "medium"))

    problems = [
        {
            "severity": sev,
            "code": code,
            "device": name,
            "confidence": conf,
            **loc.render_problem(code, lang, name=name, **params),
        }
        for code, sev, name, params, conf in raw
    ]

    actions = _group_actions(raw, lang)
    functioning = max(0, total - len(offline_devices))
    top_title = actions[0]["title"] if (actions and status not in {"ok", "unknown"}) else None
    verdict = loc.render_verdict(status, lang, ok_count=functioning, total=total, top_title=top_title)

    health_score = max(0, 100 - critical_count * 25 - warning_count * 8)

    summary = {
        "status": status,
        "health_score": health_score,
        "device_count": total,
        "functioning_count": functioning,
        "router_count": sum(1 for d in devices if d.is_router),
        "offline_count": len(offline_devices),
        "low_battery_count": len(low_battery_devices),
        "stale_count": len(stale_devices),
        "problem_count": critical_count + warning_count,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "headline": verdict["headline"],
        "subline": verdict["subline"],
    }

    return {
        "summary": summary,
        "verdict": {**verdict, "status": status},
        "actions": actions,
        "problems": problems,
        "devices": _export_devices(devices, low_battery_threshold, set(stale_devices)),
        "offline_devices": offline_devices,
        "low_battery_devices": low_battery_devices,
        "stale_devices": stale_devices,
        "routers": [d.name for d in devices if d.is_router],
        "source": snapshot.source,
        "bridge_state": _bridge_state_str(snapshot.bridge_online),
        "updated_at": now.isoformat(),
    }


def _export_devices(
    devices: list[DeviceModel], low_battery_threshold: int, stale: set[str]
) -> list[dict[str, Any]]:
    """Flatten the normalized devices for the panel's Devices tab."""
    out: list[dict[str, Any]] = []
    for device in devices:
        if device.available is False:
            dev_status = "offline"
        elif device.battery is not None and device.battery <= low_battery_threshold:
            dev_status = "low_battery"
        elif device.name in stale:
            dev_status = "stale"
        elif device.available is True:
            dev_status = "ok"
        else:
            dev_status = "unknown"

        out.append(
            {
                "name": device.name,
                "role": device.role.value,
                "available": device.available,
                "battery": _fmt_num(device.battery) if device.battery is not None else None,
                "battery_powered": device.battery_powered,
                "lqi": device.lqi,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "status": dev_status,
            }
        )

    out.sort(key=lambda item: item["name"].lower())
    return out


def _group_actions(
    raw: list[tuple[str, str, str | None, dict[str, Any], str]], lang: str
) -> list[dict[str, Any]]:
    """Collapse per-device findings into one prioritized card per code."""
    by_code: dict[str, dict[str, Any]] = {}
    for code, severity, name, params, confidence in raw:
        bucket = by_code.setdefault(
            code, {"severity": severity, "devices": [], "params": {}, "confidence": confidence}
        )
        if name:
            bucket["devices"].append(name)
        if params:
            bucket["params"] = params

    actions: list[dict[str, Any]] = []
    for code, bucket in by_code.items():
        group = loc.render_group(code, lang, bucket["devices"], **bucket["params"])
        actions.append(
            {
                "severity": bucket["severity"],
                "confidence": bucket["confidence"],
                **group,
            }
        )

    actions.sort(
        key=lambda a: (
            _SEVERITY_RANK.get(a["severity"], 3),
            _PRIORITY.index(a["code"]) if a["code"] in _PRIORITY else len(_PRIORITY),
        )
    )
    return actions


def _fmt_num(value: float | int) -> Any:
    """Show integers without a trailing .0."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value
