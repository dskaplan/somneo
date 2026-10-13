# Simple Somneo custom integration
Simple Somneo is a Home Assistant custom integration to control a Philips Somneo device (HF367x). This integration lets you control:
  - The light (with brightness) and night light of the Somneo
  - The audio player of the Somneo (FM radio presets or aux. input, volume)
  - A wake-up alarm, where the light gradually turns on before the alarm time
  - Snooze or dismiss a running alarm (buttons) and the snooze time

Furthermore, it provides the following sensors:
  - Ambient sensors (temperature, humidity, illuminance and sound pressure)
  - Status (off, light, audio, sunset, RelaxBreathe, waking up, alarm, snooze)
  - Next alarm

# Installation
You can install this custom component via HACS as a custom repository (https://hacs.xyz/docs/faq/custom_repositories/). Alternatively you can clone or copy the files into the somneo folder in the custom_components folder of HomeAssistant.

# Configuration
The Somneo should be automatically detected via SSDP. If not, you can also manually configure the Somneo:
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=somneo)

# Wake-up
The wake-up entities control the first alarm of the Somneo (the first alarm in the SleepMapper app). The light starts to turn on before the wake-up time and reaches the configured brightness at the wake-up time, when the sound starts.

| Entity | Description |
| --- | --- |
| `switch.somneo_wake_up` | Enable or disable the wake-up |
| `time.somneo_wake_up_time` | Time at which the light is at full brightness and the sound starts |
| `select.somneo_wake_up_days` | Daily, workdays, weekend or tomorrow only |
| `number.somneo_wake_up_duration` | How long the light takes to turn on (5 to 40 minutes) |
| `number.somneo_wake_up_brightness` | Final light level (1 to 25) |
| `select.somneo_wake_up_light_theme` | Colour theme of the light, e.g. sunny day |
| `select.somneo_wake_up_sound` | Wake-up sound, FM preset or off |
| `number.somneo_wake_up_volume` | Volume of the sound (1 to 25) |

The other alarms of the Somneo are not exposed and can still be used from the SleepMapper app.

# Development
Run the tests with:
```
uv run --no-project --python 3.14 --with pytest-homeassistant-custom-component --with pysomneo==5.0.6 pytest
```
