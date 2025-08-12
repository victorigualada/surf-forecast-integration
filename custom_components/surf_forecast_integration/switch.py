"""Switch platform for surf_forecast_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity

from .entity import SurfForecastIntegrationEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import CoordinatorEntity

    from .data import SurfForecastIntegrationConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SurfForecastIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up Surf Forecast integration switch entities from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The configuration entry for this integration.
        async_add_entities: Callback to add entities to Home Assistant.

    """
    coordinator = entry.runtime_data.coordinator
    async_add_entities([SurfForecastIntegrationSwitch(coordinator)])


class SurfForecastIntegrationSwitch(SurfForecastIntegrationEntity, SwitchEntity):
    """Switch entity for the Surf Forecast integration."""

    def __init__(self, coordinator: CoordinatorEntity) -> None:
        """
        Initialize the SurfForecastIntegrationSwitch entity.

        Args:
            coordinator: The coordinator entity for data updates.

        """
        super().__init__(coordinator)
        self._attr_is_on = False

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self._attr_is_on

    async def async_turn_on(self, **_: Any) -> None:
        """Turn the switch on."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn the switch off."""
        self._attr_is_on = False
        self.async_write_ha_state()
