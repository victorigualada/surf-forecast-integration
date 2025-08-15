# 🌊 Surf Forecast Integration for Home Assistant 🌊

This custom integration brings Surfline surf forecasts and conditions into Home Assistant, providing sensors, selects, and automations for your favorite surf spots.
**Get notified on your phone** when your desired surf conditions are met for each spot.

## Features

- Surf rating sensor for each configured spot
- Blueprint for phone notifications when good conditions are met
- First met condition sensor (date when desired conditions are first met)
- Select entity to set minimum desired surf rating
- Supports multiple surf spots

## Automation Blueprints


- `surf_incmoming_notification.yaml`: Notifies your phone when desired conditions are met for a spot.

  [![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fvictorigualada%2Fsurf-forecast-integration%2Fblob%2Fmain%2Fblueprints%2Fsurf_incoming_notification.yaml)

## Installation

### HACS


### Manual

1. Copy the `surf_forecast` folder to your Home Assistant `custom_components` directory:

	 ```bash
	 custom_components/surf_forecast/
	 ```
2. Restart Home Assistant.
3. Add the integration via the Home Assistant UI (Settings → Devices & Services → Add Integration → Surf Forecast).

## Configuration

1. Search for your surf spot by name in the config flow.
2. Select the correct spot from the list.
3. Repeat for additional spots (each spot can only be added once).
4. Set your desired minimum surf rating for each spot using the select entity. This will be used by the blueprint to determine when to notify you.

## Entities

- **Sensor:**
	- `sensor.<spot>_surf_rating`: Current/next surf rating
	- `sensor.<spot>_incoming_surf_date`: Date when good conditions are first met
- **Select:**
	- `select.<spot>_minimum_surf_rating`: Set your minimum desired surf rating
- **Binary Sensor:**
	- `binary_sensor.<spot>_incoming_surf`: On when forecast meets/exceeds your minimum rating

## Troubleshooting

- If the integration or entities do not appear, check the Home Assistant logs for errors.
- Ensure the `domain` in `manifest.json` matches the folder name.
- Restart Home Assistant after any changes to translation or integration files.
- Only one entry per surf spot is allowed.

---

Thanks to ludeeus for the original integration template.