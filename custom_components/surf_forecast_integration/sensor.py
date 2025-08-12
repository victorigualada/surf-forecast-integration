"""Sensor platform for surf_forecast_integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN, SURFLINE_RATING_KEY_TO_ICON, SURFLINE_RATING_LEVELS

if TYPE_CHECKING:
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import SurfForecastIntegrationConfigEntry


async def async_setup_entry(
    entry: SurfForecastIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a rating sensor with all forecasted ratings as attributes."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            SurflineRatingSensor(coordinator, entry),
            SurflineFirstMetConditionSensor(coordinator, entry),
        ]
    )


class SurflineFirstMetConditionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the first forecasted date/time that meets the selected min rating."""

    _LOGGER = logging.getLogger(__name__)

    async def async_added_to_hass(self) -> None:
        """Subscribe to select entity state changes and coordinator updates."""
        await super().async_added_to_hass()

        spot_slug = slugify(self.config_entry.title)
        select_entity_id = f"select.{spot_slug}_minimum_surf_rating"
        rating_entity_id = f"sensor.{spot_slug}_surf_rating"

        async def _handle_related_change(event: object) -> None:  # noqa: ARG001
            """Handle related entity state change by updating this sensor's state."""
            self.async_write_ha_state()

        # Listen for changes to the select entity
        self.async_on_remove(
            self.hass.helpers.event.async_track_state_change_event(
                select_entity_id, _handle_related_change
            )
        )
        # Listen for changes to the rating sensor entity
        self.async_on_remove(
            self.hass.helpers.event.async_track_state_change_event(
                rating_entity_id, _handle_related_change
            )
        )
        # Also listen for coordinator updates (already handled by CoordinatorEntity)

    """Sensor for the first forecasted date/time that meets or exceeds the selected
    minimum rating.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "next_desired_condition_date"

    def __init__(self, coordinator: CoordinatorEntity, config_entry: Any) -> None:
        """
        Initialize the SurflineFirstMetConditionSensor.

        Args:
            coordinator: The data update coordinator instance.
            config_entry: The config entry for this integration.

        """
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_next_desired_condition_date"
        self._attr_name = "Next Desired Condition Date"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "victorigualada",
            "model": "Surf forecast",
        }

    @property
    def native_value(self) -> str | None:
        """Return the ISO date/time of the first forecast that meets min rating."""
        hass = self.coordinator.hass
        spot_slug = slugify(self.config_entry.title)
        select_entity_id = f"select.{spot_slug}_minimum_surf_rating"
        select_state = hass.states.get(select_entity_id)
        min_rating = select_state.state if select_state else None
        data = self.coordinator.data
        if (
            not min_rating
            or not data
            or "data" not in data
            or "rating" not in data["data"]
        ):
            return None

        min_index = SURFLINE_RATING_LEVELS.index(min_rating)
        for rating in data["data"]["rating"]:
            key = rating["rating"].get("key")
            if key and SURFLINE_RATING_LEVELS.index(key) >= min_index:
                # Convert timestamp to ISO 8601 string
                return (
                    datetime.fromtimestamp(rating["timestamp"], tz=UTC)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
        return None


class SurflineRatingSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Surfline spot rating (current/next rating)."""

    _attr_has_entity_name = True
    _attr_translation_key = "surf_rating"

    def __init__(self, coordinator: CoordinatorEntity, config_entry: Any) -> None:
        """Initialize the Surfline rating sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_surf_rating"
        self._attr_name = "Surf Rating"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": "victorigualada",
            "model": "Surf forecast",
        }

    @property
    def native_value(self) -> str | None:
        """Return the current or next surf rating key (e.g., 'FAIR', 'GOOD')."""
        data = self.coordinator.data
        if not data or "data" not in data or "rating" not in data["data"]:
            return None
        now = datetime.now(UTC).timestamp()
        for rating in data["data"]["rating"]:
            if rating["timestamp"] >= now:
                return rating["rating"].get("key")
        return None

    @property
    def icon(self) -> str | None:
        """Return an icon based on the current/next rating key."""
        data = self.coordinator.data
        if not data or "data" not in data or "rating" not in data["data"]:
            return None
        now = datetime.now(UTC).timestamp()
        for rating in data["data"]["rating"]:
            if rating["timestamp"] >= now:
                return SURFLINE_RATING_KEY_TO_ICON.get(
                    rating["rating"].get("key"), "mdi:surfing"
                )
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose all forecasted ratings and location as attributes."""
        data = self.coordinator.data
        if not data or "data" not in data or "rating" not in data["data"]:
            return {}
        return {
            "forecast": data["data"]["rating"],
            "location": data.get("associated", {}).get("location"),
        }


# Remove duplicate async_setup_entry and unused code at the end
