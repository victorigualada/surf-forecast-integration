// Advanced Lovelace UI schema for full card picker integration
if (window.loadCardHelpers) {
  window.loadCardHelpers().then((helpers) => {
    if (helpers && helpers.createCardElement) {
      SurfForecastCard.getConfigElement = function () {
        const element = document.createElement('surf-forecast-card-editor');
        return element;
      };
      SurfForecastCard.getStubConfig = function (hass, entities) {
        const surfSensor = entities.find(eid => eid.startsWith('sensor.') && eid.endsWith('_surf_rating'));
        return {
          type: 'custom:surf-forecast-card',
          sensor: surfSensor || '',
        };
      };
      SurfForecastCard.type = 'custom:surf-forecast-card';
      SurfForecastCard.title = 'Surf Forecast Card';
      SurfForecastCard.description = 'A card to display Surfline-style surf forecasts.';
      SurfForecastCard.preview = true;
      SurfForecastCard.icon = 'mdi:surfing';
    }
  });
}
// Config editor for Lovelace UI
class SurfForecastCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass) return;
    this.innerHTML = '';
    const sensors = Object.keys(this._hass.states)
      .filter(eid => eid.startsWith('sensor.') && eid.endsWith('_surf_rating'));
    const label = document.createElement('label');
    label.textContent = 'Surf spot sensor:';
    this.appendChild(label);
    const select = document.createElement('select');
    select.style.marginLeft = '0.5em';
    sensors.forEach(eid => {
      const option = document.createElement('option');
      option.value = eid;
      option.textContent = eid.replace('sensor.', '').replace('_surf_rating', '').replace(/_/g, ' ');
      if (this._config && this._config.sensor === eid) option.selected = true;
      select.appendChild(option);
    });
    select.addEventListener('change', () => {
      this._config = { ...this._config, sensor: select.value };
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this._config } }));
    });
    this.appendChild(select);
  }

  getConfig() {
    return this._config;
  }
}

customElements.define('surf-forecast-card-editor', SurfForecastCardEditor);

