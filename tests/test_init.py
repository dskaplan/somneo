"""Tests for the Somneo integration."""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import Mock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.simple_somneo.const import DOMAIN
from custom_components.simple_somneo.coordinator import decode_status

from .conftest import FakeClient


async def _call(hass: HomeAssistant, service: str, entity_id: str, **data) -> None:
    domain = entity_id.split(".")[0]
    await hass.services.async_call(
        domain, service, {"entity_id": entity_id, **data}, blocking=True
    )


def _last_write(client: FakeClient, port: str) -> dict:
    return next(payload for name, payload in reversed(client.calls) if name == port)


async def test_states(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Test the entities and their initial state."""
    states = {state.entity_id: state.state for state in hass.states.async_all()}
    assert states == {
        "button.simple_somneo_dismiss": "unknown",
        "button.simple_somneo_snooze": "unknown",
        "light.simple_somneo_light": "off",
        "light.simple_somneo_night_light": "off",
        "media_player.simple_somneo_audio_player": "off",
        "number.simple_somneo_snooze_time": "9",
        "number.simple_somneo_wake_up_brightness": "20",
        "number.simple_somneo_wake_up_duration": "30",
        "number.simple_somneo_wake_up_volume": "12",
        "select.simple_somneo_wake_up_days": "daily",
        "select.simple_somneo_wake_up_light_theme": "sunny_day",
        "select.simple_somneo_wake_up_sound": "forest_birds",
        "sensor.simple_somneo_humidity": "48.6",
        "sensor.simple_somneo_illuminance": "0.1",
        "sensor.simple_somneo_next_alarm": "unknown",
        "sensor.simple_somneo_sound_pressure": "37",
        "sensor.simple_somneo_status": "off",
        "sensor.simple_somneo_temperature": "23.3",
        "switch.simple_somneo_wake_up": "off",
        "time.simple_somneo_wake_up_time": "07:30:00",
    }


async def test_wakeup(
    hass: HomeAssistant, entry: MockConfigEntry, client: FakeClient
) -> None:
    """Test that the wake-up controls change the first alarm of the Somneo."""
    await _call(hass, "set_value", "number.simple_somneo_wake_up_duration", value=40)
    assert _last_write(client, "wualm/prfwu") == {
        "prfnr": 1, "ctype": 0, "curve": 20, "durat": 40,
    }  # fmt: skip

    await _call(
        hass, "select_option", "select.simple_somneo_wake_up_light_theme", option="island_red"
    )
    assert _last_write(client, "wualm/prfwu")["ctype"] == 1

    await _call(hass, "select_option", "select.simple_somneo_wake_up_sound", option="off")
    assert _last_write(client, "wualm/prfwu")["snddv"] == "off"

    await _call(hass, "select_option", "select.simple_somneo_wake_up_sound", option="fm_2")
    assert _last_write(client, "wualm/prfwu") == {
        "prfnr": 1, "snddv": "fmr", "sndch": "2", "sndlv": 12,
    }  # fmt: skip

    await _call(hass, "set_value", "time.simple_somneo_wake_up_time", time="06:45:00")
    assert _last_write(client, "wualm/prfwu") == {"prfnr": 1, "almhr": 6, "almmn": 45}

    await _call(hass, "select_option", "select.simple_somneo_wake_up_days", option="workdays")
    assert _last_write(client, "wualm/prfwu") == {"prfnr": 1, "daynm": 62}

    await _call(hass, "turn_on", "switch.simple_somneo_wake_up")
    assert _last_write(client, "wualm/prfwu") == {
        "prfnr": 1, "prfvs": True, "prfen": True,
    }  # fmt: skip


async def test_controls(
    hass: HomeAssistant, entry: MockConfigEntry, client: FakeClient
) -> None:
    """Test the light, audio and alarm controls."""
    await _call(hass, "turn_on", "light.simple_somneo_light", brightness=1)
    assert _last_write(client, "wulgt")["ltlvl"] == 1

    await _call(hass, "press", "button.simple_somneo_snooze")
    assert _last_write(client, "wualm/alctr") == {"tapsz": True}

    await _call(hass, "press", "button.simple_somneo_dismiss")
    assert _last_write(client, "wualm/alctr") == {"disms": True}

    await _call(hass, "volume_set", "media_player.simple_somneo_audio_player", volume_level=1)
    assert _last_write(client, "wuply") == {"sdvol": 25}


@pytest.mark.parametrize(
    ("wusts", "status"),
    [
        (1, "off"), (2, "off"), (257, "light"), (258, "light"), (264, "sunset"),
        (777, "sunset"), (320, "relax_breathe"), (513, "audio"), (769, "audio"),
        (2309, "wake_up"), (2817, "alarm"), (2321, "snooze"),
    ],
)  # fmt: skip
def test_decode_status(wusts: int, status: str) -> None:
    """Test decoding the status bit field."""
    assert decode_status(wusts) == status


async def test_unavailable_after_repeated_failures(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    """Test that a single failed request does not make the entities unavailable."""
    entry.runtime_data.somneo.fetch_data = Mock(side_effect=TimeoutError)
    for failures in range(1, 4):
        async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=11 * failures))
        await hass.async_block_till_done(wait_background_tasks=True)
        state = hass.states.get("sensor.simple_somneo_temperature").state
        assert (state == "unavailable") == (failures == 3)


async def test_migration_removes_old_entities(
    hass: HomeAssistant, client: FakeClient, entity_registry: er.EntityRegistry
) -> None:
    """Test that entities of older versions are removed."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="serial",
        version=4,
        data={
            "host": "192.0.2.1",
            "name": "Somneo",
            "dev_info": {"manufacturer": "Philips", "model": "x", "modelnumber": "y"},
        },
    )
    entry.add_to_hass(hass)
    for platform, key in (("switch", "alarm0"), ("light", "light"), ("text", "alarm3")):
        entity_registry.async_get_or_create(
            platform, DOMAIN, f"serial_{key}", config_entry=entry
        )

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.version == 5
    unique_ids = {
        entity.unique_id
        for entity in er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    }
    assert "serial_light" in unique_ids
    assert not {"serial_alarm0", "serial_alarm3"} & unique_ids
