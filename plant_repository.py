import logging
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from abc import ABC, abstractmethod

def GetPlantRepository():
    if os.getenv('DB_ENV', 'dev') == 'prod':
        return PostgresPlantRepository()
    else:
        return SQLitePlantRepository()

class PlantRepository(ABC):
    @abstractmethod
    def get_all_plants(self):
        pass

    @abstractmethod
    def add_plant(self, name, description, watering_frequency):
        pass

    @abstractmethod
    def delete_plant(self, plant_id):
        pass

    @abstractmethod
    def update_plant(self, plant_id, name, description, watering_frequency):
        pass

    @abstractmethod
    def water_plant(self, plant_id):
        pass

    @abstractmethod
    def set_last_watered(self, plant_id, last_watered):
        pass

    @abstractmethod
    def needs_watering(self):
        pass

class PostgresPlantRepository(PlantRepository):
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')

    def _connect(self, dict_cursor=False):
        """
        Open a new DB connection.
        If dict_cursor=True, rows come back as dicts (RealDictCursor).
        """
        if dict_cursor:
            return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
        return psycopg2.connect(self.db_url)

    def init_db(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS plants (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                watering_frequency INTEGER NOT NULL,
                last_watered DATE
            )
        ''')
        conn.commit()
        conn.close()

    def get_all_plants(self):
        conn = self._connect(dict_cursor=True)
        cur = conn.cursor()
        cur.execute('SELECT id, name, description, watering_frequency, last_watered FROM plants')
        plants = cur.fetchall()  # list of dicts via RealDictCursor
        conn.close()
        return plants

    def add_plant(self, name, description, watering_frequency):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO plants (name, description, watering_frequency, last_watered)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (
            name,
            description,
            watering_frequency,
            datetime.now().date()
        ))
        plant_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return plant_id

    def delete_plant(self, plant_id):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('DELETE FROM plants WHERE id = %s', (plant_id,))
        conn.commit()
        conn.close()

    def update_plant(self, plant_id, name, description, watering_frequency):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            UPDATE plants
            SET name = %s,
                description = %s,
                watering_frequency = %s
            WHERE id = %s
        ''', (name, description, watering_frequency, plant_id))
        conn.commit()
        conn.close()

    def water_plant(self, plant_id):
        conn = self._connect()
        cur = conn.cursor()
        today = datetime.now().date()
        cur.execute('UPDATE plants SET last_watered = %s WHERE id = %s', (today, plant_id))
        conn.commit()
        conn.close()

    def set_last_watered(self, plant_id, last_watered):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('UPDATE plants SET last_watered = %s WHERE id = %s', (last_watered, plant_id))
        conn.commit()
        conn.close()

    def needs_watering(self):
        plants=self.get_all_plants()
        needs_water = []
        
        for plant in plants:
            last_watered = datetime.strptime(plant["last_watered"], '%Y-%m-%d') if plant["last_watered"] else None
            print(plant, last_watered, datetime.now())
            if not last_watered:
                needs_water.append(plant)
            else:
                days_since = (datetime.now() - last_watered).days
                if days_since >= plant["watering_frequency"]:
                    needs_water.append(plant)
        return needs_water

class SQLitePlantRepository(PlantRepository):
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

    def needs_watering(self):
        plants=self.get_all_plants()
        needs_water = []
        
        for plant in plants:
            last_watered = datetime.strptime(plant["last_watered"], '%Y-%m-%d') if plant["last_watered"] else None
            if not last_watered:
                needs_water.append(plant)
            else:
                days_since = (datetime.now() - last_watered).days
                if days_since >= plant["watering_frequency"]:
                    needs_water.append(plant)
        return needs_water
                

    