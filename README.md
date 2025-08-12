# Surf Forecast Integration for Home Assistant

This custom integration brings Surfline surf forecasts and conditions into Home Assistant, providing sensors, selects, and automations for your favorite surf spots.

## Features

- Surf rating sensor for each configured spot
- First met condition sensor (date when good conditions are first met)
- Select entity to set minimum desired surf rating
- Binary sensor that turns on when forecast meets or exceeds your minimum rating
- Blueprint for phone notifications when good conditions are met
- Supports multiple surf spots (prevents duplicates)
- UI translations and config flow

## Installation

1. Copy the `surf_forecast_integration` folder to your Home Assistant `custom_components` directory:
	 ```
	 custom_components/surf_forecast_integration/
	 ```
2. Restart Home Assistant.
3. Add the integration via the Home Assistant UI (Settings → Devices & Services → Add Integration → Surf Forecast Integration).

## Configuration

1. Search for your surf spot by name in the config flow.
2. Select the correct spot from the list.
3. Repeat for additional spots (each spot can only be added once).

## Entities

- **Sensor:**
	- `sensor.<spot>_surf_rating`: Current/next surf rating
	- `sensor.<spot>_first_met_condition`: Date when good conditions are first met
- **Select:**
	- `select.<spot>_minimum_surf_rating`: Set your minimum desired surf rating
- **Binary Sensor:**
	- `binary_sensor.<spot>_good_conditions`: On when forecast meets/exceeds your minimum rating

## Automation Blueprint

Blueprints are provided in `config/blueprints/automation/`:

- `surf_spot_good_condition_notification.yaml`: Notifies your phone when good conditions are met for a spot.

## Translations

The integration supports UI translations. If you see translation keys instead of labels, ensure you have restarted Home Assistant after editing translation files.

## Troubleshooting

- If the integration or entities do not appear, check the Home Assistant logs for errors.
- Ensure the `domain` in `manifest.json` matches the folder name.
- Restart Home Assistant after any changes to translation or integration files.
- Only one entry per surf spot is allowed.

## Links

- [Surfline](https://www.surfline.com/)
- [Home Assistant Custom Integration Docs](https://developers.home-assistant.io/docs/creating_integration_file_structure/)

---
Maintained by victorigualada. Contributions welcome!
Thanks to ludeeus for the original integration template.