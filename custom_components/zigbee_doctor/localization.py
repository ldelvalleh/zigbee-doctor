"""Localized text for Zigbee Doctor findings.

The diagnostic engine emits a stable ``code`` plus parameters. This module is
the single source of truth that turns a code into human text in the language
of the Home Assistant install (Spanish when the install is in Spanish, English
otherwise). Both the panel and the plain-text report read from here.
"""

from __future__ import annotations

from typing import Any


def normalize_lang(language: str | None) -> str:
    """Return ``es`` for Spanish installs, ``en`` for everything else."""
    return "es" if str(language or "en").lower().startswith("es") else "en"


# Each code carries, per language:
#   title      short label for a single finding (report + problems list)
#   msg        per-device line, may use {name} and extra params
#   detail     plain explanation + what to do (shared by group and single)
#   group_one  headline when exactly one device is affected (may use {name})
#   group_many headline when several are affected (uses {count})
# "learn" links to a glossary concept (used by the "Aprende" tab in F2).
CODES: dict[str, dict[str, Any]] = {
    "bridge_offline": {
        "severity": "critical",
        "learn": "coordinator",
        "es": {
            "title": "El puente Zigbee2MQTT está caído",
            "msg": "Zigbee2MQTT informa de que el puente está caído.",
            "detail": "Tu sistema Zigbee no funciona ahora mismo. Revisa el complemento Zigbee2MQTT, el broker MQTT y la conexión del coordinador.",
            "group_one": "El puente Zigbee2MQTT está caído",
        },
        "en": {
            "title": "The Zigbee2MQTT bridge is down",
            "msg": "Zigbee2MQTT reports that the bridge is down.",
            "detail": "Your Zigbee system is not running right now. Check the Zigbee2MQTT add-on, the MQTT broker and the coordinator connection.",
            "group_one": "The Zigbee2MQTT bridge is down",
        },
    },
    "bridge_unknown": {
        "severity": "warning",
        "learn": "coordinator",
        "es": {
            "title": "Aún no recibo el estado del puente",
            "msg": "Zigbee Doctor todavía no tiene un estado claro del puente.",
            "detail": "Asegúrate de que Home Assistant y Zigbee2MQTT usan el mismo broker MQTT y el mismo topic base.",
            "group_one": "Aún no recibo el estado del puente",
        },
        "en": {
            "title": "No bridge state received yet",
            "msg": "Zigbee Doctor has not received a clear bridge state yet.",
            "detail": "Make sure Home Assistant and Zigbee2MQTT use the same MQTT broker and base topic.",
            "group_one": "No bridge state received yet",
        },
    },
    "router_offline": {
        "severity": "critical",
        "learn": "repeater",
        "es": {
            "title": "Repetidor sin conexión",
            "msg": "{name} (repetidor) aparece sin conexión.",
            "detail": "Un repetidor enchufado hace de antena para los demás aparatos. Comprueba que tiene corriente. Mientras esté caído, los dispositivos cercanos pueden fallar.",
            "group_one": "El repetidor «{name}» está sin conexión",
            "group_many": "{count} repetidores sin conexión",
        },
        "en": {
            "title": "Repeater offline",
            "msg": "{name} (repeater) is reported as offline.",
            "detail": "A mains-powered repeater acts as an antenna for other devices. Check that it has power. While it is down, nearby devices may fail.",
            "group_one": "Repeater «{name}» is offline",
            "group_many": "{count} repeaters offline",
        },
    },
    "device_offline": {
        "severity": "warning",
        "learn": "availability",
        "es": {
            "title": "Dispositivo sin conexión",
            "msg": "{name} aparece sin conexión.",
            "detail": "No corras a re-emparejar. Si funcionan con pila, cámbiala y acércalos a un repetidor. Si van enchufados, comprueba primero la corriente.",
            "group_one": "1 dispositivo sin conexión: {name}",
            "group_many": "{count} dispositivos sin conexión",
        },
        "en": {
            "title": "Device offline",
            "msg": "{name} is reported as offline.",
            "detail": "Don't rush to re-pair. If they are battery devices, change the battery and move them closer to a repeater. If mains-powered, check power first.",
            "group_one": "1 device offline: {name}",
            "group_many": "{count} devices offline",
        },
    },
    "low_battery": {
        "severity": "warning",
        "learn": "battery",
        "es": {
            "title": "Pila baja",
            "msg": "{name} tiene la pila al {battery}%.",
            "detail": "Cambia o recarga la pila antes de investigar otros problemas de red. Una pila baja provoca fallos que parecen de cobertura.",
            "group_one": "1 dispositivo con la pila baja: {name}",
            "group_many": "{count} dispositivos con la pila baja",
        },
        "en": {
            "title": "Low battery",
            "msg": "{name} battery is at {battery}%.",
            "detail": "Replace or recharge the battery before investigating other network problems. A low battery causes failures that look like coverage issues.",
            "group_one": "1 device with low battery: {name}",
            "group_many": "{count} devices with low battery",
        },
    },
    "stale_last_seen": {
        "severity": "warning",
        "learn": "availability",
        "es": {
            "title": "Lleva tiempo sin reportar",
            "msg": "{name} no reporta desde hace un tiempo.",
            "detail": "No lo re-emparejes a la primera. Mira la pila, la distancia y los repetidores cercanos.",
            "group_one": "1 dispositivo lleva tiempo sin reportar: {name}",
            "group_many": "{count} dispositivos llevan tiempo sin reportar",
        },
        "en": {
            "title": "Has not reported recently",
            "msg": "{name} has not reported for a while.",
            "detail": "Don't re-pair right away. Check the battery, distance and nearby repeaters.",
            "group_one": "1 device hasn't reported in a while: {name}",
            "group_many": "{count} devices haven't reported in a while",
        },
    },
    "device_left_network": {
        "severity": "warning",
        "learn": "repeater",
        "es": {
            "title": "Salió de la red",
            "msg": "{name} ha salido de la red Zigbee {count} vez(ces).",
            "detail": "Revisa la estabilidad de la corriente, la pila y el camino de señal antes de re-emparejar.",
            "group_one": "1 dispositivo ha salido de la red: {name}",
            "group_many": "{count} dispositivos han salido de la red",
        },
        "en": {
            "title": "Left the network",
            "msg": "{name} left the Zigbee network {count} time(s).",
            "detail": "Check power stability, battery and the signal path before re-pairing.",
            "group_one": "1 device left the network: {name}",
            "group_many": "{count} devices left the network",
        },
    },
    "network_address_changes": {
        "severity": "warning",
        "confidence": "low",
        "learn": "repeater",
        "es": {
            "title": "Cambia de dirección a menudo",
            "msg": "{name} ha cambiado de dirección de red {count} vez(ces).",
            "detail": "Puede indicar inestabilidad, aunque por sí solo no es concluyente. Vigila estos aparatos y los repetidores cercanos.",
            "group_one": "1 dispositivo cambia de dirección a menudo: {name}",
            "group_many": "{count} dispositivos cambian de dirección a menudo",
        },
        "en": {
            "title": "Changes address often",
            "msg": "{name} changed its network address {count} time(s).",
            "detail": "It can hint at instability, though on its own it isn't conclusive. Keep an eye on these devices and nearby repeaters.",
            "group_one": "1 device changes address often: {name}",
            "group_many": "{count} devices change address often",
        },
    },
    "chatty_device": {
        "severity": "warning",
        "learn": "chatty",
        "es": {
            "title": "Envía demasiados mensajes",
            "msg": "{name} envía {rate} mensajes por segundo.",
            "detail": "Un aparato muy ruidoso puede hacer que la red parezca inestable. Revisa sus ajustes de reporte o su firmware.",
            "group_one": "1 dispositivo envía demasiados mensajes: {name}",
            "group_many": "{count} dispositivos envían demasiados mensajes",
        },
        "en": {
            "title": "Sends too many messages",
            "msg": "{name} is sending {rate} messages per second.",
            "detail": "A very noisy device can make the network feel unstable. Review its reporting settings or firmware.",
            "group_one": "1 device sends too many messages: {name}",
            "group_many": "{count} devices send too many messages",
        },
    },
    "recent_z2m_warnings": {
        "severity": "warning",
        "learn": None,
        "es": {
            "title": "Avisos o errores recientes en Zigbee2MQTT",
            "msg": "Hay {count} avisos o errores recientes en los registros de Zigbee2MQTT.",
            "detail": "Abre los registros de Zigbee2MQTT y busca nombres de dispositivo repetidos o errores de radio.",
            "group_one": "Avisos o errores recientes en Zigbee2MQTT",
        },
        "en": {
            "title": "Recent Zigbee2MQTT warnings or errors",
            "msg": "There are {count} recent warning or error log entries in Zigbee2MQTT.",
            "detail": "Open the Zigbee2MQTT logs and look for repeated device names or radio errors.",
            "group_one": "Recent Zigbee2MQTT warnings or errors",
        },
    },
    "network_ok": {
        "severity": "info",
        "learn": None,
        "es": {
            "title": "No veo problemas importantes",
            "msg": "Tu red parece estable con los datos disponibles.",
            "detail": "Cuanto más tiempo recoja datos Zigbee Doctor, más útil será el diagnóstico.",
            "group_one": "No veo problemas importantes",
        },
        "en": {
            "title": "No major problems detected",
            "msg": "Your network looks stable with the data available.",
            "detail": "The longer Zigbee Doctor collects data, the more useful the diagnosis becomes.",
            "group_one": "No major problems detected",
        },
    },
}


