#!/usr/bin/env python3

import argparse
import requests
import toml
import time
import os

from paho.mqtt import client as mqtt_client

# Configure Logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Parse command line args
parser = argparse.ArgumentParser(description='reads sensor data from MQTT and writes to InfluxDB ')
parser.add_argument('-c', '--config', default='config.toml', help='path to config file')
parser.add_argument('files', metavar='FILE', nargs='*', help='files to import')
args = parser.parse_args()

# Read config file
config = toml.load(args.config)

# Gibt die kWh zurück
def parse_payload(payload):
    return int.from_bytes(payload[27:31], byteorder='little')

def writeToInflux(kwh, time=None):
    influx = "wmz kwh={}i".format(kwh)
    cfg = config["influxdb"]

    if time:
        influx += " {}".format(time)

    res = requests.post(cfg["url"],
        auth=(cfg["username"], cfg["password"]),
        data=influx,
    )
    print(res.text)

def connect_mqtt() -> mqtt_client:
    mqtt_cfg  = config["mqtt"]
    client = mqtt_client.Client("mqtt2influx")
    client.connect(mqtt_cfg["broker"], mqtt_cfg["port"])
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        # Keine alten Nachrichten verarbeiten
        if(msg.retain == 1):
            return

        with open(("data/wmz-%s.dat" % int(time.time())), 'wb') as f:
            f.write(msg.payload)

        try:
            kwh = parse_payload(msg.payload)
            print("kWh:", kwh)
            client.publish("sensors/mwz/kwh", payload=kwh, retain=True)
            writeToInflux(kwh)
        except Exception as err:
            print("failed to read/write message:", err)

    client.subscribe("sensors/wmz/raw")
    client.on_message = on_message


if __name__ == '__main__':
    if len(args.files) > 0:
        # Dateien importieren
        for file in args.files:
            stat = os.stat(file)
            with open(file, "rb") as f:
                writeToInflux(f.read(), int(stat.st_ctime))
    else:
        # Daten aus MQTT lesen
        client = connect_mqtt()
        subscribe(client)
        client.loop_forever()
