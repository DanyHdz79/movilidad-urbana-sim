from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json
from flask.json import jsonify
import uuid
from reto import Car, City, Semaforo

games = {}

app = Flask(__name__, static_url_path='')
port=int(os.environ.get('PORT', 8000))

@app.route("/")
def root():
    return "ok"

@app.route("/games", methods=["POST"])
def create():
    global games
    id = str(uuid.uuid4())
    games[id] = City()
    return "ok", 201, {'Location': f"/games/{id}"}

@app.route("/games/<id>", methods=["GET"])
def queryStateCars(id):
    global model
    model = games[id]
    model.step()
    agents = model.schedule.agents
    
    listCars = []
    listLights = []

    for agent in agents:
        if(isinstance(agent, Car)):
            listCars.append({"id": agent.unique_id,"x": agent.pos[0], "y": agent.pos[1], "o": agent.orientacion})
        elif(isinstance(agent, Semaforo)):
            listLights.append({"id": agent.unique_id, "state": agent.estado})

    return jsonify({"cars": listCars, "tlights": listLights})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)