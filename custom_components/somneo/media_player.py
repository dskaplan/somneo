"""Media player entities for Somneo."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SomneoConfigEntry
from .entity import SomneoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo media player from config_entry."""
    async_add_entities([SomneoMediaPlayer(config_entry.runtime_data, "player")])


class SomneoMediaPlayer(SomneoEntity, MediaPlayerEntity):
    """Representation of an Somneo Media player."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_translation_key = "player"

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        if self.coordinator.data["player"]["state"]:
            return MediaPlayerState.ON
        return MediaPlayerState.OFF

    @property
    def volume_level(self) -> float:
        """Return the volume level of the player."""
        return self.coordinator.data["player"]["volume"]

    @property
    def source(self) -> str:
        """Return the current source."""
        return self.coordinator.data["player"]["source"]

    @property
    def source_list(self) -> list[str]:
        """Return the available sources."""
        return self.coordinator.data["player"]["possible_sources"]

    async def async_turn_on(self) -> None:
        """Turn the player on."""
        await self.coordinator.async_player_toggle(True)

    async def async_turn_off(self) -> None:
        """Turn the player off."""
        await self.coordinator.async_player_toggle(False)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the volume level."""
        await self.coordinator.async_set_player_volume(volume)

    async def async_select_source(self, source: str) -> None:
        """Select a source."""
        await self.coordinator.async_set_player_source(source)
