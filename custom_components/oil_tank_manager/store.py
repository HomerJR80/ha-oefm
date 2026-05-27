"""Datenspeicherung für Öltank Manager."""
from __future__ import annotations

import uuid
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

STORAGE_KEY = "oil_tank_manager"
STORAGE_VERSION = 1


class OilTankStore:
    """Verwaltet die persistente Datenspeicherung."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict = {"entries": []}

    async def async_load(self) -> None:
        """Daten laden."""
        data = await self._store.async_load()
        if data:
            self._data = data

    async def async_add_refill(
        self,
        liters_added: float,
        dt: datetime,
        note: str = ""
    ) -> dict:
        """Betankung hinzufügen."""
        entry = {
            "id": str(uuid.uuid4()),
            "type": "refill",
            "datetime": dt.isoformat(),
            "liters_added": liters_added,
            "note": note,
        }
        self._data["entries"].append(entry)
        await self._store.async_save(self._data)
        return entry

    async def async_add_calibration(
        self,
        current_level: float,
        dt: datetime,
        note: str = ""
    ) -> dict:
        """Füllstandsabgleich hinzufügen."""
        entry = {
            "id": str(uuid.uuid4()),
            "type": "calibration",
            "datetime": dt.isoformat(),
            "current_level": current_level,
            "note": note,
        }
        self._data["entries"].append(entry)
        await self._store.async_save(self._data)
        return entry

    async def async_delete_entry(self, entry_id: str) -> bool:
        """Eintrag löschen."""
        before = len(self._data["entries"])
        self._data["entries"] = [
            e for e in self._data["entries"] if e["id"] != entry_id
        ]
        if len(self._data["entries"]) < before:
            await self._store.async_save(self._data)
            return True
        return False

    @property
    def entries(self) -> list:
        """Alle Einträge sortiert nach Datum."""
        return sorted(
            self._data["entries"],
            key=lambda x: x["datetime"],
            reverse=True
        )

    @property
    def latest_calibration(self) -> dict | None:
        """Letzten Füllstandsabgleich holen."""
        calibrations = [
            e for e in self._data["entries"]
            if e["type"] == "calibration"
        ]
        if not calibrations:
            return None
        return max(calibrations, key=lambda x: x["datetime"])
