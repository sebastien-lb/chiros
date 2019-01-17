from flask import Flask, json, request

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
    state = {"R": 0, "G": 0, "B": 0}
    with open("state.json") as file:
        state = json.loads(file.read())
        R,G,B = data["payload"].split('-')
        state["R"] = int(R)
        state["G"] = int(G)
        state["B"] = int(B)
    # change actual led colors here
    print(state)
    with open("state.json", "w") as file:
        file.write(json.dumps(state))
    
    response = app.response_class(
        status=200
    )
    return response


@app.route("/off", methods=["POST"])
def off():
    state = {"R": 0, "G": 0, "B": 0}
    with open("state.json", "r") as file:
        file.write(json.dumps(state))
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


if __name__=='__main__':
    app.run()