_VERDICT_HEADLINE = {
    "es": {
        "critical": "Tu red Zigbee necesita atención",
        "warning": "Tu red funciona, con algún aviso por revisar",
        "ok": "Tu red Zigbee está sana",
        "unknown": "Esperando datos de tu red",
    },
    "en": {
        "critical": "Your Zigbee network needs attention",
        "warning": "Your network works, with a few things to review",
        "ok": "Your Zigbee network is healthy",
        "unknown": "Waiting for network data",
    },
}


def _loc(code: str, lang: str) -> dict[str, str]:
    spec = CODES.get(code, {})
    return spec.get(lang) or spec.get("en") or {}


def _safe_format(template: str, **params: Any) -> str:
    try:
        return template.format(**params)
    except (KeyError, IndexError, ValueError):
        return template


def render_problem(code: str, lang: str, *, name: str | None = None, **params: Any) -> dict[str, Any]:
    """Render a single finding (used by the problems list and the report)."""
    loc = _loc(code, lang)
    message = _safe_format(loc.get("msg", ""), name=name or "", **params).strip()
    return {
        "title": loc.get("title", code),
        "message": message,
        "suggested_action": loc.get("detail", ""),
        "learn": CODES.get(code, {}).get("learn"),
    }


def render_group(code: str, lang: str, devices: list[str], **params: Any) -> dict[str, Any]:
    """Render a grouped action card for the Resumen view."""
    loc = _loc(code, lang)
    count = len(devices) if devices else int(params.get("count", 1) or 1)
    first = devices[0] if devices else ""
    template = (
        loc.get("group_one", loc.get("title", code))
        if count <= 1
        else loc.get("group_many", loc.get("title", code))
    )
    # The group {count} (number of devices) overrides any per-device count param.
    title = _safe_format(template, **{**params, "name": first, "count": count})
    return {
        "code": code,
        "title": title,
        "detail": loc.get("detail", ""),
        "learn": CODES.get(code, {}).get("learn"),
        "devices": devices,
        "count": count,
    }


def render_verdict(
    status: str,
    lang: str,
    *,
    ok_count: int,
    total: int,
    top_title: str | None = None,
) -> dict[str, str]:
    """Return the plain-language headline and subline for the status banner."""
    headline = _VERDICT_HEADLINE.get(lang, _VERDICT_HEADLINE["en"]).get(
        status, _VERDICT_HEADLINE.get(lang, _VERDICT_HEADLINE["en"])["unknown"]
    )

    if status == "unknown" or total == 0:
        subline = (
            "Aún no hay datos suficientes. Revisa que Zigbee2MQTT esté publicando disponibilidad y estado."
            if lang == "es"
            else "Not enough data yet. Check that Zigbee2MQTT is publishing availability and state."
        )
        return {"headline": headline, "subline": subline}

    if lang == "es":
        subline = f"{ok_count} de {total} dispositivos funcionan."
        if status == "ok":
            subline += " Todo en orden."
        elif top_title:
            subline += f" Empieza por: {top_title}."
    else:
        subline = f"{ok_count} of {total} devices are working."
        if status == "ok":
            subline += " All good."
        elif top_title:
            subline += f" Start with: {top_title}."

    return {"headline": headline, "subline": subline}
