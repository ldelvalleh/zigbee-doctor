"""Coordinator for Zigbee Doctor."""

from __future__ import annotations

from collections import deque
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ACTIVE_TIMEOUT_MINUTES,
    CONF_BASE_TOPIC,
    CONF_LOW_BATTERY_THRESHOLD,
    CONF_PASSIVE_TIMEOUT_HOURS,
    CONF_SOURCE,
    DEFAULT_ACTIVE_TIMEOUT_MINUTES,
    DEFAULT_BASE_TOPIC,
    DEFAULT_LOW_BATTERY_THRESHOLD,
    DEFAULT_PASSIVE_TIMEOUT_HOURS,
    DEFAULT_SOURCE,
    DOMAIN,
    SOURCE_ZHA,
    ZHA_POLL_SECONDS,
)
from .collectors import build_z2m_snapshot, build_zha_snapshot
from .diagnostics import analyze
from .mqtt_client import ZigbeeDoctorMqttClient

_LOGGER = logging.getLogger(__name__)


class ZigbeeDoctorCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Collect Zigbee2MQTT data and expose a diagnostic snapshot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        options = {**entry.data, **entry.options}
        self.source: str = options.get(CONF_SOURCE, DEFAULT_SOURCE)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # ZHA has no push channel, so we poll its gateway on an interval.
            update_interval=(
                timedelta(seconds=ZHA_POLL_SECONDS) if self.source == SOURCE_ZHA else None
            ),
        )
        self.entry = entry
        self.options = options
        self.base_topic: str = self.options.get(CONF_BASE_TOPIC, DEFAULT_BASE_TOPIC)
        self.low_battery_threshold: int = self.options.get(
            CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD
        )
        self.passive_timeout_hours: int = self.options.get(
            CONF_PASSIVE_TIMEOUT_HOURS, DEFAULT_PASSIVE_TIMEOUT_HOURS
        )
        self.active_timeout_minutes: int = self.options.get(
            CONF_ACTIVE_TIMEOUT_MINUTES, DEFAULT_ACTIVE_TIMEOUT_MINUTES
        )

        self.bridge_state: str = "unknown"
        self.bridge_health: dict[str, Any] = {}
        self.devices: dict[str, dict[str, Any]] = {}
        self.availability: dict[str, Any] = {}
        self.device_states: dict[str, dict[str, Any]] = {}
        self.recent_logs: deque[dict[str, Any]] = deque(maxlen=80)
        self.recent_events: deque[dict[str, Any]] = deque(maxlen=80)
        self.last_mqtt_message_at = None

        self._mqtt: ZigbeeDoctorMqttClient | None = None
        if self.source != SOURCE_ZHA:
            self._mqtt = ZigbeeDoctorMqttClient(
                hass=hass,
                base_topic=self.base_topic,
                message_callback=self.async_handle_mqtt_message,
            )

    async def async_setup(self) -> None:
        """Start collecting data for the configured source."""
        if self.source == SOURCE_ZHA:
            await self.async_config_entry_first_refresh()
            return
        await self._mqtt.async_subscribe()
        self._publish_snapshot()

    async def async_shutdown(self) -> None:
        """Stop collecting data."""
        if self._mqtt is not None:
            await self._mqtt.async_unsubscribe()

    async def _async_update_data(self) -> dict[str, Any]:
        """Polling path (ZHA). Zigbee2MQTT is push-driven and never polls."""
        if self.source == SOURCE_ZHA:
            return self._build_zha_result()
        return self.data or {}

    @callback
    def _build_zha_result(self) -> dict[str, Any]:
        """Read the ZHA gateway and run the diagnostics."""
        snapshot = build_zha_snapshot(self.hass)
        result = analyze(
            snapshot,
            low_battery_threshold=self.low_battery_threshold,
            passive_timeout_hours=self.passive_timeout_hours,
            active_timeout_minutes=self.active_timeout_minutes,
            language=self.hass.config.language,
        )
        result["last_mqtt_message_at"] = None
        result["recent_logs"] = []
        result["recent_events"] = []
        return result

    async def async_refresh_now(self) -> None:
        """Force a fresh snapshot for the 'Analyze now' service."""
        if self.source == SOURCE_ZHA:
            await self.async_request_refresh()
        else:
            self._publish_snapshot()

    async def async_handle_mqtt_message(self, topic: str, payload: Any) -> None:
        """Process a Zigbee2MQTT MQTT message."""
        self.last_mqtt_message_at = dt_util.utcnow()
        relative_topic = topic.removeprefix(f"{self.base_topic}/")

        if relative_topic == "bridge/state":
            self.bridge_state = self._parse_bridge_state(payload)
        elif relative_topic == "bridge/health" and isinstance(payload, dict):
            self.bridge_health = payload
        elif relative_topic == "bridge/devices" and isinstance(payload, list):
            self.devices = self._parse_devices(payload)
        elif relative_topic == "bridge/logging":
            self._append_log(payload)
        elif relative_topic == "bridge/event":
            self._append_event(payload)
        elif relative_topic.endswith("/availability"):
            device_name = relative_topic[: -len("/availability")]
            self.availability[device_name] = payload
        elif "/" not in relative_topic and isinstance(payload, dict):
            # Device state topics usually look like zigbee2mqtt/<friendly_name>.
            # Bridge topics are handled above and should not land here.
            if relative_topic != "bridge":
                self.device_states[relative_topic] = {
                    **self.device_states.get(relative_topic, {}),
                    **payload,
                }

        self._publish_snapshot()

    @callback
    def _publish_snapshot(self) -> None:
        """Rebuild diagnostics and notify listeners."""
        warning_logs = [
            log
            for log in list(self.recent_logs)[-20:]
            if str(log.get("level", "")).lower() in {"warning", "warn", "error"}
        ]
        snapshot = build_z2m_snapshot(
            bridge_state=self.bridge_state,
            bridge_health=self.bridge_health,
            devices=self.devices,
            availability=self.availability,
            device_states=self.device_states,
            recent_warning_logs=warning_logs,
        )
        result = analyze(
            snapshot,
            low_battery_threshold=self.low_battery_threshold,
            passive_timeout_hours=self.passive_timeout_hours,
            active_timeout_minutes=self.active_timeout_minutes,
            language=self.hass.config.language,
        )
        result["last_mqtt_message_at"] = (
            self.last_mqtt_message_at.isoformat() if self.last_mqtt_message_at else None
        )
        result["recent_logs"] = list(self.recent_logs)
        result["recent_events"] = list(self.recent_events)
        self.async_set_updated_data(result)

    @staticmethod
    def _parse_bridge_state(payload: Any) -> str:
        """Parse bridge state payload."""
        if isinstance(payload, dict):
            state = payload.get("state") or payload.get("status")
            return str(state or "unknown").lower()
        return str(payload or "unknown").lower()

    @staticmethod
    def _parse_devices(payload: list[Any]) -> dict[str, dict[str, Any]]:
        """Parse Zigbee2MQTT bridge/devices payload."""
        devices: dict[str, dict[str, Any]] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            friendly_name = item.get("friendly_name")
            if not isinstance(friendly_name, str):
                continue
            devices[friendly_name] = item
        return devices

    def _append_log(self, payload: Any) -> None:
        """Store a recent Zigbee2MQTT log message."""
        if isinstance(payload, dict):
            item = payload
        else:
            item = {"message": str(payload)}
        item["received_at"] = dt_util.utcnow().isoformat()
        self.recent_logs.append(item)

    def _append_event(self, payload: Any) -> None:
        """Store a recent Zigbee2MQTT event."""
        if isinstance(payload, dict):
            item = payload
        else:
            item = {"event": str(payload)}
        item["received_at"] = dt_util.utcnow().isoformat()
        self.recent_events.append(item)

    def get_report_payload(self) -> dict[str, Any]:
        """Return a compact payload prepared for future AI reporting."""
        data = self.data or {}
        return {
            "summary": data.get("summary", {}),
            "verdict": data.get("verdict", {}),
            "actions": data.get("actions", []),
            "problems": data.get("problems", []),
            "offline_devices": data.get("offline_devices", []),
            "low_battery_devices": data.get("low_battery_devices", []),
            "stale_devices": data.get("stale_devices", []),
            "bridge_state": data.get("bridge_state", "unknown"),
            "updated_at": data.get("updated_at"),
        }

    def build_plain_text_report(self, language: str | None = None) -> str:
        """Build a simple, plain-language report in the install language."""
        data = self.data or {}
        summary = data.get("summary", {})
        actions = [a for a in data.get("actions", []) if a.get("code") != "network_ok"]
        spanish = str(self.hass.config.language or "en").lower().startswith("es")

        if spanish:
            lines = [
                "Informe de Zigbee Doctor",
                "",
                summary.get("headline", ""),
                summary.get("subline", ""),
                "",
                f"Dispositivos funcionando: {summary.get('functioning_count', 0)}/{summary.get('device_count', 0)}",
                f"Sin conexión: {summary.get('offline_count', 0)} · Pila baja: {summary.get('low_battery_count', 0)}",
                "",
                "Qué hacer ahora:",
            ]
            empty = "Nada pendiente, tu red parece estable."
        else:
            lines = [
                "Zigbee Doctor report",
                "",
                summary.get("headline", ""),
                summary.get("subline", ""),
                "",
                f"Working devices: {summary.get('functioning_count', 0)}/{summary.get('device_count', 0)}",
                f"Offline: {summary.get('offline_count', 0)} · Low battery: {summary.get('low_battery_count', 0)}",
                "",
                "What to do now:",
            ]
            empty = "Nothing pending, your network looks stable."

        if not actions:
            lines.append(f"- {empty}")
        for action in actions[:6]:
            lines.append(f"- {action.get('title')}")
            if action.get("detail"):
                lines.append(f"  {action['detail']}")
        return "\n".join(lines)
