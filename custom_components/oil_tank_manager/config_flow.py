"""Config Flow & Options Flow für Öltank Manager."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_TANK_SIZE,
    CONF_ENERGY_SENSOR,
    CONF_KWH_PER_LITER,
    DEFAULT_KWH_PER_LITER,
    DEFAULT_TANK_SIZE,
)

_LOGGER = logging.getLogger(__name__)


def _build_schema(
    tank_size: int = DEFAULT_TANK_SIZE,
    energy_sensor: str = "",
    kwh_per_liter: float = DEFAULT_KWH_PER_LITER,
    show_energy_selector: bool = True,
) -> vol.Schema:
    """Formular-Schema aufbauen."""
    fields = {}

    fields[vol.Required(CONF_TANK_SIZE, default=tank_size)] = selector.selector(
        {
            "number": {
                "min": 100,
                "max": 100000,
                "step": 100,
                "unit_of_measurement": "L",
                "mode": "box",
            }
        }
    )

    if show_energy_selector:
        fields[
            vol.Required(
                CONF_ENERGY_SENSOR,
                default=energy_sensor if energy_sensor else vol.UNDEFINED,
            )
        ] = selector.selector(
            {
                "entity": {
                    "domain": "sensor",
                    "device_class": "energy",
                    "multiple": False,
                }
            }
        )

    fields[
        vol.Optional(CONF_KWH_PER_LITER, default=kwh_per_liter)
    ] = selector.selector(
        {
            "number": {
                "min": 5.0,
                "max": 15.0,
                "step": 0.1,
                "unit_of_measurement": "kWh/L",
                "mode": "box",
            }
        }
    )

    return vol.Schema(fields)


# ── Haupt Config Flow ────────────────────────────────────────────────
class OilTankConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Einrichtungsassistent."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Öltank Manager",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OilTankOptionsFlow(config_entry)


# ── Options Flow ─────────────────────────────────────────────────────
class OilTankOptionsFlow(config_entries.OptionsFlow):
    """Einstellungen nachträglich ändern."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_input(user_input)
            if not errors:
                return self.async_create_entry(
                    title="",
                    data={
                        **self.config_entry.data,
                        **user_input,
                    },
                )

        current = self.config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                tank_size=current.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE),
                energy_sensor=current.get(CONF_ENERGY_SENSOR, ""),
                kwh_per_liter=current.get(CONF_KWH_PER_LITER, DEFAULT_KWH_PER_LITER),
                show_energy_selector=True,
            ),
            errors=errors,
        )


# ── Validierung ──────────────────────────────────────────────────────
def _validate_input(user_input: dict) -> dict[str, str]:
    errors: dict[str, str] = {}
    tank_size = user_input.get(CONF_TANK_SIZE, 0)
    kwh = user_input.get(CONF_KWH_PER_LITER, DEFAULT_KWH_PER_LITER)

    if not isinstance(tank_size, (int, float)) or tank_size < 100:
        errors[CONF_TANK_SIZE] = "invalid_tank_size"
    if not isinstance(kwh, (int, float)) or not (5.0 <= kwh <= 15.0):
        errors[CONF_KWH_PER_LITER] = "invalid_kwh"

    return errors