class SurfForecastCard extends HTMLElement {
  setConfig(config) {
    if (!config.sensor) {
      throw new Error('You need to define sensor');
    }
    this.config = config;
    this._initialized = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._createCard();
      this._initialized = true;
    }
    this._update();
  }

  _createCard() {
    if (this.card) {
      this.card.remove();
    }
    this.card = document.createElement('ha-card');
    this.card.className = 'surf-card';
    this.header = document.createElement('div');
    this.header.className = 'header';
    this.spotName = document.createElement('span');
    this.spotName.className = 'spot-name';
    this.header.appendChild(this.spotName);
    const subtitle = document.createElement('span');
    subtitle.style.fontSize = '0.9em';
    subtitle.style.color = 'var(--secondary-text-color)';
    subtitle.textContent = 'Surf Forecast';
    this.header.appendChild(subtitle);
    this.card.appendChild(this.header);
    this.forecastRow = document.createElement('div');
    this.forecastRow.className = 'forecast-row';
    this.card.appendChild(this.forecastRow);
    this.styles = document.createElement('style');
    this.styles.textContent = `
      .surf-card {
        background: var(--card-background-color, #fff);
        border-radius: 12px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
        padding: 1.2em 1em 1em 1em;
        font-family: var(--primary-font-family);
        max-width: 600px;
        margin: 0 auto;
      }
      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5em;
      }
      .spot-name {
        font-size: 1.3em;
        font-weight: bold;
      }
      .forecast-row {
        display: flex;
        gap: 0.7em;
        overflow-x: auto;
        padding-bottom: 0.5em;
      }
      .forecast-item {
        flex: 0 0 70px;
        background: rgba(0,0,0,0.03);
        border-radius: 8px;
        padding: 0.5em 0.2em;
        text-align: center;
        min-width: 70px;
      }
      .rating {
        font-size: 1.5em;
        margin-bottom: 0.1em;
      }
      .time {
        font-size: 0.95em;
        color: var(--secondary-text-color);
      }
      .details {
        font-size: 0.9em;
        color: var(--secondary-text-color);
        margin-top: 0.2em;
      }
      .current {
        border: 2px solid var(--primary-color, #03a9f4);
        background: rgba(3,169,244,0.08);
      }
    `;
    this.card.appendChild(this.styles);
    this.appendChild(this.card);
  }

  _update() {
    if (!this._hass || !this.config) return;
    const sensor = this.config.sensor;
    const state = this._hass.states[sensor];
    const spotName = sensor.replace('sensor.', '').replace('_surf_rating', '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    this.spotName.textContent = spotName;
    // Clear previous forecast
    while (this.forecastRow.firstChild) {
      this.forecastRow.removeChild(this.forecastRow.firstChild);
    }
    let forecast = [];
    if (state && state.attributes && Array.isArray(state.attributes.forecast)) {
      forecast = state.attributes.forecast.map((f, idx) => ({
        rating: f.rating && f.rating.key ? this._ratingToNumber(f.rating.key) : 0,
        time: f.time || '',
        height: f.height || '',
        wind: f.wind || '',
        current: idx === 0,
      }));
    }
    forecast.forEach((f, idx) => {
      const item = document.createElement('div');
      item.className = 'forecast-item' + (f.current ? ' current' : '');
      const ratingDiv = document.createElement('div');
      ratingDiv.className = 'rating';
      ratingDiv.innerHTML = this._ratingIcon(f.rating);
      item.appendChild(ratingDiv);
      const timeDiv = document.createElement('div');
      timeDiv.className = 'time';
      timeDiv.textContent = f.time;
      item.appendChild(timeDiv);
      const detailsDiv = document.createElement('div');
      detailsDiv.className = 'details';
      detailsDiv.innerHTML = `<div>${f.height}</div><div>${f.wind}</div>`;
      item.appendChild(detailsDiv);
      this.forecastRow.appendChild(item);
    });
  }

  _ratingToNumber(key) {
    // Map rating key to number of stars (customize as needed)
    const map = { POOR: 1, FAIR: 2, 'FAIR_TO_GOOD': 3, GOOD: 4, EPIC: 5 };
    return map[key] || 0;
  }

  _getForecast() {
    const { entities } = this.config;
    if (!entities.forecast || !Array.isArray(entities.forecast)) return [];
    return entities.forecast.map((eid, idx) => {
      const state = this._hass.states[eid];
      if (!state) return { rating: 0, time: '', height: '', wind: '', current: idx === 0 };
      return {
        rating: state.attributes.rating ?? state.state,
        time: state.attributes.time ?? '',
        height: state.attributes.height ?? '',
        wind: state.attributes.wind ?? '',
        current: idx === 0, // Mark first as current
      };
    });
  }

  _ratingIcon(rating) {
    // 0-5 stars, use mdi icons
    const n = Number(rating);
    if (isNaN(n)) return '<ha-icon icon="mdi:star-outline"></ha-icon>';
    let icons = '';
    for (let i = 0; i < 5; i++) {
      icons += `<ha-icon icon="mdi:${i < n ? 'star' : 'star-outline'}"></ha-icon>`;
    }
    return icons;
  }

  getCardSize() {
    return 3;
  }
}

// Add type property for Lovelace card picker
SurfForecastCard.type = 'custom:surf-forecast-card';

// Provide a stub config for Lovelace card picker
SurfForecastCard.getStubConfig = function (hass, entities) {
  // Try to find a surf rating sensor
  const surfSensor = entities.find(eid => eid.startsWith('sensor.') && eid.endsWith('_surf_rating'));
  return {
    type: 'custom:surf-forecast-card',
    sensor: surfSensor || '',
  };
};


customElements.define('surf-forecast-card', SurfForecastCard);

// Attach config editor to card
SurfForecastCard.getConfigElement = function () {
  return document.createElement('surf-forecast-card-editor');
};