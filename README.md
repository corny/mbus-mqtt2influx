# mbus MQTT to InfluxDB

Dieses Python-Script parst die Rohdaten des [mbus-Lesers](https://github.com/corny/mbus-esp32),
schreibt sie sowohl in eine InfluxDB und sendet sie zurück an den MQTT-Server.

## Home Assistant

Damit Home Assistant die Daten abholt, ist folgenden Konfiguration notwendig:

Die `/usr/share/hassio/homeassistant/configuration.yaml`
ergänzen und anschließen HA neustarten mit `ha core restart`.

```yaml
mqtt:
  sensor:
  - state_topic: "sensors/mwz/kwh"
    name: "Wärme"
    object_id: waerme
    device_class: energy
    unit_of_measurement: kWh
```
