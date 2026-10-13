"""Select entities for Somneo."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import EVERYDAY, TOMORROW, WEEKEND, WORKDAYS
from .coordinator import SomneoConfigEntry
from .entity import SomneoWakeupEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            SomneoWakeupDays(coordinator, "days"),
            SomneoWakeupTheme(coordinator, "theme"),
            SomneoWakeupSound(coordinator, "sound"),
        ]
    )


class SomneoWakeupSelect(SomneoWakeupEntity, SelectEntity):
    """Base class for a setting of the wake-up alarm with options."""

    @property
    def current_option(self) -> str | None:
        """Return the selected option."""
        option = str(self._value).replace(" ", "_")
        return option if option in self.options else None


class SomneoWakeupDays(SomneoWakeupSelect):
    """Representation of the days of the wake-up alarm."""

    # Other combinations of days can only be set in the SleepMapper app.
    _attr_options = [EVERYDAY, WORKDAYS, WEEKEND, TOMORROW]

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_wakeup(days=option)


class SomneoWakeupTheme(SomneoWakeupSelect):
    """Representation of the light theme of the wake-up alarm."""

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return [item.replace(" ", "_") for item in self.coordinator.light_themes]

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_wakeup_light(theme=option.replace("_", " "))


class SomneoWakeupSound(SomneoWakeupSelect):
    """Representation of the sound of the wake-up alarm."""

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        return [item.replace(" ", "_") for item in self.coordinator.sounds]

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_wakeup_sound(sound=option.replace("_", " "))
