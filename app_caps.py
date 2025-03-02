import streamlit as st
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from streamlit_folium import folium_static

# Load Airbnb data based on city selection
@st.cache_data
def load_data(city):
    if city == "Amsterdam":
        file_path = "df_amsterdam.csv"
    else:
        file_path = "df_barcelona.csv"
    df = pd.read_csv(file_path)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )
    return gdf

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

st.set_page_config(page_title="SmartStay: AI-Powered Interrail Accommodation", page_icon="🚆", layout="wide")

# Step 1: User selects city
city = st.selectbox("Which city are you planning to visit?", ["Amsterdam", "Barcelona"], index=0)
gdf = load_data(city)

st.subheader("🎯 Select the sightseeing places you want to visit:")
selected_sights = []
sightseeing_list = list(sightseeing_spots[city].items())
first_row = sightseeing_list[:5]
second_row = sightseeing_list[5:]

# First row of sightseeing images
cols = st.columns(5)
for col, (sight, (lat, lon, img)) in zip(cols, first_row):
    with col:
        st.image(img, width=250)
        if st.checkbox(sight, key=sight):
            selected_sights.append((sight, lat, lon, img))

# Second row of sightseeing images
cols = st.columns(5)
for col, (sight, (lat, lon, img)) in zip(cols, second_row):
    with col:
        st.image(img, width=250)
        if st.checkbox(sight, key=sight):
            selected_sights.append((sight, lat, lon, img))

if selected_sights:
    st.subheader("🏡 Filter Your Airbnb Preferences")
    property_types = gdf['property_type'].unique().tolist()
    room_types = gdf['room_type'].unique().tolist()
    
    selected_property_type = st.selectbox("Select property type", ["Any"] + property_types)
    selected_room_type = st.selectbox("Select room type", ["Any"] + room_types)
    budget = st.slider("What is your budget per night (in €)?", 50, 500, 150)
    
    filtered_gdf = gdf[gdf['price'] <= budget]
    
    st.write("### 🗺️ Nearby Airbnb Listings")
    map_city = folium.Map(location=[gdf.latitude.mean(), gdf.longitude.mean()], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(map_city)
    
    for sight, lat, lon, img in selected_sights:
        popup_html = f"""
        <strong>{sight}</strong><br>
        <img src='{img}' width='250'>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(map_city)
    
    for _, row in filtered_gdf.iterrows():
        popup_html = f"""
        <strong>{row['name']}</strong><br>
        <img src='{row['picture_url']}' width='250'><br>
        <b>Price:</b> €{row['price']} per night<br>
        """
        folium.Marker(
            location=[row.latitude, row.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="orange", icon="home", prefix="fa")
        ).add_to(marker_cluster)
    
    folium_static(map_city)


