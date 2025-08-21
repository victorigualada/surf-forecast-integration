"""
Custom integration to integrate surf_forecast with Home Assistant.

For more details about this integration, please refer to
https://github.com/victorigualada/surf_forecast_integration
"""

from __future__ import annotations

<<<<<<< Updated upstream
from datetime import timedelta
=======
from pathlib import Path
>>>>>>> Stashed changes
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from custom_components.surf_forecast import utils

from .api import SurfForecastIntegrationApiClient
from .const import DOMAIN, LOGGER
from .coordinator import SurfForecastDataUpdateCoordinator
from .data import SurfForecastIntegrationData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SurfForecastIntegrationConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:  # noqa: ARG001
    """Set up the Surf Forecast integration."""
    LOGGER.debug("Setting up Surf Forecast integration")
    # 1. Serve lovelace card
    path = Path(__file__).parent / "www"
    await utils.register_static_path(
        hass,
        "/surf_forecast/surf-forecast-card.js",
        str(path / "surf-forecast-card.js"),
    )

    # 2. Add card to resources
    version = getattr(hass.data["integrations"][DOMAIN], "version", 0)
    await utils.init_resource(
        hass, "/surf_forecast/surf-forecast-card.js", str(version)
    )

    return True


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: SurfForecastIntegrationConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = SurfForecastDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=1),
    )
    entry.runtime_data = SurfForecastIntegrationData(
        client=SurfForecastIntegrationApiClient(
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SurfForecastIntegrationConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: SurfForecastIntegrationConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
