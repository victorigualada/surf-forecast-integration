"""DataUpdateCoordinator for surf_forecast."""

from __future__ import annotations

from datetime import timedelta
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
    from logging import Logger

    from .data import SurfForecastIntegrationConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SurfForecastDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: SurfForecastIntegrationConfigEntry

    def __init__(
        self,
        hass: Any,
        logger: Logger,
        name: str,
        config_entry: SurfForecastIntegrationConfigEntry,
    ) -> None:
        """Initialize the SurfForecastDataUpdateCoordinator with 1h polling."""
        super().__init__(
            hass,
            logger=logger,
            name=name,
            update_interval=timedelta(hours=1),
            config_entry=config_entry,
        )
        self.config_entry = config_entry

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
