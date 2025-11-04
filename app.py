import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# --- Streamlit page settings ---
st.set_page_config(page_title="🌦️ Global Weather Dashboard", page_icon="🌍", layout="centered")

st.title("🌍 Global Weather Explorer (Open-Meteo API)")
st.markdown("""
Select a city or click any location on the map to see **current weather** data, including:
- 🌡️ Temperature  
- 💧 Humidity  
- 🌧️ Precipitation
""")

# --- City input ---
city = st.text_input("🔍 Enter a city name (optional):", "")

# --- Function: Get weather data ---
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation"
        f"&timezone=auto"
    )
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return data.get("current", {})
    else:
        return {"error": "Failed to fetch data"}

# --- Geocoding (convert city name to coordinates) ---
lat, lon = None, None
if city:
    st.write(f"Searching for coordinates of **{city}** ...")
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    geo_res = requests.get(geo_url).json()
    if "results" in geo_res and len(geo_res["results"]) > 0:
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        st.success(f"✅ Found {city}: ({lat:.2f}, {lon:.2f})")
    else:
        st.error("City not found. Try again.")

# --- Map section ---
st.subheader("🗺️ Click on the map to explore weather anywhere")
m = folium.Map(location=[20, 0], zoom_start=2)
map_data = st_folium(m, height=400, width=700)

# --- If user clicked on map, use that location ---
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.info(f"📍 Selected coordinates: ({lat:.2f}, {lon:.2f})")

# --- Fetch weather if coordinates exist ---
if lat and lon:
    weather = get_weather(lat, lon)
    if "temperature_2m" in weather:
        st.subheader("🌦️ Current Weather Data")
        st.metric("Temperature (°C)", f"{weather['temperature_2m']}")
        st.metric("Humidity (%)", f"{weather['relative_humidity_2m']}")
        st.metric("Precipitation (mm)", f"{weather['precipitation']}")
        st.caption(f"Last update: {weather.get('time', 'N/A')}")
    else:
        st.error("⚠️ Could not fetch weather data.")
