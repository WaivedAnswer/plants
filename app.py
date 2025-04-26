from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS plants
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         description TEXT,
         watering_frequency INTEGER NOT NULL,
         last_watered DATE)
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/plants', methods=['GET'])
def get_plants():
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    c.execute('SELECT * FROM plants')
    plants = [{'id': row[0], 'name': row[1], 'description': row[2], 
               'watering_frequency': row[3], 'last_watered': row[4]} 
              for row in c.fetchall()]
    conn.close()
    return jsonify(plants)

@app.route('/api/plants', methods=['POST'])
def add_plant():
    data = request.json
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO plants (name, description, watering_frequency, last_watered)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['description'], data['watering_frequency'], 
          datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    plant_id = c.lastrowid
    conn.close()
    return jsonify({'id': plant_id, **data})

@app.route('/api/plants/<int:plant_id>', methods=['PUT'])
def update_plant(plant_id):
    data = request.json
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    c.execute('''
        UPDATE plants 
        SET name = ?, description = ?, watering_frequency = ?
        WHERE id = ?
    ''', (data['name'], data['description'], data['watering_frequency'], plant_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
def delete_plant(plant_id):
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    c.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>/last-watered', methods=['POST'])
def set_last_watered(plant_id):
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    data = request.json
    last_watered = data.get('last_watered')
    c.execute('UPDATE plants SET last_watered = ? WHERE id = ?', (last_watered, plant_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>/water', methods=['POST'])
def water_plant(plant_id):
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('UPDATE plants SET last_watered = ? WHERE id = ?', (today, plant_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/plants/needs-watering', methods=['GET'])
def get_plants_needing_water():
    conn = sqlite3.connect('plants.db')
    c = conn.cursor()
    c.execute('SELECT * FROM plants')
    plants = c.fetchall()
    needs_water = []
    
    for plant in plants:
        last_watered = datetime.strptime(plant[4], '%Y-%m-%d') if plant[4] else None
        if not last_watered or \
           (datetime.now() - last_watered).days >= plant[3]:
            needs_water.append({
                'id': plant[0],
                'name': plant[1],
                'description': plant[2],
                'watering_frequency': plant[3],
                'last_watered': plant[4]
            })
    
    conn.close()
    return jsonify(needs_water)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 50309))
    app.run(host='0.0.0.0', port=port)