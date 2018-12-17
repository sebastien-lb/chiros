import time
from math import cos
import schedule
import sys
import requests

from flask import Flask, json, request
from threading import Thread

app = Flask(__name__)

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
    data = {
        "value": cos(time.time() / 30)
    }

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

    response = app.response_class(
        response=json.dumps(data),
        status=500,
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


def send_status():
    data = {
        "value": cos(time.time() / 30)
    }

    with open("server.json", "r") as file:
        server = json.loads(file.read())
        data["data_source_id"] = server["data-source-ids"]["temperature"]

    requests.post("http://" + server["url"] + ":" + server["port"] + "/saveDataPoint", data=json.dumps(data),
        headers={'Content-type': 'application/json'})

    return app.response_class(status=200)

def runJobs():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__=='__main__':
    cron_thread = Thread(target=runJobs)
    cron_thread.start()
    port = 5000 if not(len(sys.argv)>1) else int(sys.argv[1])
    app.run(port=port)
    app.run()
