from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["persistencia_poliglota"]
places = db["places"]

def ensure_indexes():
    places.create_index([("location", "2dsphere")])
    places.create_index([("cidade", ASCENDING)])

def insert_place(nome_local, cidade, latitude, longitude, descricao=""):
    doc = {
        "nome_local": nome_local,
        "cidade": cidade,
        "location": { "type": "Point", "coordinates": [longitude, latitude] },
        "descricao": descricao,
        "created_at": datetime.timezone.utc.now()
    }
    return places.insert_one(doc).inserted_id

def find_places_by_city(cidade: str):
    return list(places.find({"cidade": cidade}))

def find_nearby(latitude: float, longitude: float, max_distance_meters: int):
    query = {
        "location": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "$maxDistance": max_distance_meters
            }
        }
    }
    return list(places.find(query))