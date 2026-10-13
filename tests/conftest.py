"""Fixtures for the Somneo tests."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.somneo.const import DOMAIN

PROFILE = {
    "prfnr": 1, "prfen": False, "prfvs": True, "pname": "",
    "ayear": 0, "amnth": 0, "alday": 0, "daynm": 254, "almhr": 7, "almmn": 30,
    "curve": 20, "durat": 30, "ctype": 0, "snddv": "wus", "sndch": "1",
    "sndlv": 12, "sndss": 0, "pwrsz": 0, "pszhr": 0, "pszmn": 0,
}  # fmt: skip


class FakeClient:
    """Somneo client answering with data captured from a HF3670/60."""

    def __init__(self, *_: Any, **__: Any) -> None:
        """Initialize the fake client."""
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.status = 1

    def get_themes(self) -> dict[str, dict[str, int]]:
        return {
            "wake_light": {
                "sunny day": 0, "island red": 1, "nordic white": 2, "caribbean red": 3,
            },
            "dusk_light": {"sunny day": 0},
            "wake_sound": {"forest birds": 1, "summer birds": 2, "ocean waves": 8},
            "dusk_sound": {"soft rain": 1},
        }  # fmt: skip

    def get_sensor_data(self) -> dict[str, Any]:
        return {"temperature": 23.3, "humidity": 48.6, "luminance": 0.1, "noise": 37}

    def get_alarm_status(self) -> dict[str, Any]:
        return {"wusts": self.status, "brght": 4, "dspon": False}

    def get_light_data(self) -> dict[str, Any]:
        return {"ltlvl": 25, "onoff": False, "ctype": 0, "tempy": False, "ngtlt": False}

    def get_sunset_data(self) -> dict[str, Any]:
        return {
            "durat": 30, "onoff": False, "curve": 20, "ctype": 0,
            "snddv": "dus", "sndch": "1", "sndlv": 12,
        }  # fmt: skip

    def get_enabled_alarms(self) -> dict[str, Any]:
        return {"prfen": [False] * 16, "prfvs": [True] * 16, "pwrsv": [0] * 48}

    def get_time_alarms(self) -> dict[str, Any]:
        return {"daynm": [254] * 16, "almhr": [7] * 16, "almmn": [30] * 16}

    def get_snooze_time(self) -> dict[str, Any]:
        return {"snztm": 9}

    def get_player_status(self) -> dict[str, Any]:
        return {"onoff": False, "sdvol": 8, "snddv": "dus", "sndch": "1"}

    def _record(self, port: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((port, dict(payload)))
        return dict(payload)

    def modify_alarm_details(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("wualm", dict(payload)))
        return dict(PROFILE)

    def modify_alarm_wake_up_configuration(self, payload: dict[str, Any]) -> dict:
        return self._record("wualm/prfwu", payload)

    def modify_running_alarm(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._record("wualm/alctr", payload)

    def modify_light(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._record("wulgt", payload)

    def modify_player(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._record("wuply", payload)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations."""


@pytest.fixture
def client():
    """Patch the Somneo client."""
    fake = FakeClient()
    with (
        patch("pysomneo.somneo.SomneoClient", return_value=fake),
        patch("pysomneo.somneo.time.sleep"),
    ):
        yield fake


@pytest.fixture
async def entry(hass, client) -> MockConfigEntry:
    """Set up the integration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="serial",
        version=5,
        data={
            "host": "192.0.2.1",
            "name": "Somneo",
            "dev_info": {
                "manufacturer": "Royal Philips Electronics",
                "model": "Wake-up Light",
                "modelnumber": "HF367x",
                "serial": "serial",
            },
        },
        options={"session": True},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
