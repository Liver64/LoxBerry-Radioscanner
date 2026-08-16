[![LoxBerry Plugin](https://img.shields.io/badge/LoxBerry-Plugin-blue)](https://www.loxberry.de/)
[![GitHub release](https://img.shields.io/github/v/release/Liver64/LoxBerry-Radioscanner?include_prereleases)](https://github.com/Liver64/LoxBerry-Radioscanner/releases)
[![GitHub issues](https://img.shields.io/github/issues/Liver64/LoxBerry-Radioscanner)](https://github.com/Liver64/LoxBerry-Radioscanner/issues)
[![License](https://img.shields.io/github/license/Liver64/LoxBerry-Radioscanner)](https://github.com/Liver64/LoxBerry-Radioscanner/blob/master/LICENSE)

# RadioScanner für LoxBerry

**RadioScanner** ist ein LoxBerry-Plugin zum Empfang und zur Auswertung drahtloser Sensoren im ISM-Band mit einem kompatiblen **RTL-SDR USB-Dongle**.

Das Plugin basiert auf den Open-Source-Projekten **rtl-sdr** und **rtl_433**. Empfangene Sensordaten werden über MQTT bereitgestellt und können dadurch unter anderem in Loxone oder anderen Smart-Home-Systemen weiterverarbeitet werden.

## Funktionen

* Unterstützung von RTL-SDR USB-Dongles
* Empfang zahlreicher von `rtl_433` unterstützter Sensoren und Funkprotokolle
* Ausgabe der empfangenen Sensordaten über MQTT
* Auswahl einzelner Sensorprotokolle
* Konfiguration mehrerer Empfangsfrequenzen
* Einstellbares Frequency Hopping
* Einstellbare Sample Rate
* Erkennung angeschlossener RTL-SDR-Dongles
* Änderung der Dongle-Seriennummer
* Scanner-Funktion über den Terminal-Befehl `rascanner`
* Betrieb von `rtl_433` als systemd-Service
* Webbasierte Konfiguration über die LoxBerry-Oberfläche
* Deutsch- und englischsprachige Benutzeroberfläche
* LoxBerry AutoUpdate-Unterstützung

## Voraussetzungen

* **LoxBerry 3.0 oder neuer**
* Ein von `rtl-sdr` unterstützter RTL-SDR USB-Dongle
* Funktionierende MQTT-Konfiguration auf dem LoxBerry
* Internetzugang während der Plugin-Installation bzw. eines Updates

Während der Installation werden `rtl-sdr` und `rtl_433` aus ihren jeweiligen Quellcode-Repositories geladen und lokal kompiliert.

## Installation

1. Die aktuelle ZIP-Datei unter [Releases](https://github.com/Liver64/LoxBerry-Radioscanner/releases) herunterladen.
2. In LoxBerry die **Plugin-Verwaltung** öffnen.
3. Die ZIP-Datei als neues Plugin installieren.
4. Nach Abschluss der Installation den LoxBerry bei Aufforderung neu starten.
5. Den RTL-SDR USB-Dongle anschließen.
6. **Radio Scanner** über das LoxBerry-Menü öffnen.
7. Gewünschte Frequenzen, Sample Rate und Sensorprotokolle konfigurieren.
8. Einstellungen speichern.

Nach dem ersten Speichern der Konfiguration wird `rtl_433` mit der erzeugten Konfiguration gestartet.

## MQTT

Die empfangenen Daten werden von `rtl_433` direkt an den in LoxBerry konfigurierten MQTT-Broker übertragen.

Die MQTT-Topics werden nach folgendem Schema erzeugt:

```text
rtl_433[/protocol][/model][/id]
```

Wird in der Plugin-Oberfläche keine Einschränkung auf bestimmte Sensorprotokolle vorgenommen, werden alle empfangenen und von `rtl_433` erkannten Sensoren an MQTT ausgegeben.

## Scanner

Für die Suche nach empfangbaren Geräten steht der Terminal-Befehl

```bash
rascanner
```

zur Verfügung.

Das Terminal kann auf dem LoxBerry unter folgendem Pfad geöffnet werden:

```text
http://loxberry-neu/admin/system/tools/terminal/
```

Alternativ kann eine SSH-Verbindung zum LoxBerry verwendet werden.

## RTL-SDR Dongles

Das Plugin erkennt angeschlossene RTL-SDR-Geräte automatisch.

Bei Verwendung mehrerer Dongles kann über die Plugin-Oberfläche die jeweilige Seriennummer angepasst werden. Dadurch lassen sich die Geräte dauerhaft eindeutig zuordnen.

> [!NOTE]
> Es werden ausschließlich RTL-SDR-kompatible Dongles unterstützt.

## Frequenzen und Protokolle

RadioScanner kann auf einer oder mehreren konfigurierten Frequenzen arbeiten.

Bei mehreren Frequenzen kann ein Hop-Intervall festgelegt werden. Zusätzlich können einzelne von `rtl_433` unterstützte Sensorprotokolle ausgewählt werden.

Ohne explizite Protokollauswahl verarbeitet `rtl_433` alle empfangenen unterstützten Protokolle.

## Dienst

`rtl_433` wird durch das Plugin als systemd-Service eingerichtet:

```text
rtl_433-mqtt.service
```

Der Service verwendet die vom Plugin erzeugte Konfigurationsdatei `rtl_433.conf`.

Für Diagnosezwecke können beispielsweise folgende Befehle verwendet werden:

```bash
systemctl status rtl_433-mqtt.service
journalctl -u rtl_433-mqtt.service
```

## Dokumentation und Hilfe

Ausführlichere Informationen und Beispiele:

* [LoxBerry Wiki – RadioScanner](https://wiki.loxberry.de/plugins/radioscanner/start)
* [GitHub Issues](https://github.com/Liver64/LoxBerry-Radioscanner/issues)
* [LoxForum – RadioScanner](https://www.loxforum.com/forum/projektforen/loxberry/plugins/412617-radioscanner)

Bei einer Fehlermeldung bitte möglichst folgende Angaben mitliefern:

* LoxBerry-Version
* RadioScanner-Version
* verwendete Hardware / RTL-SDR-Dongle
* relevante Logausgaben
* Schritte zur Reproduktion des Problems

Passwörter, MQTT-Zugangsdaten und andere sensible Informationen bitte vor dem Veröffentlichen aus Logs entfernen.

---

# Hinweise für Entwickler

> [!IMPORTANT]
> `rtl-sdr` und `rtl_433` werden während der Installation aus dem Quellcode gebaut. Änderungen an Installations-, Upgrade- oder Uninstall-Skripten müssen deshalb immer für **Neuinstallation und Upgrade** geprüft werden.

## Plugin-Daten

Der technische Plugin-Ordner lautet:

```text
rascan4lox
```

Die Mindestversion von LoxBerry wird in `plugin.cfg` definiert.

## Externe Komponenten

Das Plugin verwendet:

* `rtl-sdr`
  `https://gitea.osmocom.org/sdr/rtl-sdr.git`
* `rtl_433`
  `https://github.com/merbanan/rtl_433.git`

Die Source- und Build-Verzeichnisse liegen unter:

```text
/usr/local/rtl/rtl-sdr/
/usr/local/rtl/rtl_433/
```

Das von `rtl_433` verwendete Runtime-Binary ist:

```text
/usr/local/bin/rtl_433
```

## Installationsmanifeste

Für eine vollständige und sichere Deinstallation werden die von CMake erzeugten `install_manifest.txt`-Dateien dauerhaft zusammengeführt und gespeichert:

```text
/usr/local/rtl/install-manifests/rtl-sdr.txt
/usr/local/rtl/install-manifests/rtl_433.txt
```

Diese Manifeste dürfen bei Änderungen an `postroot.sh` nicht entfernt oder umgangen werden.

## systemd

Die Service-Datei wird installiert unter:

```text
/etc/systemd/system/rtl_433-mqtt.service
```

Nach Änderungen an systemd-Dateien muss immer

```bash
systemctl daemon-reload
```

ausgeführt werden.

## LoxBerry Installations-Hooks

Für `postroot.sh` gelten die LoxBerry-Exitcodes:

```text
0 = erfolgreich
1 = Warnung, Installation wird fortgesetzt
2 = fataler Fehler, Installation wird abgebrochen
```

Fehler beim Clone, Build oder bei der Installation von `rtl-sdr` bzw. `rtl_433` müssen deshalb mit **Exitcode 2** beendet werden.

## LoxBerry-Pfade

In Dateien, die vom LoxBerry-Installer verarbeitet werden, sollten die vorgesehenen `REPLACELB...`-Platzhalter verwendet werden.

Beispiel:

```text
REPLACELBPCONFIGDIR
REPLACELBPBINDIR
```

Keine installationsspezifischen LoxBerry-Pfade unnötig hart codieren.

## Konfiguration

`bin/create_conf.php` erzeugt die `rtl_433.conf`.

Dabei gilt:

* MQTT-Zugangsdaten werden über die LoxBerry-API gelesen.
* `create_conf.php` stellt selbst keine MQTT-Verbindung her.
* Die eigentliche MQTT-Verbindung übernimmt `rtl_433`.
* Fehler beim Erzeugen der Konfiguration müssen mit einem Fehlercode zurückgegeben werden.

## Daemon

Der LoxBerry-Daemon:

1. erzeugt bzw. aktualisiert die `rtl_433.conf`,
2. prüft den Rückgabewert von `create_conf.php`,
3. stellt sicher, dass `rtl_433-mqtt.service` läuft.

`create_conf.php` darf deshalb **nicht asynchron im Hintergrund** gestartet werden.

## Änderungen testen

Vor einem Release sollten mindestens folgende Fälle geprüft werden:

* Neuinstallation auf einem sauberen LoxBerry
* Upgrade einer bestehenden Installation
* bestehende RadioScanner-Konfiguration bleibt beim Upgrade erhalten
* RTL-SDR-Dongle wird erkannt
* `rtl_433-mqtt.service` startet erfolgreich
* Sensordaten werden an MQTT übertragen
* `rascanner` funktioniert
* Deinstallation stoppt und entfernt den Service
* durch CMake installierte Dateien werden anhand der Manifeste entfernt
* fremde Dateien unter `/usr/local/rtl` bleiben unangetastet

## Changelog

Änderungen zwischen den Versionen werden in [`changelog.txt`](changelog.txt) dokumentiert.

## Lizenz

Dieses Projekt steht unter der **Apache License 2.0**.

Weitere Informationen befinden sich in der Datei [LICENSE](LICENSE).
