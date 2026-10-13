"""Light entities for Somneo."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SomneoConfigEntry
from .entity import SomneoEntity

# The Somneo has 25 light levels, lower brightnesses would round down to 0.
MIN_BRIGHTNESS = 11


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo light from config_entry."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            SomneoLight(coordinator, "light"),
            SomneoNightLight(coordinator, "nightlight"),
        ]
    )


class SomneoLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_translation_key = "normal_light"

    @property
    def is_on(self) -> bool:
        """Return if the light is on."""
        return self.coordinator.data["light_is_on"]

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self.coordinator.data["light_brightness"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness is not None:
            brightness = max(brightness, MIN_BRIGHTNESS)
        await self.coordinator.async_toggle_light(True, brightness=brightness)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_toggle_light(False)


class SomneoNightLight(SomneoEntity, LightEntity):
    """Representation of an Somneo Night light."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_translation_key = "night_light"

    @property
    def is_on(self) -> bool:
        """Return if the night light is on."""
        return self.coordinator.data["nightlight_is_on"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        await self.coordinator.async_toggle_nightlight(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self.coordinator.async_toggle_nightlight(False)
