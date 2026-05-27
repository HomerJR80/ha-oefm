"""Öltank Manager - Sensoren."""
from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, CONF_TANK_SIZE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensoren einrichten."""
    tank_size = entry.options.get(CONF_TANK_SIZE) or entry.data.get(CONF_TANK_SIZE)

    sensor = OilTankLevelSensor(hass, entry.entry_id, tank_size)
    async_add_entities([sensor])

    @callback
    def handle_update(event):
        sensor.update_from_storage()
        sensor.async_write_ha_state()

    hass.bus.async_listen(f"{DOMAIN}_updated", handle_update)


class OilTankLevelSensor(SensorEntity):
    """Sensor für den Füllstand."""

    def __init__(self, hass: HomeAssistant, entry_id: str, tank_size: int) -> None:
        self._hass = hass
        self._entry_id = entry_id
        self._tank_size = tank_size
        self._attr_name = "Öltank Füllstand"
        self._attr_unique_id = f"{entry_id}_fuel_level"
        self._attr_native_unit_of_measurement = "L"
        self._attr_icon = "mdi:barrel"
        self._attr_native_value = None

    def update_from_storage(self):
        """Füllstand aus gespeicherten Daten berechnen."""
        domain_data = self._hass.data.get(DOMAIN, {}).get(self._entry_id, {})
        store = domain_data.get("store")

        if store is None:
            _LOGGER.warning("Store nicht gefunden!")
            return

        entries = sorted(
            store.data.get("entries", []),
            key=lambda x: x["datetime"]
        )

        if not entries:
            _LOGGER.debug("Keine Einträge vorhanden")
            return

        level = None
        for entry in entries:
            if entry["type"] == "calibration":
                level = entry["current_level"]
            elif entry["type"] == "refill" and level is not None:
                level += entry["liters_added"]

        self._attr_native_value = level
        _LOGGER.debug("Füllstand berechnet: %s L", level)

    @property
    def extra_state_attributes(self):
        return {
            "tank_size": self._tank_size,
        }
