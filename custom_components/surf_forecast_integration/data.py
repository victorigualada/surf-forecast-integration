"""Custom types for surf_forecast_integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import SurfForecastIntegrationApiClient
    from .coordinator import BlueprintDataUpdateCoordinator

type SurfForecastIntegrationConfigEntry = ConfigEntry["SurfForecastIntegrationData"]


@dataclass
class SurfForecastIntegrationData:
    """Data for the Surf Forecast integration."""

    client: SurfForecastIntegrationApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
