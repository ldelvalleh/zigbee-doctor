"""Binary sensor platform for Zigbee Doctor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_CRITICAL, STATUS_WARNING
from .coordinator import ZigbeeDoctorCoordinator

ValueFn = Callable[[dict[str, Any]], bool]


@dataclass(frozen=True, kw_only=True)
class ZigbeeDoctorBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Description for a Zigbee Doctor binary sensor."""

    value_fn: ValueFn


BINARY_SENSORS: tuple[ZigbeeDoctorBinarySensorEntityDescription, ...] = (
    ZigbeeDoctorBinarySensorEntityDescription(
        key="problem_detected",
        translation_key="problem_detected",
        icon="mdi:alert-outline",
        value_fn=lambda data: data.get("summary", {}).get("status")
        in {STATUS_WARNING, STATUS_CRITICAL},
    ),
    ZigbeeDoctorBinarySensorEntityDescription(
        key="bridge_connected",
        translation_key="bridge_connected",
        icon="mdi:connection",
        value_fn=lambda data: data.get("bridge_state") == "online",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zigbee Doctor binary sensors."""
    coordinator: ZigbeeDoctorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZigbeeDoctorBinarySensor(coordinator, entry.entry_id, description)
        for description in BINARY_SENSORS
    )


class ZigbeeDoctorBinarySensor(
    CoordinatorEntity[ZigbeeDoctorCoordinator], BinarySensorEntity
):
    """A Zigbee Doctor binary sensor."""

    entity_description: ZigbeeDoctorBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZigbeeDoctorCoordinator,
        entry_id: str,
        description: ZigbeeDoctorBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes."""
        data = self.coordinator.data or {}
        return {
            "updated_at": data.get("updated_at"),
            "bridge_state": data.get("bridge_state"),
            "problem_count": data.get("summary", {}).get("problem_count", 0),
        }
