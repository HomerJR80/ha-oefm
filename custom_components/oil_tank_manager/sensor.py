"""Öltank Manager - Sensoren."""
from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity

from . import DOMAIN, CONF_TANK_SIZE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensoren einrichten."""
    tank_size = entry.data[CONF_TANK_SIZE]

    async_add_entities([
        OilTankLevelSensor(entry.entry_id, tank_size),
    ])


class OilTankLevelSensor(SensorEntity):
    """Sensor für den Füllstand."""

    def __init__(self, entry_id: str, tank_size: int) -> None:
        self._entry_id = entry_id
        self._tank_size = tank_size
        self._attr_name = "Öltank Füllstand"
        self._attr_unique_id = f"{entry_id}_fuel_level"
        self._attr_native_unit_of_measurement = "L"
        self._attr_icon = "mdi:barrel"
        self._attr_native_value = None

    @property
    def extra_state_attributes(self):
        return {
            "tank_size": self._tank_size,
        }
