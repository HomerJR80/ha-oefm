"""Verbrauchsberechnung für Oil Tank Manager."""
import logging
from datetime import datetime, timedelta
from typing import Optional

_LOGGER = logging.getLogger(__name__)

WINTER_MONTHS = [12, 1, 2]
TRANSITION_MONTHS = [3, 4, 10, 11]
SUMMER_MONTHS = [5, 6, 7, 8, 9]


def get_season(month: int) -> str:
    if month in WINTER_MONTHS:
        return "winter"
    elif month in TRANSITION_MONTHS:
        return "transition"
    return "summer"


class ConsumptionTracker:
    """Verwaltet Verbrauchsdaten und Berechnungen."""

    def __init__(self, store_data: dict, liters_per_kwh: float):
        self._data = store_data
        self._liters_per_kwh = liters_per_kwh

        # Sicherstellen dass Struktur vorhanden
        if "monthly_stats" not in self._data:
            self._data["monthly_stats"] = {}
        if "energy_baseline" not in self._data:
            self._data["energy_baseline"] = {}

    def update(self, current_kwh: float, current_date: datetime) -> dict:
        """
        Hauptmethode - bei jedem Update aufrufen.
        Gibt berechnete Werte zurück.
        """
        month_key = current_date.strftime("%Y-%m")
        day_key = current_date.strftime("%Y-%m-%d")

        # Baseline für diesen Monat setzen falls nicht vorhanden
        if month_key not in self._data["energy_baseline"]:
            self._data["energy_baseline"][month_key] = {
                "start_kwh": current_kwh,
                "start_date": day_key
            }
            _LOGGER.info(f"Neue Monats-Baseline gesetzt: {month_key} = {current_kwh} kWh")

        # Tagesbaseline
        if "day_baseline" not in self._data:
            self._data["day_baseline"] = {}

        if day_key not in self._data["day_baseline"]:
            # Neuer Tag - gestern abschließen
            self._close_yesterday(current_kwh, current_date)
            self._data["day_baseline"][day_key] = current_kwh
            # Alte Tagesbaselines aufräumen (nur letzte 400 Tage behalten)
            self._cleanup_day_baselines(current_date)

        # Berechnungen
        daily = self._calc_daily(current_kwh, day_key)
        monthly = self._calc_monthly(current_kwh, month_key)
        yearly = self._calc_yearly(current_kwh, current_date)
        range_days = self._calc_range(current_date)
        season = get_season(current_date.month)

        # Monatsstats aktualisieren
        self._update_monthly_stats(monthly, month_key)

        return {
            "daily_liters": round(daily, 1),
            "monthly_liters": round(monthly, 1),
            "yearly_liters": round(yearly, 1),
            "range_days": range_days,
            "season": season,
            "liters_per_kwh": self._liters_per_kwh,
        }

    def _calc_daily(self, current_kwh: float, day_key: str) -> float:
        baseline = self._data["day_baseline"].get(day_key, current_kwh)
        delta = max(0, current_kwh - baseline)
        return delta * self._liters_per_kwh

    def _calc_monthly(self, current_kwh: float, month_key: str) -> float:
        baseline = self._data["energy_baseline"].get(month_key, {})
        start_kwh = baseline.get("start_kwh", current_kwh)
        delta = max(0, current_kwh - start_kwh)
        return delta * self._liters_per_kwh

    def _calc_yearly(self, current_kwh: float, current_date: datetime) -> float:
        year = str(current_date.year)
        total = 0.0
        for month_key, baseline in self._data["energy_baseline"].items():
            if not month_key.startswith(year):
                continue
            # Letzten bekannten Monatsverbrauch nehmen
            stats = self._data["monthly_stats"].get(month_key, {})
            if month_key == current_date.strftime("%Y-%m"):
                # Aktueller Monat - live berechnen
                total += max(0, current_kwh - baseline.get("start_kwh", current_kwh))
            else:
                total += stats.get("kwh", 0)
        return total * self._liters_per_kwh

    def _calc_range(self, current_date: datetime) -> Optional[int]:
        """Reichweite in Tagen berechnen."""
        from homeassistant.core import HomeAssistant  # wird von außen gesetzt
        fill_level = self._data.get("fill_level", 0)
        if fill_level <= 0:
            return 0

        avg_daily = self._get_reference_daily_consumption(current_date)
        if avg_daily is None or avg_daily <= 0:
            return None

        return round(fill_level / avg_daily)

    def _get_reference_daily_consumption(self, current_date: datetime) -> Optional[float]:
        """
        Referenz-Tagesverbrauch ermitteln.
        Priorität: Vorjahresdaten gleicher Monat → verfügbare Daten gleiche Saison → 30-Tage-Schnitt
        """
        current_month = current_date.month
        current_season = get_season(current_month)

        # Vorjahr gleicher Monat
        last_year_key = f"{current_date.year - 1}-{current_date.month:02d}"
        if last_year_key in self._data["monthly_stats"]:
            stats = self._data["monthly_stats"][last_year_key]
            days = stats.get("days", 30)
            liter = stats.get("liter", 0)
            if liter > 0 and days > 0:
                _LOGGER.debug(f"Reichweite basiert auf Vorjahr {last_year_key}")
                return liter / days

        # Gleiche Saison aus verfügbaren Daten
        season_liters = []
        for month_key, stats in self._data["monthly_stats"].items():
            try:
                month_num = int(month_key.split("-")[1])
                if get_season(month_num) == current_season:
                    days = stats.get("days", 30)
                    liter = stats.get("liter", 0)
                    if liter > 0 and days > 0:
                        season_liters.append(liter / days)
            except (ValueError, IndexError):
                continue

        if season_liters:
            avg = sum(season_liters) / len(season_liters)
            _LOGGER.debug(f"Reichweite basiert auf Saison {current_season}: {avg:.1f} L/Tag")
            return avg

        # Fallback: 30-Tage-Schnitt aus Tagesdaten
        return self._get_30day_average(current_date)

    def _get_30day_average(self, current_date: datetime) -> Optional[float]:
        """Durchschnitt der letzten 30 Tage."""
        daily_data = self._data.get("day_baseline", {})
        if len(daily_data) < 2:
            return None

        # Sortierte Tage
        sorted_days = sorted(daily_data.keys())[-31:]
        if len(sorted_days) < 2:
            return None

        total_liter = 0
        count = 0
        for i in range(1, len(sorted_days)):
            kwh_start = daily_data[sorted_days[i-1]]
            kwh_end = daily_data[sorted_days[i]]
            delta = max(0, kwh_end - kwh_start) * self._liters_per_kwh
            total_liter += delta
            count += 1

        if count == 0:
            return None

        avg = total_liter / count
        _LOGGER.debug(f"Reichweite basiert auf 30-Tage-Schnitt: {avg:.1f} L/Tag")
        return avg

    def _close_yesterday(self, current_kwh: float, current_date: datetime):
        """Gestrigen Tag in monthly_stats abschließen."""
        yesterday = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_month = yesterday[:7]

        if yesterday in self._data["day_baseline"]:
            kwh_start = self._data["day_baseline"][yesterday]
            # Monatsende - current_kwh ist Mitternacht = Ende von gestern
            kwh_delta = max(0, current_kwh - kwh_start)
            liter = kwh_delta * self._liters_per_kwh

            if yesterday_month not in self._data["monthly_stats"]:
                self._data["monthly_stats"][yesterday_month] = {
                    "kwh": 0, "liter": 0, "days": 0
                }

            self._data["monthly_stats"][yesterday_month]["kwh"] += kwh_delta
            self._data["monthly_stats"][yesterday_month]["liter"] += liter
            self._data["monthly_stats"][yesterday_month]["days"] += 1

    def _update_monthly_stats(self, monthly_liters: float, month_key: str):
        """Aktuellen Monatsstand für Referenz speichern."""
        if month_key not in self._data["monthly_stats"]:
            self._data["monthly_stats"][month_key] = {
                "kwh": 0, "liter": 0, "days": 0
            }
        # Live-Wert setzen (wird täglich überschrieben bis Monat endet)
        self._data["monthly_stats"][month_key]["liter_current"] = monthly_liters

    def _cleanup_day_baselines(self, current_date: datetime):
        """Alte Tagesbaselines löschen (> 400 Tage)."""
        cutoff = (current_date - timedelta(days=400)).strftime("%Y-%m-%d")
        to_delete = [k for k in self._data["day_baseline"] if k < cutoff]
        for k in to_delete:
            del self._data["day_baseline"][k]

    def set_fill_level(self, liters: float):
        """Füllstand für Reichweiten-Berechnung setzen."""
        self._data["fill_level"] = liters

    def get_data(self) -> dict:
        """Aktuelle Daten für Storage zurückgeben."""
        return self._data
