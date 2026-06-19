"""Coordinator for Zigbee Doctor."""

from __future__ import annotations

from collections import deque
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
    DEFAULT_ACTIVE_TIMEOUT_MINUTES,
    DEFAULT_BASE_TOPIC,
    DEFAULT_LOW_BATTERY_THRESHOLD,
    DEFAULT_PASSIVE_TIMEOUT_HOURS,
    DOMAIN,
)
from .diagnostics import build_diagnostics
from .mqtt_client import ZigbeeDoctorMqttClient

_LOGGER = logging.getLogger(__name__)


class ZigbeeDoctorCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Collect Zigbee2MQTT data and expose a diagnostic snapshot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self.entry = entry
        self.options = {**entry.data, **entry.options}
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

        self._mqtt = ZigbeeDoctorMqttClient(
            hass=hass,
            base_topic=self.base_topic,
            message_callback=self.async_handle_mqtt_message,
        )

    async def async_setup(self) -> None:
        """Set up MQTT subscriptions."""
        await self._mqtt.async_subscribe()
        self._publish_snapshot()

    async def async_shutdown(self) -> None:
        """Shutdown MQTT subscriptions."""
        await self._mqtt.async_unsubscribe()

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
        snapshot = build_diagnostics(
            bridge_state=self.bridge_state,
            bridge_health=self.bridge_health,
            devices=self.devices,
            availability=self.availability,
            device_states=self.device_states,
            recent_logs=list(self.recent_logs),
            low_battery_threshold=self.low_battery_threshold,
            passive_timeout_hours=self.passive_timeout_hours,
            active_timeout_minutes=self.active_timeout_minutes,
        )
        snapshot["last_mqtt_message_at"] = (
            self.last_mqtt_message_at.isoformat() if self.last_mqtt_message_at else None
        )
        snapshot["recent_logs"] = list(self.recent_logs)
        snapshot["recent_events"] = list(self.recent_events)
        self.async_set_updated_data(snapshot)

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
            "problems": data.get("problems", []),
            "offline_devices": data.get("offline_devices", []),
            "low_battery_devices": data.get("low_battery_devices", []),
            "stale_devices": data.get("stale_devices", []),
            "recent_warning_logs": data.get("recent_warning_logs", []),
            "bridge_state": data.get("bridge_state", "unknown"),
            "updated_at": data.get("updated_at"),
        }

    def build_plain_text_report(self, language: str = "en") -> str:
        """Build a simple non-AI report for Phase 1 and Phase 2."""
        payload = self.get_report_payload()
        summary = payload.get("summary", {})
        problems = payload.get("problems", [])

        if language.startswith("es"):
            lines = [
                "Informe de Zigbee Doctor",
                "",
                f"Estado: {summary.get('status', 'unknown')}",
                f"Puntuación orientativa: {summary.get('health_score', 0)}/100",
                f"Dispositivos: {summary.get('device_count', 0)}",
                f"Problemas detectados: {summary.get('problem_count', 0)}",
                "",
                "Problemas principales:",
            ]
            for problem in problems[:5]:
                lines.append(f"- {problem.get('title')}: {problem.get('message')}")
                if problem.get("suggested_action"):
                    lines.append(f"  Acción sugerida: {problem['suggested_action']}")
            return "\n".join(lines)

        lines = [
            "Zigbee Doctor report",
            "",
            f"Status: {summary.get('status', 'unknown')}",
            f"Indicative score: {summary.get('health_score', 0)}/100",
            f"Devices: {summary.get('device_count', 0)}",
            f"Problems found: {summary.get('problem_count', 0)}",
            "",
            "Main findings:",
        ]
        for problem in problems[:5]:
            lines.append(f"- {problem.get('title')}: {problem.get('message')}")
            if problem.get("suggested_action"):
                lines.append(f"  Suggested action: {problem['suggested_action']}")
        return "\n".join(lines)
