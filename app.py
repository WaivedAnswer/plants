from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import os
from plant_repository import PlantRepository, GetPlantRepository
import logging

# Load environment variables from .env file

if os.getenv('DB_ENV', 'dev') == 'dev':
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
CORS(app)


repo = GetPlantRepository()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/plants', methods=['GET'])
def get_plants():
    plants = repo.get_all_plants()
    return jsonify(plants)

@app.route('/api/plants', methods=['POST'])
def add_plant():
    data = request.json
    plant_id = repo.add_plant(data['name'], data['description'], data['watering_frequency'])
    return jsonify({'id': plant_id, **data})

@app.route('/api/plants/<int:plant_id>', methods=['PUT'])
def update_plant(plant_id):
    data = request.json
    repo.update_plant(plant_id, data['name'], data['description'], data['watering_frequency'])
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
def delete_plant(plant_id):
    repo.delete_plant(plant_id)
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>/last-watered', methods=['POST'])
def set_last_watered(plant_id):
    data = request.json
    last_watered = data.get('last_watered')
    repo.set_last_watered(plant_id, last_watered)
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>/water', methods=['POST'])
def water_plant(plant_id):
    repo.water_plant(plant_id)
    return jsonify({'success': True})

#TODO fix this endpoint. - missing multiple plants
@app.route('/api/plants/needs-watering', methods=['GET'])
def get_plants_needing_water():
    needs_water = repo.needs_watering()
    return jsonify(needs_water)

if __name__ == '__main__':
    repo.init_db()
    port = int(os.environ.get('PORT', 50309))
    app.run(host='0.0.0.0', port=port)