"""Select platform for surf_forecast."""

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
    hass: HomeAssistant,  # noqa: ARG001
    entry: SurfForecastIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entity for minimum surf rating."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([SurflineMinRatingSelect(coordinator, entry)])


class SurflineMinRatingSelect(CoordinatorEntity, SelectEntity):
    @property
    def available(self) -> bool:
        """Keep select entity available during coordinator refreshes."""
        return self.coordinator.last_update_success or self.coordinator.data is not None

    """Select entity for minimum surf rating preference."""

    _attr_has_entity_name = True
    _attr_translation_key = "min_rating"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected minimum surf rating option."""
        return self._attr_current_option

    def __init__(self, coordinator: CoordinatorEntity, config_entry: Any) -> None:
        """
        Initialize the SurflineMinRatingSelect entity.

        Args:
            coordinator: The data update coordinator for surf forecast.
            config_entry: The config entry associated with this entity.
        """
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_min_rating"
        self._attr_name = "Minimum Surf Rating"
        self._attr_options = SURFLINE_RATING_LEVELS
        # Restore from config_entry.options if present, else use default
        self._attr_current_option = config_entry.options.get(
            "min_surf_rating", SURFLINE_RATING_LEVELS[0]
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "victorigualada",
            "model": "Surf forecast",
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity being added to Home Assistant."""
        await super().async_added_to_hass()
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """
        Change the selected minimum surf rating option and persist it.

        Args:
            option: The new minimum surf rating to select.

        """
        if option in SURFLINE_RATING_LEVELS:
            self._attr_current_option = option
            # Persist the selected option in config_entry.options
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options={**self.config_entry.options, "min_surf_rating": option},
            )
            self.async_write_ha_state()
            self.coordinator.async_update_listeners()
