"""Öltank Manager - Sensoren."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfVolume

from .const import DOMAIN, CONF_TANK_SIZE, CONF_ENERGY_SENSOR, DEFAULT_LITERS_PER_KWH, LITERS_PER_KWH

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensoren einrichten."""
    tank_size = entry.options.get(CONF_TANK_SIZE) or entry.data.get(CONF_TANK_SIZE)

    # Bestehender Füllstandssensor
    level_sensor = OilTankLevelSensor(hass, entry.entry_id, tank_size)

    # Neue Verbrauchssensoren
    daily_sensor = OilTankDailyConsumptionSensor(hass, entry.entry_id)
    monthly_sensor = OilTankMonthlyConsumptionSensor(hass, entry.entry_id)
    yearly_sensor = OilTankYearlyConsumptionSensor(hass, entry.entry_id)
    range_sensor = OilTankRangeSensor(hass, entry.entry_id)

    all_sensors = [level_sensor, daily_sensor, monthly_sensor, yearly_sensor, range_sensor]
    async_add_entities(all_sensors)

    @callback
    def handle_update(event):
        for s in all_sensors:
            s.update_from_storage()
            s.async_write_ha_state()

    hass.bus.async_listen(f"{DOMAIN}_updated", handle_update)


# ─────────────────────────────────────────────
# BESTEHENDER SENSOR (unverändert)
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# NEUE SENSOREN
# ─────────────────────────────────────────────

class OilTankBaseSensor(SensorEntity):
    """Basis für Verbrauchssensoren."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._hass = hass
        self._entry_id = entry_id
        self._value = None
        self._attributes = {}

    def _get_consumption_data(self) -> dict:
        """Verbrauchsdaten aus hass.data holen."""
        return self._hass.data.get(DOMAIN, {}).get(self._entry_id, {}).get("consumption", {})

    def update_from_storage(self):
        """Wird bei jedem Update aufgerufen - von Unterklassen überschreiben."""
        pass

    @property
    def native_value(self):
        return self._value

    @property
    def extra_state_attributes(self):
        return self._attributes


class OilTankDailyConsumptionSensor(OilTankBaseSensor):
    """Tagesverbrauch in Litern."""

    def __init__(self, hass, entry_id):
        super().__init__(hass, entry_id)
        self._attr_name = "Öltank Tagesverbrauch"
        self._attr_unique_id = f"{entry_id}_daily_consumption"
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_device_class = SensorDeviceClass.VOLUME
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:oil"

    def update_from_storage(self):
        data = self._get_consumption_data()
        self._value = data.get("daily_liters")
        self._attributes = {
            "datum": datetime.now().strftime("%d.%m.%Y"),
            "saison": data.get("season"),
        }


class OilTankMonthlyConsumptionSensor(OilTankBaseSensor):
    """Monatsverbrauch in Litern."""

    def __init__(self, hass, entry_id):
        super().__init__(hass, entry_id)
        self._attr_name = "Öltank Monatsverbrauch"
        self._attr_unique_id = f"{entry_id}_monthly_consumption"
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_device_class = SensorDeviceClass.VOLUME
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:calendar-month"

    def update_from_storage(self):
        data = self._get_consumption_data()
        self._value = data.get("monthly_liters")
        self._attributes = {
            "monat": datetime.now().strftime("%B %Y"),
            "saison": data.get("season"),
        }


class OilTankYearlyConsumptionSensor(OilTankBaseSensor):
    """Jahresverbrauch in Litern."""

    def __init__(self, hass, entry_id):
        super().__init__(hass, entry_id)
        self._attr_name = "Öltank Jahresverbrauch"
        self._attr_unique_id = f"{entry_id}_yearly_consumption"
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_device_class = SensorDeviceClass.VOLUME
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:calendar-year"

    def update_from_storage(self):
        data = self._get_consumption_data()
        self._value = data.get("yearly_liters")
        self._attributes = {
            "jahr": datetime.now().year,
            "saison": data.get("season"),
        }


class OilTankRangeSensor(OilTankBaseSensor):
    """Reichweite in Tagen."""

    def __init__(self, hass, entry_id):
        super().__init__(hass, entry_id)
        self._attr_name = "Öltank Reichweite"
        self._attr_unique_id = f"{entry_id}_range_days"
        self._attr_native_unit_of_measurement = "Tage"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:calendar-clock"

    def update_from_storage(self):
        data = self._get_consumption_data()
        days = data.get("range_days")
        self._value = days
        empty_date = None
        if days is not None:
            empty_date = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
        self._attributes = {
            "saison": data.get("season"),
            "leer_am": empty_date,
            "tagesverbrauch_referenz": data.get("daily_reference"),
        }
