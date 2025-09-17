from fastapi import FastAPI
from pydantic import BaseModel
from db_sqlite import insert_country, insert_state, insert_city, get_countries, get_states_by_country, get_cities_by_state
from db_mongo import insert_place, find_places_by_city, find_nearby, ensure_indexes
import re

app = FastAPI()
ensure_indexes()

class Country(BaseModel):
    name: str

class State(BaseModel):
    name: str
    country_id: int

class City(BaseModel):
    name: str
    state_id: int

class Place(BaseModel):
    nome: str
    cidade: str
    lat: float
    lon: float
    descricao: str | None = None

def serialize_place(place):
    place["_id"] = str(place["_id"])
    if "location" in place and "coordinates" in place["location"]:
        place["location"]["coordinates"] = [float(c) for c in place["location"]["coordinates"]]
    return place

@app.get("/places/{cidade}")
def list_places(cidade: str):
    try:
        locais = find_places_by_city(re.compile(f"^{re.escape(cidade)}$", re.IGNORECASE))
        if not locais:
            return []
        return [serialize_place(l) for l in locais]
    except Exception as e:
        return {"error": str(e)}

@app.post("/countries")
def add_country(country: Country):
    insert_country(country.name)
    return {"msg": f"País {country.name} cadastrado!"}

@app.get("/countries")
def list_countries():
    return get_countries()

@app.post("/states")
def add_state(state: State):
    insert_state(state.name, state.country_id)
    return {"msg": f"Estado {state.name} cadastrado!"}

@app.get("/states/{country_id}")
def list_states(country_id: int):
    return get_states_by_country(country_id)

@app.post("/cities")
def add_city(city: City):
    insert_city(city.name, city.state_id)
    return {"msg": f"Cidade {city.name} cadastrada!"}

@app.get("/cities/{state_id}")
def list_cities(state_id: int):
    return get_cities_by_state(state_id)

@app.post("/places")
def add_place(place: Place):
    insert_place(place.nome, place.cidade, place.lat, place.lon, descricao=place.descricao)
    return {"msg": f"Local {place.nome} cadastrado no MongoDB!"}

@app.get("/places/nearby/")
def list_nearby(lat: float, lon: float, raio_metros: int = 1000):
    return find_nearby(lat, lon, raio_metros)