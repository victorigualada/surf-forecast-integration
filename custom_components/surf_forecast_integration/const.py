"""Constants for surf_forecast_integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "surf_forecast_integration"
ATTRIBUTION = "Data provided by https://surfline.com"

# Mapping of Surfline rating keys to Material Design Icons
SURFLINE_RATING_KEY_TO_ICON = {
    "POOR": "mdi:weather-cloudy",
    "POOR_TO_FAIR": "mdi:weather-fog",
    "FAIR": "mdi:weather-partly-cloudy",
    "FAIR_TO_GOOD": "mdi:weather-partly-snowy-rainy",
    "GOOD": "mdi:weather-sunny",
}

# Ordered list of rating keys for select and comparison
SURFLINE_RATING_LEVELS = [
    "VERY_POOR",
    "POOR",
    "POOR_TO_FAIR",
    "FAIR",
    "FAIR_TO_GOOD",
    "GOOD",
]
