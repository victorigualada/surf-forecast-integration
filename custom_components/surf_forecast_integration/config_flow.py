"""Adds config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession

if TYPE_CHECKING:
    from aiohttp import ClientSession

from .api import (
    SurfForecastIntegrationApiClient,
)
from .const import DOMAIN


async def async_search_spots(session: ClientSession, spot_query: str):  # noqa: ANN201
    """Search for surf spots matching the query."""
    return await SurfForecastIntegrationApiClient(session=session).async_search_spots(
        spot_query
    )


class SurfForecastFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            spot_query = user_input["spot_query"]
            session = async_create_clientsession(self.hass)
            try:
                spots = await async_search_spots(session, spot_query)
            except (
                Exception  # noqa: BLE001
            ):  # Replace with specific exception if possible
                errors["base"] = "cannot_connect"
                spots = []
            if not spots:
                errors["base"] = "no_spots_found"
            else:
                # Check if any of the found spots is already configured
                existing_spot_ids = {
                    entry.data.get("spot_id") for entry in self._async_current_entries()
                }
                filtered_spots = [
                    s for s in spots if s["spot_id"] not in existing_spot_ids
                ]
                if not filtered_spots:
                    errors["base"] = "already_configured"
                else:
                    self.spot_search_results = filtered_spots
                    return await self.async_step_select_spot()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("spot_query"): str}),
            errors=errors,
        )

    async def async_step_select_spot(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """
        Handle the selection of a surf spot by the user.

        Presents a list of available surf spots to the user and creates a config entry

        for the selected spot.
        """
        errors = {}
        spots = getattr(self, "spot_search_results", [])
        spot_options = {s["spot_id"]: f"{s['name']} ({s['city']})" for s in spots}
        if user_input is not None:
            spot_id = user_input["spot_id"]
            # Prevent adding a spot that is already configured (race condition safety)
            if any(
                entry.data.get("spot_id") == spot_id
                for entry in self._async_current_entries()
            ):
                errors["base"] = "already_configured"
            else:
                spot = next((s for s in spots if s["spot_id"] == spot_id), None)
                if spot:
                    return self.async_create_entry(
                        title=f"{spot['name']} ({spot['city']})",
                        data={
                            "spot_id": spot["spot_id"],
                            "name": spot["name"],
                            "city": spot["city"],
                            "region": spot.get("region"),
                            "country": spot.get("country"),
                            "latitude": spot.get("latitude"),
                            "longitude": spot.get("longitude"),
                            "href": spot.get("href"),
                        },
                    )
                errors["base"] = "unknown"
        return self.async_show_form(
            step_id="select_spot",
            data_schema=vol.Schema({vol.Required("spot_id"): vol.In(spot_options)}),
            errors=errors,
            description_placeholders={"spot_count": str(len(spots))},
        )
