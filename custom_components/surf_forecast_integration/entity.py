"""SurfForecastIntegrationEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import BlueprintDataUpdateCoordinator


class SurfForecastIntegrationEntity(CoordinatorEntity[BlueprintDataUpdateCoordinator]):
    """SurfForecastIntegrationEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: BlueprintDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        config_entry = coordinator.config_entry
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "victorigualada",
            "model": "Surf forecast",
        }
        self._attr_has_entity_name = True
