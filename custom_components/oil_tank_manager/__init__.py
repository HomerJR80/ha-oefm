"""Öltank Manager Integration."""
from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

DOMAIN = "oil_tank_manager"

# ── Konfigurationsschlüssel ──────────────────────────────────────────
CONF_TANK_SIZE      = "tank_size"
CONF_ENERGY_SENSOR  = "energy_sensor"
CONF_KWH_PER_LITER  = "kwh_per_liter"

# ── Standardwerte ────────────────────────────────────────────────────
DEFAULT_KWH_PER_LITER = 10.0
DEFAULT_TANK_SIZE     = 3000

# ── Plattformen ──────────────────────────────────────────────────────
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration einrichten."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
    }

    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info(
        "Öltank Manager gestartet | Tank: %s L | Sensor: %s",
        entry.data.get(CONF_TANK_SIZE),
        entry.data.get(CONF_ENERGY_SENSOR),
    )
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Wird aufgerufen wenn Optionen geändert werden."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entfernen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Öltank Manager entfernt")
    return unload_ok
