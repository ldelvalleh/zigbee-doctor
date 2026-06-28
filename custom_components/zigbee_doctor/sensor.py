"""Sensor platform for Zigbee Doctor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZigbeeDoctorCoordinator

ValueFn = Callable[[dict[str, Any]], Any]
AttrFn = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True, kw_only=True)
class ZigbeeDoctorSensorEntityDescription(SensorEntityDescription):
    """Description for a Zigbee Doctor sensor."""

    value_fn: ValueFn
    attr_fn: AttrFn | None = None


def _summary(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("summary", {}) if data else {}


def _problems_attr(data: dict[str, Any]) -> dict[str, Any]:
    problems = data.get("problems", []) if data else []
    return {"problems": problems[:10]}


def _status_attr(data: dict[str, Any]) -> dict[str, Any]:
    """Everything the panel needs to render the at-a-glance summary."""
    data = data or {}
    summary = data.get("summary", {})
    return {
        "problems": (data.get("problems", []) or [])[:10],
        "actions": data.get("actions", []),
        "headline": summary.get("headline"),
        "subline": summary.get("subline"),
        "summary": summary,
    }


def _devices_attr(data: dict[str, Any]) -> dict[str, Any]:
    """Full per-device list for the panel's Devices tab."""
    return {"devices": (data or {}).get("devices", [])}


def _device_list_attr(key: str) -> AttrFn:
    def _attr(data: dict[str, Any]) -> dict[str, Any]:
        return {key: data.get(key, []) if data else []}

    return _attr


SENSORS: tuple[ZigbeeDoctorSensorEntityDescription, ...] = (
    ZigbeeDoctorSensorEntityDescription(
        key="network_status",
        translation_key="network_status",
        icon="mdi:zigbee",
        value_fn=lambda data: _summary(data).get("status", "unknown"),
        attr_fn=_status_attr,
    ),
    ZigbeeDoctorSensorEntityDescription(
        key="health_score",
        translation_key="health_score",
        icon="mdi:heart-pulse",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: _summary(data).get("health_score", 0),
    ),
    ZigbeeDoctorSensorEntityDescription(
        key="device_count",
        translation_key="device_count",
        icon="mdi:devices",
        value_fn=lambda data: _summary(data).get("device_count", 0),
        attr_fn=_devices_attr,
    ),
    ZigbeeDoctorSensorEntityDescription(
        key="offline_devices",
        translation_key="offline_devices",
        icon="mdi:access-point-network-off",
        value_fn=lambda data: _summary(data).get("offline_count", 0),
        attr_fn=_device_list_attr("offline_devices"),
    ),
    ZigbeeDoctorSensorEntityDescription(
        key="problem_count",
        translation_key="problem_count",
        icon="mdi:alert-circle-outline",
        value_fn=lambda data: _summary(data).get("problem_count", 0),
        attr_fn=_problems_attr,
    ),
    ZigbeeDoctorSensorEntityDescription(
        key="low_battery_devices",
        translation_key="low_battery_devices",
        icon="mdi:battery-alert-variant-outline",
        value_fn=lambda data: _summary(data).get("low_battery_count", 0),
        attr_fn=_device_list_attr("low_battery_devices"),
    ),
    ZigbeeDoctorSensorEntityDescription(
        key="stale_devices",
        translation_key="stale_devices",
        icon="mdi:clock-alert-outline",
        value_fn=lambda data: _summary(data).get("stale_count", 0),
        attr_fn=_device_list_attr("stale_devices"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zigbee Doctor sensors."""
    coordinator: ZigbeeDoctorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZigbeeDoctorSensor(coordinator, entry.entry_id, description)
        for description in SENSORS
    )


class ZigbeeDoctorSensor(CoordinatorEntity[ZigbeeDoctorCoordinator], SensorEntity):
    """A Zigbee Doctor sensor."""

    entity_description: ZigbeeDoctorSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZigbeeDoctorCoordinator,
        entry_id: str,
        description: ZigbeeDoctorSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Zigbee Doctor",
            "manufacturer": "Zigbee Doctor",
            "model": "Zigbee2MQTT Diagnostics",
        }

    @property
    def native_value(self) -> Any:
        """Return the native value."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes."""
        data = self.coordinator.data or {}
        attributes = {
            "updated_at": data.get("updated_at"),
            "last_mqtt_message_at": data.get("last_mqtt_message_at"),
            "bridge_state": data.get("bridge_state"),
        }
        if self.entity_description.attr_fn:
            attributes.update(self.entity_description.attr_fn(data))
        return attributes
