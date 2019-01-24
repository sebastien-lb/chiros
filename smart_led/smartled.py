from flask import Flask, json, request
import requests

app = Flask(__name__)


@app.route("/config")
def config():
    return getConfigResponse()


@app.route("/state")
def state():
    data = {}
    with open("state.json") as file:
        data = json.loads(file.read())
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='appliaction/json'
        )
        return response

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/on", methods=["POST", "PUT"])
def on():
    data = request.get_json(force=True)
    print(data)
    state = {'r': 0, 'g': 0, 'b': 0, 'a': 0}
    with open("state.json", "r") as file:
        state = json.loads(file.read())
        state = data["payload"]
    # change actual led colors here
    print(state)
    with open("state.json", "w") as file:
        file.write(json.dumps(state))

    send_status()
    response = app.response_class(
        status=200
    )
    return response


@app.route("/off", methods=["POST"])
def off():
    state = {'r': 0, 'g': 0, 'b': 0, 'a': 0}
    with open("state.json", "w") as file:
        file.write(json.dumps(state))

    send_status()
    # turn off leds here
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

def send_status():
    data = {}
    with open("state.json", "r") as file:
        state = json.loads(file.read())
        data["value"] = json.dumps(state)

    with open("server.json", "r") as file:
        server = json.loads(file.read())
        data_source_id = server["data-source-ids"]["state"]
        data["data_source_id"] = data_source_id

    r = requests.post("http://" + server["url"] + ":" + server["port"] + "/saveDataPoint", data=json.dumps(data),
        headers={'Content-type': 'application/json'})

    print("response datasaved", r.text, data)

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

if __name__=='__main__':
    app.run()
