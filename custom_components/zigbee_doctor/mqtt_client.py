"""MQTT helpers for Zigbee Doctor."""

from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)


class ZigbeeDoctorMqttClient:
    """Subscribe to Zigbee2MQTT topics and forward parsed payloads."""

    def __init__(self, hass: HomeAssistant, base_topic: str, message_callback) -> None:
        """Initialize the MQTT client wrapper."""
        self.hass = hass
        self.base_topic = base_topic.strip().strip("/")
        self._message_callback = message_callback
        self._unsubscribers = []

    async def async_subscribe(self) -> None:
        """Subscribe to Zigbee2MQTT topics."""
        topics = [
            f"{self.base_topic}/bridge/state",
            f"{self.base_topic}/bridge/health",
            f"{self.base_topic}/bridge/devices",
            f"{self.base_topic}/bridge/logging",
            f"{self.base_topic}/bridge/event",
            f"{self.base_topic}/+/availability",
            f"{self.base_topic}/+",
        ]

        for topic in topics:
            unsubscribe = await mqtt.async_subscribe(
                self.hass,
                topic,
                self._mqtt_message_received,
                qos=0,
                encoding="utf-8",
            )
            self._unsubscribers.append(unsubscribe)
            _LOGGER.debug("Subscribed to MQTT topic: %s", topic)

    async def async_unsubscribe(self) -> None:
        """Unsubscribe from all MQTT topics."""
        while self._unsubscribers:
            unsubscribe = self._unsubscribers.pop()
            unsubscribe()

    @callback
    def _mqtt_message_received(self, msg) -> None:
        """Handle incoming MQTT messages."""
        payload = self._parse_payload(msg.payload)
        result = self._message_callback(msg.topic, payload)
        if result is not None:
            self.hass.async_create_task(result)

    @staticmethod
    def _parse_payload(payload: Any) -> Any:
        """Parse MQTT payload into JSON when possible."""
        if payload is None:
            return None
        if not isinstance(payload, str):
            return payload

        text = payload.strip()
        if text == "":
            return ""

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
