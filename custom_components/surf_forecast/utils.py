"""
Utility functions for the Surf Forecast integration.

This module provides helpers for static path registration and related tasks.

Borrowed from https://github.com/AlexxIT/WebRTC/blob/master/custom_components/webrtc/utils.py
"""

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

from .const import LOGGER

STATIC_PATHS_VERSION_THRESHOLD = 202407


async def register_static_path(hass: HomeAssistant, url_path: str, path: str) -> None:
    """Register a static path for serving files in Home Assistant."""
    LOGGER.debug("Registering static path: %s -> %s", url_path, path)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url_path, path, True)]  # noqa: FBT003
    )
    LOGGER.debug("Static path registered: %s -> %s", url_path, path)


async def init_resource(hass: HomeAssistant, url: str, ver: str) -> bool:
    """

    Add extra JS module for lovelace mode YAML and new lovelace resource.

    for mode GUI. It's better to add extra JS for all modes, because it has

    random url to avoid problems with the cache. But chromecast don't support

    extra JS urls and can't load custom card.

    """
    lovelace = hass.data["lovelace"]
    resources: ResourceStorageCollection = (
        lovelace.resources if hasattr(lovelace, "resources") else lovelace["resources"]
    )

    # force load storage
    await resources.async_get_info()

    url2 = f"{url}?v={ver}"

    for item in resources.async_items():
        LOGGER.debug("Check lovelace resource: %s", item)
        if not item.get("url", "").startswith(url):
            continue

        # no need to update
        if item["url"].endswith(ver):
            return False

        LOGGER.debug(f"Update lovelace resource to: {url2}")

        if isinstance(resources, ResourceStorageCollection):
            await resources.async_update_item(
                item["id"], {"res_type": "module", "url": url2}
            )
        else:
            # not the best solution, but what else can we do
            item["url"] = url2

        return True

    if isinstance(resources, ResourceStorageCollection):
        LOGGER.debug(f"Add new lovelace resource: {url2}")
        await resources.async_create_item({"res_type": "module", "url": url2})
    else:
        LOGGER.debug(f"Add extra JS module: {url2}")
        add_extra_js_url(hass, url2)

    return True
