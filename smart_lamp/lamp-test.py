from flask import Flask, json
import time
from threading import Thread
import schedule
import requests

app = Flask(__name__)

@app.route('/config')
def config():
    return getConfigResponse()


@app.route('/state')
def state():
    with open("state.json") as file:
        data = json.loads(file.read())

        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    return response


@app.route('/on')
def on():
    data = {}
    with open("state.json", "r") as file:
        data = json.loads(file.read())

    data['value'] = 1
    # led.on()

    with open("state.json", "w") as file:
        file.write(json.dumps(data))

    response = app.response_class(
        status=200
    )

    return response


@app.route('/off')
def off():
    data = {}
    with open("state.json", "r") as file:
        data = json.loads(file.read())

    data['value'] = 0
    # led.off()

    with open("state.json", "w") as file:
        file.write(json.dumps(data))

    response = app.response_class(
        status=200
    )

    return response

def getConfigResponse():
    data = {}
    with open("config.json") as file:
        data = json.loads(file.read())
        print(data)
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
    state = json.loads("state.json")
    server = json.loads("server.json")
    data = json.dumps(state["value"])
    requests.post(server["url"] + ":" + server["port"] + "/entryPoint/" + server["id"], data=data )
    return app.response_class(status=200)

def runJobs():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__=='__main__':
    cron_thread = Thread(target=runJobs)
    cron_thread.start()
    app.run()
