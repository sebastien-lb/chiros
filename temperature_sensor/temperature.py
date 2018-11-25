import sys
import time
from datetime import datetime
from os import listdir, system

from flask import Flask, jsonify
from flask_cors import CORS

DEVICE_FOLDER = "/sys/bus/w1/devices/"
DEVICE_SUFFIX = "/w1_slave"
WAIT_INTERVAL = 0.2

ALLOWABLE_ORIGINS = ["https://freeboard.io"]
system('modprobe w1-gpio')
system('modprobe w1-therm')

app = Flask(__name__)

@app.route("/")
def temperature():
    device = guess_temperature_sensor()
    return jsonify(read_temperature(device))


def guess_temperature_sensor():
    """
    Try guessing the location of the installed temperature sensor
    """
    devices = listdir(DEVICE_FOLDER)
    devices = [device for device in devices if device.startswith('28-')]
    if devices:
        return DEVICE_FOLDER + devices[0] + DEVICE_SUFFIX
    else:
        sys.exit("Sorry, no temperature sensors found")


def raw_temperature(device):
    """
    Get a raw temperature reading from the temperature sensor
    """
    raw_reading = None
    with open(device, 'r') as sensor:
        raw_reading = sensor.readlines()
    return raw_reading


def read_temperature(device):
    """
    Keep trying to read the temperature from the sensor until
    it returns a valid result
    """
    lines = raw_temperature(device)

    # Keep retrying till we get a YES from the thermometer
    # 1. Make sure that the response is not blank
    # 2. Make sure the response has at least 2 lines
    # 3. Make sure the first line has a "YES" at the end
    while not lines and len(lines) < 2 and lines[0].strip()[-3:] != 'YES':
        # If we haven't got a valid response, wait for the WAIT_INTERVAL
        # (seconds) and try again.
        time.sleep(WAIT_INTERVAL)
        lines = raw_temperature()

    # Split out the raw temperature number
    temperature = lines[1].split('t=')[1]

    # Check that the temperature is not invalid
    if temperature != -1:
        temperature_celsius = round(float(temperature) / 1000.0, 1)
        temperature_fahrenheit = round((temperature_celsius * 1.8) + 32.0, 1)

    response = {'celsius': temperature_celsius,
                'fahrenheit': temperature_fahrenheit}
    return response


if __name__ == "__main__":
    app.run()
