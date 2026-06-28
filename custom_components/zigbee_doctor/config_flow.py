"""Config flow for Zigbee Doctor."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_ACTIVE_TIMEOUT_MINUTES,
    CONF_BASE_TOPIC,
    CONF_ENABLE_PANEL,
    CONF_LOW_BATTERY_THRESHOLD,
    CONF_PASSIVE_TIMEOUT_HOURS,
    CONF_SOURCE,
    DEFAULT_ACTIVE_TIMEOUT_MINUTES,
    DEFAULT_BASE_TOPIC,
    DEFAULT_ENABLE_PANEL,
    DEFAULT_LOW_BATTERY_THRESHOLD,
    DEFAULT_PASSIVE_TIMEOUT_HOURS,
    DEFAULT_SOURCE,
    DOMAIN,
    NAME,
    SOURCE_ZHA,
    SOURCES,
)


def _schema(user_input: dict | None = None) -> vol.Schema:
    """Return the config schema."""
    user_input = user_input or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_SOURCE,
                default=user_input.get(CONF_SOURCE, DEFAULT_SOURCE),
            ): vol.In(SOURCES),
            vol.Required(
                CONF_BASE_TOPIC,
                default=user_input.get(CONF_BASE_TOPIC, DEFAULT_BASE_TOPIC),
            ): str,
            vol.Optional(
                CONF_ENABLE_PANEL,
                default=user_input.get(CONF_ENABLE_PANEL, DEFAULT_ENABLE_PANEL),
            ): bool,
            vol.Optional(
                CONF_LOW_BATTERY_THRESHOLD,
                default=user_input.get(
                    CONF_LOW_BATTERY_THRESHOLD, DEFAULT_LOW_BATTERY_THRESHOLD
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Optional(
                CONF_PASSIVE_TIMEOUT_HOURS,
                default=user_input.get(
                    CONF_PASSIVE_TIMEOUT_HOURS, DEFAULT_PASSIVE_TIMEOUT_HOURS
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            vol.Optional(
                CONF_ACTIVE_TIMEOUT_MINUTES,
                default=user_input.get(
                    CONF_ACTIVE_TIMEOUT_MINUTES, DEFAULT_ACTIVE_TIMEOUT_MINUTES
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
        }
    )


class ZigbeeDoctorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zigbee Doctor."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}

        if user_input is not None:
            base_topic = user_input[CONF_BASE_TOPIC].strip().strip("/")
            user_input[CONF_BASE_TOPIC] = base_topic
            # The base topic only matters for Zigbee2MQTT; ZHA ignores it.
            if user_input.get(CONF_SOURCE) != SOURCE_ZHA and not base_topic:
                errors[CONF_BASE_TOPIC] = "invalid_base_topic"
            else:
                return self.async_create_entry(title=NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return ZigbeeDoctorOptionsFlow(config_entry)


class ZigbeeDoctorOptionsFlow(config_entries.OptionsFlow):
    """Handle Zigbee Doctor options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage options."""
        if user_input is not None:
            user_input[CONF_BASE_TOPIC] = user_input[CONF_BASE_TOPIC].strip().strip("/")
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
        )
