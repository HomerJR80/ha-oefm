"""Service-Handler für Öltank Manager."""
from __future__ import annotations

from datetime import datetime
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN
from .store import OilTankStore

SERVICE_ADD_REFILL = "add_refill"
SERVICE_ADD_CALIBRATION = "add_calibration"
SERVICE_DELETE_ENTRY = "delete_entry"

SCHEMA_ADD_REFILL = vol.Schema({
    vol.Required("liters_added"): vol.Coerce(float),
    vol.Optional("datetime"): str,
    vol.Optional("note", default=""): str,
})

SCHEMA_ADD_CALIBRATION = vol.Schema({
    vol.Required("current_level"): vol.Coerce(float),
    vol.Optional("datetime"): str,
    vol.Optional("note", default=""): str,
})

SCHEMA_DELETE_ENTRY = vol.Schema({
    vol.Required("entry_id"): str,
})


def _parse_datetime(dt_str: str | None) -> datetime:
    """String zu datetime oder jetzt."""
    if not dt_str:
        return datetime.now()
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return datetime.now()


async def async_setup_services(
    hass: HomeAssistant,
    store: OilTankStore
) -> None:
    """Services registrieren."""

    async def handle_add_refill(call: ServiceCall) -> None:
        data = SCHEMA_ADD_REFILL(dict(call.data))
        dt = _parse_datetime(data.get("datetime"))
        await store.async_add_refill(
            liters_added=data["liters_added"],
            dt=dt,
            note=data.get("note", "")
        )
        hass.bus.async_fire(f"{DOMAIN}_updated")

    async def handle_add_calibration(call: ServiceCall) -> None:
        data = SCHEMA_ADD_CALIBRATION(dict(call.data))
        dt = _parse_datetime(data.get("datetime"))
        await store.async_add_calibration(
            current_level=data["current_level"],
            dt=dt,
            note=data.get("note", "")
        )
        hass.bus.async_fire(f"{DOMAIN}_updated")

    async def handle_delete_entry(call: ServiceCall) -> None:
        data = SCHEMA_DELETE_ENTRY(dict(call.data))
        await store.async_delete_entry(data["entry_id"])
        hass.bus.async_fire(f"{DOMAIN}_updated")

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_REFILL,
        handle_add_refill, schema=SCHEMA_ADD_REFILL
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_CALIBRATION,
        handle_add_calibration, schema=SCHEMA_ADD_CALIBRATION
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_ENTRY,
        handle_delete_entry, schema=SCHEMA_DELETE_ENTRY
    )
