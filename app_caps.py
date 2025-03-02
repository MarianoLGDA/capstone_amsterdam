import streamlit as st
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
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

# Apply new color theme
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1E1E2F;
        color: #EAEAEA;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: #FFD700;
    }
    .stButton>button {
        background-color: #FF5733;
        color: white;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] {
        background-color: #25274D;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Welcome message
st.markdown(
    """
    ## 🌍 Welcome to SmartStay! 🚆
    **Your AI-powered travel assistant for Interrail adventures!**
    
    Planning your European journey has never been easier. With SmartStay, you can:
    - **Find the best Airbnb accommodations** tailored to your trip.
    - **Discover top sightseeing spots** and stay near them.
    - **Optimize your travel budget** with smart recommendations.
    
    Whether you're exploring **Amsterdam** or **Barcelona**, SmartStay helps you **save time and money** while ensuring an amazing experience!
    """
)

# Load logos
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("kpmg_logo.jpg", width=100)
with col3:
    st.image("airbnb_logo.jpg", width=100)

st.title("SmartStay: AI-Powered Interrail Accommodation")

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

# Ensure filters and maps appear after selecting sightseeing spots
if selected_sights:
    st.subheader("🏡 Filter Your Airbnb Preferences")
    property_types = gdf['property_type'].unique().tolist()
    room_types = gdf['room_type'].unique().tolist()
    
    selected_property_type = st.selectbox("Select property type", ["Any"] + property_types)
    selected_room_type = st.selectbox("Select room type", ["Any"] + room_types)
    budget = st.slider("What is your budget per night (in €)?", 50, 500, 150)
    
    # Display map
    st.write("### 🗺️ Nearby Airbnb Listings")
    map_city = folium.Map(location=[gdf.latitude.mean(), gdf.longitude.mean()], zoom_start=13)
    folium_static(map_city)

