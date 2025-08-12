from __future__ import annotations

import logging
import socket
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

SURFLINE_SEARCH_URL = "https://services.surfline.com/search/site?q=${spot_name_or_city_name}&querySize=10&suggestionSize=10&newsSearch=false^&includeWavePools=false"
SURFLINE_RATINGS_URL = "https://services.surfline.com/kbyg/spots/forecasts/ratings"


"""Sample API Client."""


class SurfForecastIntegrationApiClientError(Exception):
    """Exception to indicate a general API error."""


class SurfForecastIntegrationApiClientCommunicationError(
    SurfForecastIntegrationApiClientError,
):
    """Exception to indicate a communication error."""


class SurfForecastIntegrationApiClientAuthenticationError(
    SurfForecastIntegrationApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise SurfForecastIntegrationApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class SurfForecastIntegrationApiClient:
    """Sample API Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._session = session

    async def async_search_spots(self, query: str) -> list[dict[str, Any]]:
        """Search for surf spots by name or city using the correct Surfline search URL."""
        url = (
            "https://services.surfline.com/search/site"
            f"?q={query}&querySize=10&suggestionSize=10&newsSearch=true&includeWavePools=false"
        )
        response = await self._api_wrapper(
            method="get",
            url=url,
        )
        # The response structure may differ from the old endpoint, so adapt parsing as needed
        spots = []
        for result in response if isinstance(response, list) else [response]:
            hits = result.get("hits", {}).get("hits", [])
            for hit in hits:
                src = hit.get("_source", {})
                spot_id = hit.get("_id")
                if spot_id is None:
                    continue
                if hit.get("_index") != "spots":
                    continue
                spots.append(
                    {
                        "spot_id": spot_id,
                        "name": src.get("name"),
                        "city": src.get("breadCrumbs", [None, None, None, None])[-1],
                        "region": src.get("breadCrumbs", [None, None, None, None])[-2],
                        "country": src.get("breadCrumbs", [None, None, None, None])[0],
                        "latitude": src.get("location", {}).get("lat"),
                        "longitude": src.get("location", {}).get("lon"),
                        "href": src.get("href"),
                    }
                )
        return spots

    async def async_get_ratings(self, spot_id: str) -> dict[str, Any]:
        """Fetch ratings for a given spot from Surfline API."""
        url = (
            "https://services.surfline.com/kbyg/spots/forecasts/rating"
            f"?spotId={spot_id}&days=5&intervalHours=1&cacheEnabled=true"
        )
        response = await self._api_wrapper(
            method="get",
            url=url,
        )

        return response

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            response = await self._session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
            )
            _verify_response_or_raise(response)
            return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise SurfForecastIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise SurfForecastIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise SurfForecastIntegrationApiClientError(
                msg,
            ) from exception
