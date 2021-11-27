from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
from flask.json import jsonify
import uuid
from reto import City

games = {}

app = Flask(__name__, static_url_path='')

@app.route("/games", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    games[id] = City()
    return "ok", 201, {'Location': f"/games/{id}"}


@app.route("/games/<id>/cars", methods=["GET"])
def queryStateCars(id):
    global model
    model = games[id]
    model.step()
    cars = model.schedule.agents
    
    listAgents = []

    for i in range(model.numCoches):
        listAgents.append({"x": cars[i].pos[0], "y": cars[i].pos[1]})

    return jsonify({"Items": listAgents})


@app.route("/games/<id>/lights", methods=["GET"])
def queryStateLights(id):
    global model
    model = games[id]
    model.step()
    lights = model.schedule.agents
    
    listAgents = []

    for i in range(model.numCoches, model.numCoches + model.numLights):
        listAgents.append({"state": lights[i].estado})

    return jsonify({"Items": listAgents})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))