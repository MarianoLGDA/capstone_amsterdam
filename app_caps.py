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

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    /* Apply global styling */
    html, body, [class*="stApp"] {
        font-family: 'Poppins', sans-serif !important;
        background-color: #0B0F28 !important;
        color: white !important;
    }

    /* TITLES */
    h1, h2 {
        color: #4DA8DA !important;
        font-weight: 600 !important;
        text-align: center;
        letter-spacing: 1px;
        text-transform: uppercase;
        animation: fadeIn 1s ease-in-out;
    }

    h3, h4, h5, h6, p, label {
        color: #E0E0E0 !important;
    }

    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #1A73E8, #4DA8DA) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0px 4px 10px rgba(77, 168, 218, 0.5);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4DA8DA, #1A73E8) !important;
        transform: scale(1.08);
        box-shadow: 0px 6px 15px rgba(77, 168, 218, 0.8);
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #162447 !important;
        padding: 20px;
    }
    
    /* SIDEBAR HEADERS */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #4DA8DA !important;
        font-weight: 600;
    }

    /* DROPDOWNS & SELECT BOXES */
    div[data-testid="stSelectbox"] label {
        font-size: 18px !important;
        color: #4DA8DA !important;
        font-weight: bold !important;
    }
    
    /* INPUT FIELDS */
    input, textarea, select {
        background-color: rgba(27, 31, 59, 0.8) !important;
        color: white !important;
        border: 1px solid #4DA8DA !important;
        border-radius: 8px !important;
        padding: 10px !important;
        backdrop-filter: blur(8px);
    }

    /* SLIDER CUSTOMIZATION */
    div[data-baseweb="slider"] > div {
        background: #4DA8DA !important;
    }

    /* CUSTOM ANIMATIONS */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(77, 168, 218, 0.5); }
        50% { box-shadow: 0 0 20px rgba(77, 168, 218, 0.8); }
        100% { box-shadow: 0 0 10px rgba(77, 168, 218, 0.5); }
    }

    /* ADD A GLOW EFFECT TO THE BUTTONS */
    .stButton > button:focus {
        animation: pulseGlow 1.5s infinite;
    }

    /* MAKE HEADINGS APPEAR GRADUALLY */
    h1, h2, h3 {
        animation: fadeIn 1.2s ease-out;
    }
    </style>
    """,
    unsafe_allow_html=True,
)




# Load logos
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("kpmg_logo.jpg", width=150)
with col3:
    st.image("airbnb_logo.jpg", width=150)

st.title("SmartStay: AI-Powered Interrail Accommodation")
# Load Airbnb data based on city selection
@st.cache_data
def load_data(city):
    file_path = f"df_{city.lower()}.csv"
    
    # Try reading with UTF-8, fallback to ISO-8859-1
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="ISO-8859-1")  # Try Latin-1 if UTF-8 fails

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
if "room_type" not in st.session_state:
    st.session_state.room_type = []
if "bedrooms" not in st.session_state:
    st.session_state.bedrooms = 1
if "review_score" not in st.session_state:
    st.session_state.review_score = 3
if "superhost" not in st.session_state:
    st.session_state.superhost = "Any"
if "gdf" not in st.session_state:
    st.session_state.gdf = None

# Back button logic
if st.session_state.step != "ask_name" and st.button("⬅️ Back"):
    steps = ["ask_name", "ask_city", "ask_sightseeing", "ask_budget", "ask_bedrooms", "ask_review_score", "ask_superhost", "ask_room_type", "show_results"]
    current_index = steps.index(st.session_state.step)
    if current_index > 0:
        st.session_state.step = steps[current_index - 1]
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
                selected_sights.append((sight, lat, lon, img))

    # Second row of sightseeing options
    cols = st.columns(5)
    for col, (sight, (lat, lon, img)) in zip(cols, second_row):
        with col:
            st.image(img, width=200)
            if st.checkbox(sight, key=sight):
                selected_sights.append((sight, lat, lon, img))

    if st.button("Confirm Sightseeing"):
        st.session_state.selected_sights = selected_sights
        st.session_state.step = "ask_budget"
        st.rerun()

# Step 4: Ask for budget
if st.session_state.step == "ask_budget":
    st.write(f"Great choices, {st.session_state.name}! 💰 Now, what's your budget per night?")
    budget = st.slider("Select your budget (€)", 50, 500, 150)

    if st.button("Confirm Budget"):
        st.session_state.budget = budget
        st.session_state.step = "ask_room_type"
        st.rerun()

# Step 5: Ask for room type
elif st.session_state.step == "ask_room_type":
    st.write(f"Almost there, {st.session_state.name}! 🏡 What type of room do you prefer?")
    room_types = st.session_state.gdf['room_type'].unique().tolist()
    selected_room_type = st.multiselect("Select room type(s):", room_types)

    if st.button("Confirm Room Type"):
        st.session_state.room_type = selected_room_type
        st.session_state.step = "ask_bedrooms"
        st.rerun()

# Step 6: Ask for number of bedrooms
elif st.session_state.step == "ask_bedrooms":
    bedrooms = st.number_input("How many bedrooms do you need?", min_value=1, max_value=10, value=1)
    if st.button("Confirm Bedrooms"):
        st.session_state.bedrooms = bedrooms
        st.session_state.step = "ask_review_score"
        st.rerun()

# Step 7: Ask for minimum review score
elif st.session_state.step == "ask_review_score":
    review_score = st.slider("Minimum review score (1-5)", 1, 5, 3)
    if st.button("Confirm Review Score"):
        st.session_state.review_score = review_score
        st.session_state.step = "ask_superhost"
        st.rerun()

# Step 8: Ask for Superhost preference
elif st.session_state.step == "ask_superhost":
    superhost = st.radio("Do you prefer a Superhost?", ["Any", "Yes", "No"])
    if st.button("Confirm Superhost Preference"):
        st.session_state.superhost = superhost
        st.session_state.step = "show_results"
        st.rerun()

# Step 6: Show map with filtered Airbnbs inside polygon and sightseeing spots
if st.session_state.step == "show_results":
    st.write(f"Here are your best options in {st.session_state.city}, {st.session_state.name}! 🎉")

    map_city = folium.Map(location=[st.session_state.gdf.latitude.mean(), st.session_state.gdf.longitude.mean()], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(map_city)

    # Add sightseeing locations
    sightseeing_coords = []
    for sight, lat, lon, img in st.session_state.selected_sights:
        sightseeing_coords.append((lon, lat))  # Append in (longitude, latitude) format for Polygon
        folium.Marker(
            location=[lat, lon], 
            popup=f"<strong>{sight}</strong><br><img src='{img}' width='250'>", 
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(map_city)

    # Create Polygon around selected sightseeing spots
    if len(sightseeing_coords) >= 3:
        sightseeing_polygon = Polygon(sightseeing_coords)
        folium.PolyLine(sightseeing_coords + [sightseeing_coords[0]], color="blue", weight=2.5, opacity=1).add_to(map_city)
        
        # Convert Polygon to GeoSeries for filtering
        polygon_gdf = gpd.GeoSeries([sightseeing_polygon], crs="EPSG:4326")

        # Filter Airbnbs inside the polygon
        filtered_gdf = st.session_state.gdf[
            (st.session_state.gdf['price'] <= st.session_state.budget) & 
            (st.session_state.gdf.geometry.within(sightseeing_polygon))
        ]

        # Add Airbnb markers
        for _, row in filtered_gdf.iterrows():
            popup_html = f"""
            <strong>{row['name']}</strong><br>
            <img src='{row['picture_url']}' width='250'><br>
            <b>Price:</b> €{row['price']} per night<br>
            <b>Type:</b> {row['property_type']} - {row['room_type']}<br>
            <b>Bedrooms:</b> {row['bedrooms']} | <b>Bathrooms:</b> {row['bathrooms']} | <b>Beds:</b> {row['beds']}<br>
            <b>Rating:</b> {row['review_scores_rating']} ⭐<br>
            """
            folium.Marker(
                location=[row.latitude, row.longitude],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="orange", icon="home", prefix="fa")
            ).add_to(marker_cluster)
    
        if filtered_gdf.empty:
            st.warning("⚠️ No Airbnb listings found within the selected area. Try adjusting your budget or choosing different sightseeing spots.")

    else:
        st.warning("⚠️ Select at least 3 sightseeing locations to filter Airbnbs by area.")

    folium_static(map_city)

import os
import openai

# ✅ Load API key correctly
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("⚠️ API key is missing. Make sure it's set in your environment variables.")

# ✅ Initialize OpenAI Client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Test OpenAI Request
response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)











