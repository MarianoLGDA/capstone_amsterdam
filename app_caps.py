import os
import openai
import time
import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Set OpenAI API Key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# Sightseeing locations for each city
sightseeing_spots = {
    "Amsterdam": {
        "Rijksmuseum": (52.360001, 4.885278, "rijksmuseum.jpg"),
        "Anne Frank House": (52.375218, 4.883977, "anne_frank_house.jpg"),
        "Van Gogh Museum": (52.358416, 4.881077, "van_gogh_museum.jpg"),
        "Dam Square": (52.373058, 4.892557, "dam_square.jpg"),
        "Jordaan District": (52.379189, 4.880556, "jordaan.jpg"),
        "Vondelpark": (52.358333, 4.868611, "vondelpark.jpg"),
        "Ajax Stadium": (52.314167, 4.941389, "ajax_stadium.jpg"),
        "A'DAM Lookout": (52.384409, 4.902568, "adam_lookout.jpg"),
        "NEMO Science Museum": (52.374639, 4.912261, "nemo_museum.jpg"),
        "The Heineken Experience": (52.357869, 4.891700, "heineken_experience.jpg"),
    },
    "Barcelona": {
        "Sagrada Familia": (41.403629, 2.174356, "sagrada_familia.jpg"),
        "Park Güell": (41.414495, 2.152695, "park_guell.jpg"),
        "Casa Batlló": (41.391640, 2.164894, "casa_batllo.jpg"),
        "La Rambla": (41.376430, 2.175610, "la_rambla.jpg"),
        "Gothic Quarter": (41.380897, 2.176847, "gothic_quarter.jpg"),
        "Camp Nou": (41.380896, 2.122820, "camp_nou.jpg"),
        "Montjuïc": (41.363531, 2.158798, "montjuic.jpg"),
        "Tibidabo": (41.418064, 2.118847, "tibidabo.jpg"),
        "Magic Fountain": (41.371454, 2.151699, "magic_fountain.jpg"),
        "Arc de Triomf": (41.391926, 2.180305, "arc_de_triomf.jpg"),
    }
}

# Load Airbnb data based on city selection
@st.cache_data
def load_data(city):
    file_path = f"df_{city.lower()}.csv"
    df = pd.read_csv(file_path)

    # Ensure lat/lon are valid
    df = df.dropna(subset=["latitude", "longitude"])

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )
    return gdf

st.subheader("💬 SmartStay AI Chatbot: Plan Your Trip!")

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = "ask_name"
if "name" not in st.session_state:
    st.session_state.name = ""
if "city" not in st.session_state:
    st.session_state.city = ""
if "selected_sights" not in st.session_state:
    st.session_state.selected_sights = []
if "budget" not in st.session_state:
    st.session_state.budget = None
if "property_type" not in st.session_state:
    st.session_state.property_type = []
if "gdf" not in st.session_state:
    st.session_state.gdf = None

# Back button logic
if st.session_state.step != "ask_name" and st.button("⬅️ Back"):
    if st.session_state.step == "ask_city":
        st.session_state.step = "ask_name"
    elif st.session_state.step == "ask_sightseeing":
        st.session_state.step = "ask_city"
    elif st.session_state.step == "ask_budget":
        st.session_state.step = "ask_sightseeing"
    elif st.session_state.step == "ask_property_type":
        st.session_state.step = "ask_budget"
    elif st.session_state.step == "show_results":
        st.session_state.step = "ask_property_type"
    st.rerun()

# Step 1: Ask for the user's name
if st.session_state.step == "ask_name":
    user_name = st.text_input("👋 Hey traveler! What's your name?")
    if user_name:
        st.session_state.name = user_name
        st.session_state.step = "ask_city"
        st.rerun()

# Step 2: Ask for the city
elif st.session_state.step == "ask_city":
    st.write(f"Nice to meet you, {st.session_state.name}! 😊")
    city = st.selectbox("🌍 Which city are you traveling to?", ["Amsterdam", "Barcelona"])
    if st.button("Confirm City"):
        st.session_state.city = city
        st.session_state.gdf = load_data(city)
        st.session_state.step = "ask_sightseeing"
        st.rerun()

# Step 3: Ask for sightseeing locations (2 rows, 5 per row)
elif st.session_state.step == "ask_sightseeing":
    st.write(f"Awesome, {st.session_state.name}! 🏙️ Now, select your must-visit places in {st.session_state.city}.")
    
    sightseeing_list = list(sightseeing_spots[st.session_state.city].items())
    first_row = sightseeing_list[:5]
    second_row = sightseeing_list[5:]

    selected_sights = []

    # First row of sightseeing options
    cols = st.columns(5)
    for col, (sight, (lat, lon, img)) in zip(cols, first_row):
        with col:
            st.image(img, width=200)
            if st.checkbox(sight, key=sight):
                selected_sights.append(sight)

    # Second row of sightseeing options
    cols = st.columns(5)
    for col, (sight, (lat, lon, img)) in zip(cols, second_row):
        with col:
            st.image(img, width=200)
            if st.checkbox(sight, key=sight):
                selected_sights.append(sight)

    if st.button("Confirm Sightseeing"):
        st.session_state.selected_sights = selected_sights
        st.session_state.step = "ask_budget"
        st.rerun()

# Step 4: Ask for budget
elif st.session_state.step == "ask_budget":
    st.write(f"Great choices, {st.session_state.name}! 💰 Now, what's your budget per night?")
    budget = st.slider("Select your budget (€)", 50, 500, 150)

    if st.button("Confirm Budget"):
        st.session_state.budget = budget
        st.session_state.step = "ask_property_type"
        st.rerun()

# Step 5: Ask for property type
elif st.session_state.step == "ask_property_type":
    st.write(f"Almost there, {st.session_state.name}! 🏡 What type of property do you prefer?")
    property_types = st.session_state.gdf['property_type'].unique().tolist()
    selected_property_type = st.multiselect("Select property type(s):", property_types)

    if st.button("Find Best Stays"):
        st.session_state.property_type = selected_property_type
        st.session_state.step = "show_results"
        st.rerun()

# Step 6: Show map with filtered Airbnbs
elif st.session_state.step == "show_results":
    st.write(f"Here are your best options in {st.session_state.city}, {st.session_state.name}! 🎉")
    filtered_gdf = st.session_state.gdf[
        (st.session_state.gdf['price'] <= st.session_state.budget)
    ]
    
    if st.session_state.property_type:
        filtered_gdf = filtered_gdf[filtered_gdf['property_type'].isin(st.session_state.property_type)]

    if not filtered_gdf.empty:
        map_city = folium.Map(location=[filtered_gdf.latitude.mean(), filtered_gdf.longitude.mean()], zoom_start=13)
        folium_static(map_city)










