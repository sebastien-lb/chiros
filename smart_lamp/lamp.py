from flask import Flask, json
from gpiozero import LED
from time import sleep

app = Flask(__name__)
led = LED(14)

@app.route('/config')
def config():
    return response()


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
    led.on()

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
    led.off()

    with open("state.json", "w") as file:
        file.write(json.dumps(data))

    response = app.response_class(
        status=200
    )

    return response

def response():
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
