"""Source-agnostic network model for Zigbee Doctor.

Both Zigbee2MQTT and (later) ZHA collectors normalize their raw data into
these structures, so the diagnostic engine never depends on a specific
backend. Adding ZHA later means writing a new collector that fills a
``NetworkSnapshot`` -- the diagnostics and the panel do not change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeviceRole(str, Enum):
    """Normalized Zigbee device role."""

    COORDINATOR = "coordinator"
    ROUTER = "router"
    END_DEVICE = "end_device"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class DeviceModel:
    """A single Zigbee device, normalized across backends."""

    id: str
    name: str
    role: DeviceRole = DeviceRole.UNKNOWN
    available: bool | None = None
    battery: float | None = None
    battery_powered: bool | None = None
    lqi: int | None = None
    last_seen: datetime | None = None
    leave_count: int = 0
    address_changes: int = 0
    messages_per_sec: float | None = None
    model: str | None = None
    vendor: str | None = None

    @property
    def is_router(self) -> bool:
        """Return whether this device routes traffic for others."""
        return self.role == DeviceRole.ROUTER


@dataclass(slots=True)
class NetworkSnapshot:
    """A normalized snapshot of the whole Zigbee network."""

    source: str
    bridge_online: bool | None = None
    devices: list[DeviceModel] = field(default_factory=list)
    recent_warning_logs: list[dict] = field(default_factory=list)
    # Network/config info (filled by F3 config analysis; optional for now).
    channel: int | None = None
    log_level: str | None = None
    permit_join: bool | None = None
    version: str | None = None
    coordinator_type: str | None = None
