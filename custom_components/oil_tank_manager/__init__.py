"""Öltank Manager Integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .store import OilTankStore
from .services import async_setup_services

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # Store initialisieren & laden
    store = OilTankStore(hass)
    await store.async_load()

    hass.data[DOMAIN][entry.entry_id] = {
        "store": store,
        "config": {**entry.data, **entry.options},
    }

    # Services registrieren
    await async_setup_services(hass, store)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
