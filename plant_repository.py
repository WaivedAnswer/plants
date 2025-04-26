import sqlite3
from datetime import datetime

class PlantRepository:
    def __init__(self, db_path='plants.db'):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
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

    def get_all_plants(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM plants')
        plants = [{'id': row[0], 'name': row[1], 'description': row[2], 
                   'watering_frequency': row[3], 'last_watered': row[4]} 
                  for row in c.fetchall()]
        conn.close()
        return plants

    def add_plant(self, name, description, watering_frequency):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO plants (name, description, watering_frequency, last_watered)
            VALUES (?, ?, ?, ?)
        ''', (name, description, watering_frequency, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        plant_id = c.lastrowid
        conn.close()
        return plant_id

    def delete_plant(self, plant_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
        conn.commit()
        conn.close()

    def update_plant(self, plant_id, name, description, watering_frequency):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE plants 
            SET name = ?, description = ?, watering_frequency = ?
            WHERE id = ?
        ''', (name, description, watering_frequency, plant_id))
        conn.commit()
        conn.close()

    def water_plant(self, plant_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('UPDATE plants SET last_watered = ? WHERE id = ?', (today, plant_id))
        conn.commit()
        conn.close()

    def set_last_watered(self, plant_id, last_watered):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE plants SET last_watered = ? WHERE id = ?', (last_watered, plant_id))
        conn.commit()
        conn.close()