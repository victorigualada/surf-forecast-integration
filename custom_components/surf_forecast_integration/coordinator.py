"""DataUpdateCoordinator for surf_forecast_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SurfForecastIntegrationApiClient,
    SurfForecastIntegrationApiClientAuthenticationError,
    SurfForecastIntegrationApiClientError,
)

if TYPE_CHECKING:
    from .data import SurfForecastIntegrationConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class BlueprintDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: SurfForecastIntegrationConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            session = async_get_clientsession(self.hass)
            spot_id = self.config_entry.data["spot_id"]
            client = SurfForecastIntegrationApiClient(session)
            return await client.async_get_ratings(spot_id)
        except SurfForecastIntegrationApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except SurfForecastIntegrationApiClientError as exception:
            raise UpdateFailed(exception) from exception
        except OSError as err:
            # Catch network-related errors (socket, aiohttp, etc.)
            msg = "Error fetching Surfline data: network or system error"
            raise UpdateFailed(msg) from err
