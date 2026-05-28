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

# Verbrauch
CONF_ENERGY_SENSOR = "energy_sensor"  # bereits vorhanden beim Setup
LITERS_PER_KWH = "liters_per_kwh"
DEFAULT_LITERS_PER_KWH = 8.715

# Storage Keys
STORAGE_KEY = "oil_tank_manager"
STORAGE_VERSION = 1

# Neue Storage Keys
STORAGE_MONTHLY_STATS = "monthly_stats"
STORAGE_ENERGY_BASELINE = "energy_baseline"  # kWh Wert bei Monatsstart

# Sensor Namen
SENSOR_FILL_LEVEL = "oltank_fullstand"
SENSOR_DAILY_CONSUMPTION = "oltank_tagesverbrauch"
SENSOR_MONTHLY_CONSUMPTION = "oltank_monatsverbrauch"
SENSOR_YEARLY_CONSUMPTION = "oltank_jahresverbrauch"
SENSOR_RANGE_DAYS = "oltank_reichweite"

# Jahreszeiten Monate
WINTER_MONTHS = [12, 1, 2]
TRANSITION_MONTHS = [3, 4, 10, 11]
SUMMER_MONTHS = [5, 6, 7, 8, 9]

SEASON_NAMES = {
    "winter": "Winter",
    "transition": "Übergang",
    "summer": "Sommer"
}
