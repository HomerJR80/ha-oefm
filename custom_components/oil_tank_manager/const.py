"""Konstanten für Öltank Manager."""

DOMAIN = "oil_tank_manager"

# Config Schlüssel
CONF_TANK_SIZE = "tank_size"
CONF_ENERGY_SENSOR = "energy_sensor"
CONF_KWH_PER_LITER = "kwh_per_liter"

# Services
SERVICE_ADD_REFILL = "add_refill"
SERVICE_ADD_CALIBRATION = "add_calibration"
SERVICE_DELETE_ENTRY = "delete_entry"

# Standardwerte
DEFAULT_TANK_SIZE = 3000
DEFAULT_KWH_PER_LITER = 10.0
