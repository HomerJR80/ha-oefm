"""Öltank Manager Integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .store import OilTankStore
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


def _calculate_consumption(entries: list, tank_size: int) -> dict:
    """Verbrauch aus Einträgen berechnen."""
    if not entries:
        return {}

    sorted_entries = sorted(entries, key=lambda x: x["datetime"])

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    # Aktuellen Füllstand berechnen
    current_level = None
    for entry in sorted_entries:
        if entry["type"] == "calibration":
            current_level = entry["current_level"]
        elif entry["type"] == "refill" and current_level is not None:
            current_level += entry["liters_added"]

    if current_level is None:
        return {}

    # Verbrauchsberechnung über Zeiträume
    def calc_consumption_since(since_str: str) -> float | None:
        """Verbrauch seit einem Zeitpunkt berechnen."""
        # Füllstand zum Startzeitpunkt rekonstruieren
        level_at_start = None
        last_known_level = None
        last_known_time = None

        for entry in sorted_entries:
            entry_time = datetime.fromisoformat(entry["datetime"])

            if entry_time <= datetime.fromisoformat(since_str):
                # Letzter bekannter Stand vor Startzeitpunkt
                if entry["type"] == "calibration":
                    last_known_level = entry["current_level"]
                    last_known_time = entry_time
                elif entry["type"] == "refill" and last_known_level is not None:
                    last_known_level += entry["liters_added"]
                    last_known_time = entry_time
            else:
                # Erster Eintrag nach Startzeitpunkt
                if level_at_start is None:
                    level_at_start = last_known_level
                if entry["type"] == "calibration":
                    last_known_level = entry["current_level"]
                elif entry["type"] == "refill" and last_known_level is not None:
                    last_known_level += entry["liters_added"]

        if level_at_start is None:
            level_at_start = last_known_level

        if level_at_start is None:
            return None

        consumed = level_at_start - current_level
        return round(max(consumed, 0), 1)

    daily = calc_consumption_since(today_start.isoformat())
    monthly = calc_consumption_since(month_start.isoformat())
    yearly = calc_consumption_since(year_start.isoformat())

    # Reichweite berechnen (basierend auf 30-Tage Durchschnitt)
    range_days = None
    daily_reference = None
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    consumption_30d = calc_consumption_since(thirty_days_ago)

    if consumption_30d and consumption_30d > 0:
        daily_reference = round(consumption_30d / 30, 2)
        if daily_reference > 0 and current_level is not None:
            range_days = int(current_level / daily_reference)

    # Saison bestimmen
    month = now.month
    if month in (12, 1, 2):
        season = "Winter"
    elif month in (3, 4, 5):
        season = "Frühling"
    elif month in (6, 7, 8):
        season = "Sommer"
    else:
        season = "Herbst"

    return {
        "daily_liters": daily,
        "monthly_liters": monthly,
        "yearly_liters": yearly,
        "range_days": range_days,
        "daily_reference": daily_reference,
        "season": season,
    }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # Store initialisieren & laden
    store = OilTankStore(hass)
    await store.async_load()

    # Verbrauch initial berechnen
    tank_size = entry.options.get("tank_size") or entry.data.get("tank_size", 0)
    entries = store.data.get("entries", [])
    consumption = _calculate_consumption(entries, tank_size)

    hass.data[DOMAIN][entry.entry_id] = {
        "store": store,
        "config": {**entry.data, **entry.options},
        "consumption": consumption,
    }

    # Services registrieren
    await async_setup_services(hass, store)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Bei jedem Storage-Update Verbrauch neu berechnen
    async def handle_storage_update(event):
        entries = store.data.get("entries", [])
        hass.data[DOMAIN][entry.entry_id]["consumption"] = _calculate_consumption(
            entries, tank_size
        )
        _LOGGER.debug("Verbrauch neu berechnet: %s", hass.data[DOMAIN][entry.entry_id]["consumption"])

    hass.bus.async_listen(f"{DOMAIN}_updated", handle_storage_update)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
