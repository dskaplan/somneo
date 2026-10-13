"""Sensor entities for Somneo."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfSoundPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATUSES
from .coordinator import SomneoConfigEntry, SomneoCoordinator
from .entity import SomneoEntity

SENSORS = (
    SensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="luminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="noise",
        device_class=SensorDeviceClass.SOUND_PRESSURE,
        native_unit_of_measurement=UnitOfSoundPressure.DECIBEL,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SomneoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        [
            *(SomneoSensor(coordinator, description) for description in SENSORS),
            SomneoNextAlarmSensor(coordinator, "next"),
            SomneoStatusSensor(coordinator, "alarm_status"),
        ]
    )


class SomneoSensor(SomneoEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self, coordinator: SomneoCoordinator, description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data[self.entity_description.key]


class SomneoNextAlarmSensor(SomneoEntity, SensorEntity):
    """Representation of a Next alarm sensor."""

    _attr_translation_key = "next_alarm"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the time of the next alarm."""
        return self.coordinator.data["next_alarm"]


class SomneoStatusSensor(SomneoEntity, SensorEntity):
    """Sensor entity that provides what the Somneo is currently doing."""

    _attr_translation_key = "status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUSES

    @property
    def native_value(self) -> str:
        """Return the status."""
        return self.coordinator.data["status"]
