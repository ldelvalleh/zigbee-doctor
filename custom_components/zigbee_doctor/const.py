"""Constants for Zigbee Doctor."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "zigbee_doctor"
NAME = "Zigbee Doctor"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

CONF_SOURCE = "source"
CONF_BASE_TOPIC = "base_topic"
CONF_ENABLE_PANEL = "enable_panel"
CONF_LOW_BATTERY_THRESHOLD = "low_battery_threshold"
CONF_PASSIVE_TIMEOUT_HOURS = "passive_timeout_hours"
CONF_ACTIVE_TIMEOUT_MINUTES = "active_timeout_minutes"

SOURCE_Z2M = "zigbee2mqtt"
SOURCE_ZHA = "zha"
SOURCES = [SOURCE_Z2M, SOURCE_ZHA]

DEFAULT_SOURCE = SOURCE_Z2M
DEFAULT_BASE_TOPIC = "zigbee2mqtt"
DEFAULT_ENABLE_PANEL = True
DEFAULT_LOW_BATTERY_THRESHOLD = 20
DEFAULT_PASSIVE_TIMEOUT_HOURS = 25
DEFAULT_ACTIVE_TIMEOUT_MINUTES = 10

# How often to poll the ZHA gateway (ZHA has no MQTT push to subscribe to).
ZHA_POLL_SECONDS = 60

PANEL_URL_PATH = "zigbee-doctor"
PANEL_STATIC_PATH = "/zigbee_doctor_static"
PANEL_FILE_NAME = "zigbee-doctor-panel.js"
# Bump on every frontend change to bust the browser cache for the panel JS.
PANEL_VERSION = "4"

SERVICE_ANALYZE_NOW = "analyze_now"
SERVICE_GENERATE_REPORT = "generate_report"

STATUS_OK = "ok"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"

SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_CRITICAL = "critical"
