"""Select platform for surf_forecast_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SURFLINE_RATING_LEVELS

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SurfForecastIntegrationConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SurfForecastIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entity for minimum surf rating."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([SurflineMinRatingSelect(coordinator, entry)])


class SurflineMinRatingSelect(CoordinatorEntity, SelectEntity):
    """Select entity for minimum surf rating preference."""

    _attr_has_entity_name = True
    _attr_translation_key = "min_rating"

    @property
    def current_option(self) -> str | None:
        return self._attr_current_option

    def __init__(self, coordinator: CoordinatorEntity, config_entry: Any) -> None:
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_min_rating"
        self._attr_name = "Minimum Surf Rating"
        self._attr_options = SURFLINE_RATING_LEVELS
        self._attr_current_option = SURFLINE_RATING_LEVELS[0]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "Surfline",
            "model": "Surf Spot",
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        if option in SURFLINE_RATING_LEVELS:
            self._attr_current_option = option
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
