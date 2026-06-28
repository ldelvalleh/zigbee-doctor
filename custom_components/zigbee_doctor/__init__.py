"""Zigbee Doctor integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import frontend, panel_custom, persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_ENABLE_PANEL,
    DEFAULT_ENABLE_PANEL,
    DOMAIN,
    NAME,
    PANEL_FILE_NAME,
    PANEL_STATIC_PATH,
    PANEL_URL_PATH,
    PANEL_VERSION,
    PLATFORMS,
    SERVICE_ANALYZE_NOW,
    SERVICE_GENERATE_REPORT,
)
from .coordinator import ZigbeeDoctorCoordinator

_LOGGER = logging.getLogger(__name__)


def _entry_option(entry: ConfigEntry, key: str, default):
    """Return config entry option with data fallback."""
    return entry.options.get(key, entry.data.get(key, default))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zigbee Doctor from a config entry."""
    coordinator = ZigbeeDoctorCoordinator(hass, entry)
    await coordinator.async_setup()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if _entry_option(entry, CONF_ENABLE_PANEL, DEFAULT_ENABLE_PANEL):
        await _async_register_panel(hass)

    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Zigbee Doctor config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    coordinator: ZigbeeDoctorCoordinator | None = hass.data.get(DOMAIN, {}).pop(
        entry.entry_id, None
    )
    if coordinator:
        await coordinator.async_shutdown()

    if not hass.data.get(DOMAIN):
        hass.data.pop(DOMAIN, None)
        _async_unregister_services(hass)
        _async_remove_panel(hass)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload Zigbee Doctor."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def _get_first_coordinator(hass: HomeAssistant) -> ZigbeeDoctorCoordinator:
    """Return the first configured coordinator."""
    coordinators = hass.data.get(DOMAIN, {})
    if not coordinators:
        raise HomeAssistantError("Zigbee Doctor is not configured")
    return next(iter(coordinators.values()))


def _async_register_services(hass: HomeAssistant) -> None:
    """Register integration services."""
    if hass.services.has_service(DOMAIN, SERVICE_ANALYZE_NOW):
        return

    async def analyze_now(call: ServiceCall) -> None:
        """Force a diagnostic snapshot refresh."""
        coordinator = _get_first_coordinator(hass)
        coordinator._publish_snapshot()  # noqa: SLF001 - intentional internal refresh

    async def generate_report(call: ServiceCall) -> None:
        """Generate a Phase 1/2 plain-text report."""
        coordinator = _get_first_coordinator(hass)
        language = str(call.data.get("language", hass.config.language or "en"))
        report = coordinator.build_plain_text_report(language=language)
        persistent_notification.async_create(
            hass,
            report,
            title=NAME,
            notification_id="zigbee_doctor_report",
        )

    hass.services.async_register(DOMAIN, SERVICE_ANALYZE_NOW, analyze_now)
    hass.services.async_register(DOMAIN, SERVICE_GENERATE_REPORT, generate_report)


def _async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister services."""
    for service in (SERVICE_ANALYZE_NOW, SERVICE_GENERATE_REPORT):
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)


async def _async_register_panel(hass: HomeAssistant) -> None:
    """Register the Zigbee Doctor sidebar panel."""
    frontend_dir = Path(__file__).parent / "frontend"

    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(PANEL_STATIC_PATH, str(frontend_dir), False)]
        )
    except Exception as err:  # pragma: no cover - compatibility fallback
        _LOGGER.debug("Falling back to legacy static path registration: %s", err)
        hass.http.register_static_path(PANEL_STATIC_PATH, str(frontend_dir), False)

    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name="zigbee-doctor-panel",
        sidebar_title=NAME,
        sidebar_icon="mdi:stethoscope",
        js_url=f"{PANEL_STATIC_PATH}/{PANEL_FILE_NAME}?v={PANEL_VERSION}",
        embed_iframe=False,
        require_admin=False,
        config_panel_domain=DOMAIN,
    )


def _async_remove_panel(hass: HomeAssistant) -> None:
    """Remove the Zigbee Doctor sidebar panel when possible."""
    remove_panel = getattr(frontend, "async_remove_panel", None)
    if remove_panel is not None:
        remove_panel(hass, PANEL_URL_PATH)
