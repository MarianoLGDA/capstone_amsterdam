import os
import openai
import time
import random
import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Set OpenAI API Key securely
openai.api_key = os.getenv("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")

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
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )
    return gdf

st.subheader("💬 SmartStay AI Chatbot: Plan Your Trip!")

# Random greetings for different interactions
greetings = [
    "Hi, Interrail traveler! 🌍 Where are you headed?",
    "Welcome, globetrotter! ✈️ Which city will you explore?",
    "Hello, adventurer! 🚆 Where is your next stop?",
    "Hey, traveler! 🏙️ Are you visiting Amsterdam or Barcelona?",
    "Greetings, explorer! 🗺️ Let's plan your stay!"
]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": random.choice(greetings)}]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input field
user_input = st.chat_input("Type your answer here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Process user response
    city = user_input.strip().title()
    if city not in ["Amsterdam", "Barcelona"]:
        bot_reply = "Sorry, we currently support only Amsterdam and Barcelona. Please choose one of these cities. 😊"
    else:
        bot_reply = f"Great! You're visiting **{city}**. Now, select the sightseeing places you want to visit!"

        # Load city-specific data
        gdf = load_data(city)

        # Display sightseeing choices
        selected_sights = []
        sightseeing_list = list(sightseeing_spots[city].items())
        first_row = sightseeing_list[:5]
        second_row = sightseeing_list[5:]

        # Sightseeing images in two rows
        cols = st.columns(5)
        for col, (sight, (lat, lon, img)) in zip(cols, first_row):
            with col:
                st.image(img, width=200)
                if st.checkbox(sight, key=sight):
                    selected_sights.append((sight, lat, lon, img))

        cols = st.columns(5)
        for col, (sight, (lat, lon, img)) in zip(cols, second_row):
            with col:
                st.image(img, width=200)
                if st.checkbox(sight, key=sight):
                    selected_sights.append((sight, lat, lon, img))

        # Ask for travel preferences
        bot_reply += "\n\n💰 **What is your budget per night (€)?**"
        budget = st.number_input("Enter your budget:", min_value=50, max_value=500, step=10)

        bot_reply += "\n\n🏡 **What type of property do you want?**"
        property_types = gdf['property_type'].unique().tolist()
        selected_property_type = st.multiselect("Select property type(s):", property_types)

        bot_reply += "\n\n⭐ **Minimum review score?**"
        review_score = st.slider("Select a minimum review score:", 50, 100, 80)

        # Filter Airbnbs
        filtered_gdf = gdf[gdf['price'] <= budget]
        if selected_property_type:
            filtered_gdf = filtered_gdf[gdf['property_type'].isin(selected_property_type)]
        filtered_gdf = filtered_gdf[gdf['review_scores_rating'] >= review_score]

        # Display the map with Airbnb recommendations
        if len(selected_sights) >= 3:
            polygon = Polygon([(lon, lat) for _, lat, lon, _ in selected_sights])
            filtered_gdf = filtered_gdf[filtered_gdf.geometry.within(polygon)]

            bot_reply += "\n\n📍 **Here are the best accommodations within your selected zone:**"
            map_city = folium.Map(location=[gdf.latitude.mean(), gdf.longitude.mean()], zoom_start=13)
            marker_cluster = MarkerCluster().add_to(map_city)

            for _, row in filtered_gdf.iterrows():
                folium.Marker(
                    location=[row.latitude, row.longitude],
                    popup=f"{row['name']}, €{row['price']} per night",
                    icon=folium.Icon(color="orange", icon="home", prefix="fa")
                ).add_to(marker_cluster)

            folium_static(map_city)

    # Append bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Display bot response
    with st.chat_message("assistant"):
        st.write(bot_reply)

    time.sleep(1)










