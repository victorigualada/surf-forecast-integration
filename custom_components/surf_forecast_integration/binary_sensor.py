"""Binary sensor platform for surf_forecast_integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN, SURFLINE_RATING_LEVELS

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SurfForecastIntegrationConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SurfForecastIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor for surf forecast conditions."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([SurflineConditionBinarySensor(coordinator, entry)])


class SurflineConditionBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor that is on if any forecasted rating meets the selected."""

    @property
    def icon(self) -> str:
        """Return a surfing icon if on, bed icon if off."""
        return "mdi:surfing" if self.is_on else "mdi:bed"

    async def async_added_to_hass(self) -> None:
        """Subscribe to select entity state changes and coordinator updates."""
        await super().async_added_to_hass()
        # Listen for select changes
        spot_slug = slugify(self.config_entry.title)
        select_entity_id = f"select.{spot_slug}_minimum_surf_rating"
        sensor_entity_id = f"sensor.{spot_slug}_surf_rating"
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                select_entity_id,
                self._handle_select_change,
            )
        )
        # Listen for sensor state changes
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                sensor_entity_id,
                self._handle_sensor_change,
            )
        )
        # Listen for coordinator data refresh
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def _handle_sensor_change(self, event: object) -> None:  # noqa: ARG002
        """Handle sensor entity state change by updating binary sensor state."""
        self.async_write_ha_state()

    async def _handle_select_change(self, event: object) -> None:  # noqa: ARG002
        """Handle select entity state change by updating binary sensor state."""
        self.async_write_ha_state()

    """
    Binary sensor that is on if any forecasted rating meets or exceeds the selected.
    minimum rating.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "good_conditions"

    def __init__(self, coordinator: CoordinatorEntity, config_entry: Any) -> None:
        """Initialize the Surfline good conditions binary sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_good_conditions"
        self._attr_name = "Good Surf Conditions"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "victorigualada",
            "model": "Surf Forecast",
        }

    @property
    def is_on(self) -> bool:
        """Return true if any forecasted rating is >= the selected minimum rating."""
        hass = self.coordinator.hass
        # Slugify the config entry title to match Home Assistant's entity_id pattern
        spot_slug = slugify(self.config_entry.title)

        # Get the select entity state for minimum rating
        select_entity_id = f"select.{spot_slug}_minimum_surf_rating"
        select_state = hass.states.get(select_entity_id)
        min_rating = select_state.state if select_state else None

        # Get the sensor entity state for forecasted ratings
        sensor_entity_id = f"sensor.{spot_slug}_surf_rating"
        sensor_state = hass.states.get(sensor_entity_id)
        forecast = sensor_state.attributes.get("forecast") if sensor_state else None

        if not min_rating or not forecast:
            return False
        min_index = SURFLINE_RATING_LEVELS.index(min_rating)
        # Iterate over all forecasted values in the attributes
        for rating in forecast:
            key = rating["rating"].get("key")
            if key and SURFLINE_RATING_LEVELS.index(key) >= min_index:
                return True
        return False
