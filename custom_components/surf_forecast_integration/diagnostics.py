"""Diagnostics support for surf_forecast_integration."""

from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import diagnostics

from .const import DOMAIN

TO_REDACT = ["api_key", "password"]


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    return {
        "entry_data": diagnostics.async_redact_data(entry.data, TO_REDACT),
        "options": diagnostics.async_redact_data(entry.options, TO_REDACT),
    }
