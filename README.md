# SimpleSomneo

SimpleSomneo is a focused fork of the [Philips Somneo Home Assistant integration](https://github.com/theneweinstein/somneo), maintained in [this repository](https://github.com/dskaplan/somneo). It targets Philips Somneo HF367x devices and keeps the integration centered on the wake-up alarm, light, audio player, and device sensors.

This fork intentionally exposes a smaller feature set than the upstream integration. It controls the first wake-up alarm only; additional alarms can still be managed in the Philips SleepMapper app. The Home Assistant integration domain remains `somneo`, preserving the existing `somneo` entity IDs and configuration entries.

## Features

- Control the main light, including brightness, and the night light.
- Control the audio player, including volume, FM presets, and auxiliary input.
- Configure and enable or disable the first wake-up alarm: time, days, light theme, sound, brightness, volume, and gradual-light duration.
- Snooze or dismiss a running alarm and set the snooze duration.
- Read device temperature, humidity, illuminance, sound pressure, current status, and next alarm.
- Automatically discover the Somneo via SSDP, or add it manually by host address.

## Installation

### HACS

1. In Home Assistant, open **HACS → Integrations**.
2. Open the menu and choose **Custom repositories**.
3. Add `https://github.com/dskaplan/somneo` with the category **Integration**.
4. Find and install **SimpleSomneo**, then restart Home Assistant.

### Manual

Copy the `custom_components/somneo` directory from this repository into the `custom_components` directory in your Home Assistant configuration, then restart Home Assistant.

## Setup

After installation, add **SimpleSomneo** from **Settings → Devices & services → Add integration**. The device should be discovered automatically. If it is not, select the integration and enter the Somneo's host address manually.

[![Open your Home Assistant instance and start setting up SimpleSomneo](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=somneo)

## Wake-up alarm entities

The wake-up controls below operate on the first alarm slot (the first alarm shown in SleepMapper). The light gradually turns on before the configured time and reaches the selected brightness when the alarm time arrives; the configured sound starts then as well.

| Entity | Description |
| --- | --- |
| `switch.somneo_wake_up` | Enable or disable the wake-up alarm |
| `time.somneo_wake_up_time` | Time the light reaches full brightness and sound starts |
| `select.somneo_wake_up_days` | Daily, workdays, weekend, or tomorrow only |
| `number.somneo_wake_up_duration` | Gradual-light duration (5–40 minutes) |
| `number.somneo_wake_up_brightness` | Final light level (1–25) |
| `select.somneo_wake_up_light_theme` | Wake-up light theme |
| `select.somneo_wake_up_sound` | Wake-up sound, FM preset, or off |
| `number.somneo_wake_up_volume` | Wake-up sound volume (1–25) |

Other alarms are not exposed by this integration and remain available in the SleepMapper app.

## Development

Run the tests with Python 3.14 or 3.15:

```sh
uv run --no-project --python 3.14 \
  --with pytest-homeassistant-custom-component \
  --with pysomneo==5.0.6 pytest -q
```
