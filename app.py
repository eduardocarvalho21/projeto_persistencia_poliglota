import streamlit as st
import pandas as pd
import requests
from requests.utils import quote

API_URL = "http://127.0.0.1:8000"

st.title("Persistência Poliglota")
st.sidebar.header("Cadastros")

with st.sidebar.form("form_country"):
    country_name = st.text_input("Nome do país")
    submitted_country = st.form_submit_button("Salvar país")
    if submitted_country and country_name:
        r = requests.post(f"{API_URL}/countries", json={"name": country_name})
        if r.status_code == 200:
            st.success(r.json()["msg"])
        else:
            st.error("Erro ao cadastrar país")

with st.sidebar.form("form_state"):
    state_name = st.text_input("Nome do estado", key="state_name")
    countries = requests.get(f"{API_URL}/countries").json()
    country_options = {c['name']: c['id'] for c in countries}
    country_selected = st.selectbox("Selecione o país", list(country_options.keys()), key="state_country")
    submitted_state = st.form_submit_button("Salvar estado")
    if submitted_state and state_name:
        r = requests.post(f"{API_URL}/states", json={"name": state_name, "country_id": country_options[country_selected]})
        if r.status_code == 200:
            st.success(r.json()["msg"])
        else:
            st.error("Erro ao cadastrar estado")

with st.sidebar.form("form_city"):
    city_name = st.text_input("Nome da cidade", key="city_name")
    countries = requests.get(f"{API_URL}/countries").json()
    country_options = {c['name']: c['id'] for c in countries}
    country_selected = st.selectbox("Selecione o país", list(country_options.keys()), key="city_country")
    states = requests.get(f"{API_URL}/states/{country_options[country_selected]}").json()
    state_options = {s['name']: s['id'] for s in states}
    state_selected = st.selectbox("Selecione o estado", list(state_options.keys()), key="city_state")
    submitted_city = st.form_submit_button("Salvar cidade")
    if submitted_city and city_name:
        r = requests.post(f"{API_URL}/cities", json={"name": city_name, "state_id": state_options[state_selected]})
        if r.status_code == 200:
            st.success(r.json()["msg"])
        else:
            st.error("Erro ao cadastrar cidade")

with st.sidebar.form("form_local"):
    nome = st.text_input("Nome do local", key="local_name")
    cidade = st.text_input("Cidade", key="local_city")
    lat = st.number_input("Latitude", value=0.0, format="%.6f", key="local_lat")
    lon = st.number_input("Longitude", value=0.0, format="%.6f", key="local_lon")
    descricao = st.text_area("Descrição", key="local_desc")
    submitted_local = st.form_submit_button("Salvar no MongoDB")
    if submitted_local and nome and cidade:
        r = requests.post(f"{API_URL}/places", json={"nome": nome, "cidade": cidade, "lat": lat, "lon": lon, "descricao": descricao})
        if r.status_code == 200:
            st.success(r.json()["msg"])
        else:
            st.error("Erro ao cadastrar local")

st.header("Consultas e Visualização")

countries = requests.get(f"{API_URL}/countries").json()
if countries:
    country_options = {c['name']: c['id'] for c in countries}
    country_selected = st.selectbox("Selecione o país", list(country_options.keys()), key="query_country")
    states = requests.get(f"{API_URL}/states/{country_options[country_selected]}").json()
    state_options = {s['name']: s['id'] for s in states}
    state_selected = st.selectbox("Selecione o estado", list(state_options.keys()), key="query_state")
    cities = requests.get(f"{API_URL}/cities/{state_options[state_selected]}").json()
    cidade_consulta = st.selectbox("Selecione a cidade", options=[c['name'] for c in cities], key="query_city")

    if st.button("Mostrar locais da cidade"):
        cidade_encoded = quote(cidade_consulta)
        r = requests.get(f"{API_URL}/places/{cidade_encoded}")
        if r.status_code == 200:
            locais = r.json()
            if isinstance(locais, dict) and "error" in locais:
                st.error(f"Erro na API: {locais['error']}")
            elif locais:
                df = pd.DataFrame(locais)
                df["lon"] = df["location"].apply(lambda x: x["coordinates"][0])
                df["lat"] = df["location"].apply(lambda x: x["coordinates"][1])
                st.dataframe(df)
                st.map(df[['lat', 'lon']])
            else:
                st.warning("Nenhum local encontrado para essa cidade.")

st.header("Consulta por proximidade")

lat_ref = st.number_input("Latitude de referência", value=0.0, format="%.6f", key="prox_lat")
lon_ref = st.number_input("Longitude de referência", value=0.0, format="%.6f", key="prox_lon")
raio_km = st.slider("Raio de busca (km)", 1, 50, 10, key="prox_raio")

if st.button("Buscar locais próximos"):
    params = {"lat": lat_ref, "lon": lon_ref, "raio_metros": int(raio_km * 1000)}
    locais_proximos = requests.get(f"{API_URL}/places/nearby/", params=params).json()
    if locais_proximos:
        df_proximos = pd.DataFrame(locais_proximos)
        df_proximos["lon"] = df_proximos["location"].apply(lambda x: x["coordinates"][0])
        df_proximos["lat"] = df_proximos["location"].apply(lambda x: x["coordinates"][1])
        st.dataframe(df_proximos)
        st.map(df_proximos[['lat', 'lon']])
    else:
        st.warning("Nenhum local encontrado nesse raio.")