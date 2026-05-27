# 🛢️ Öltank Manager für Home Assistant

![Version](https://img.shields.io/badge/Version-0.1.0-blue)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1+-orange)
![HACS](https://img.shields.io/badge/HACS-Custom%20Repository-green)

Eine Home Assistant Integration zur Verwaltung und Überwachung deines Heizöltanks.  
Verfolge deinen Füllstand, berechne deinen Verbrauch und behalte immer den Überblick über deine Heizölreserven.

---

## ✨ Features

- 📊 **Füllstandsanzeige** in Liter und Prozent
- 🔥 **Verbrauchsberechnung** basierend auf deinem Energiezähler
- 📅 **Verbrauchshistorie** (täglich, monatlich, jährlich)
- ⚠️ **Benachrichtigungen** bei niedrigem Füllstand
- 🏠 **Vollständige HA-Integration** via Config Flow (keine YAML-Konfiguration nötig)
- 🃏 **Lovelace Card** für eine übersichtliche Darstellung *(geplant)*

---

## 📋 Voraussetzungen

- Home Assistant 2024.1 oder neuer
- Ein Energiezähler-Sensor in Home Assistant (z.B. für deinen Ölkessel)
- [HACS](https://hacs.xyz/) installiert *(empfohlen)*

---

## 🚀 Installation

### Via HACS (empfohlen)

1. HACS öffnen → **Integrationen**
2. Oben rechts: ⋮ → **Benutzerdefinierte Repositories**
3. URL eintragen:
   ```
   https://github.com/DEIN-USERNAME/ha-oefm
   ```
4. Kategorie: **Integration** → **Hinzufügen**
5. Integration suchen: `Öltank Manager` → **Installieren**
6. Home Assistant neu starten

### Manuell

1. Dieses Repository herunterladen
2. Ordner `custom_components/oil_tank_manager/` nach  
   `/config/custom_components/oil_tank_manager/` kopieren
3. Home Assistant neu starten

---

## ⚙️ Einrichtung

1. **Einstellungen** → **Integrationen** → **+ Hinzufügen**
2. Suche nach `Öltank` oder `oil_tank`
3. Integration auswählen und Formular ausfüllen:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| Tankgröße | Maximales Fassungsvermögen in Liter | `3000` |
| Energiezähler | Sensor aus Home Assistant | `sensor.ölkessel_energie` |
| Verbrauchsfaktor | kWh pro Liter Heizöl | `10.0` |

4. **Bestätigen** → Integration ist bereit!

---

## 📡 Sensoren

Nach der Einrichtung stehen folgende Sensoren zur Verfügung:

| Sensor | Beschreibung | Einheit |
|--------|-------------|---------|
| `sensor.öltank_füllstand` | Aktueller Füllstand | Liter |
| `sensor.öltank_füllstand_prozent` | Füllstand in Prozent | % |
| `sensor.öltank_verbrauch_heute` | Verbrauch heute | Liter |
| `sensor.öltank_verbrauch_monat` | Verbrauch diesen Monat | Liter |

---

## 🗂️ Projektstruktur

```
custom_components/
└── oil_tank_manager/
    ├── __init__.py          # Integration Setup
    ├── manifest.json        # Metadaten
    ├── config_flow.py       # GUI Einrichtung
    ├── sensor.py            # Sensoren & Berechnungen
    ├── storage.py           # Datenspeicherung
    ├── services.yaml        # HA Services
    └── translations/
        └── de.json          # Deutsche Übersetzungen
```

---

## 🛠️ Entwicklung

```bash
# Repository klonen
git clone https://github.com/DEIN-USERNAME/ha-oefm.git
cd ha-oefm

# Änderungen committen
git add .
git commit -m "feat: Beschreibung der Änderung"
git push origin main
```

### Versionen

| Version | Beschreibung |
|---------|-------------|
| 0.1.0 | Grundstruktur & Config Flow |
| 0.2.0 | Sensor & Verbrauchsberechnung *(in Entwicklung)* |

---

## 🐛 Fehler melden

Fehler oder Verbesserungsvorschläge bitte als  
[GitHub Issue](https://github.com/DEIN-USERNAME/ha-oefm/issues) melden.

**Hilfreiche Infos beim Melden:**
- Home Assistant Version
- Fehlermeldung aus den Protokollen
- Schritte zur Reproduktion

---

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

## 👤 Autor

Erstellt mit ❤️ für Home Assistant  
GitHub: [@DEIN-USERNAME](https://github.com/DEIN-USERNAME)
