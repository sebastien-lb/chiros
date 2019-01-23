import time
from math import cos
import schedule
import sys
import requests
from os import listdir, system

from flask import Flask, json, request
from threading import Thread

import system_handler as handler

app = Flask(__name__)

if handler.is_raspberry_pi():
    print('Launching in Raspberry Pi mode.')
    DEVICE_FOLDER = "/sys/bus/w1/devices/"
    DEVICE_SUFFIX = "/w1_slave"
    WAIT_INTERVAL = 0.2

    ALLOWABLE_ORIGINS = ["https://freeboard.io"]
    system('modprobe w1-gpio')
    system('modprobe w1-therm')

    devices = listdir(DEVICE_FOLDER)
    devices = [device for device in devices if device.startswith('28-')]
    if devices:
        device = DEVICE_FOLDER + devices[0] + DEVICE_SUFFIX
    else:
        sys.exit("Sorry, no temperature sensors found")


    def raw_temperature():
        """
        Get a raw temperature reading from the temperature sensor
        """
        raw_reading = None
        with open(device, 'r') as sensor:
            raw_reading = sensor.readlines()
        return raw_reading


    def read_temperature():
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

        response = {'celsius': temperature_celsius}
        return response


else:
    print('Launching test mode.')

    def read_temperature():
        return {"celsius": 20 + 2*cos(time.time() / 30)}


def send_status():
    data = read_temperature()

    with open("server.json", "r") as file:
        server = json.loads(file.read())
        data["data_source_id"] = server["data-source-ids"]["temperature"]

    requests.post("http://" + server["url"] + ":" + server["port"] + "/saveDataPoint", data=json.dumps(data),
                  headers={'Content-type': 'application/json'})

    return app.response_class(status=200)


@app.route('/serverConfig', methods=['POST'])
def setServerConfig():
    try:
        data = request.get_json(force=True)
        server_config = {}
        server_config["url"] = data.get("url")
        server_config["id"] = data.get("id")
        server_config["port"] = data.get("port")
        server_config["data-source-ids"] = data.get("data-source-ids")
    except:
        return app.response_class(status=400)


    with open("server.json", "w") as file:
        file.write(json.dumps(server_config))

    response = app.response_class(
        status=200
    )
    return response

@app.route('/state')
def state():
    data = read_temperature()

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    return response

@app.route('/config')
def getConfigResponse():
    data = {}
    with open("config.json") as file:
        data = json.loads(file.read())
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response


@app.route('/read', methods=["POST"])
def read():
    schedule.every(3).seconds.do(send_status).tag('read')
    return app.response_class(status=200)


@app.route('/read', methods=["DELETE"])
def stopRead():
    schedule.clear('read')
    return app.response_class(status=200)


def runJobs():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    cron_thread = Thread(target=runJobs)
    cron_thread.start()
    port = 5000 if not(len(sys.argv)>1) else int(sys.argv[1])
    app.run(port=port)
    app.run()
