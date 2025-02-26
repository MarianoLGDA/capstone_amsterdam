import streamlit as st
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
from streamlit_folium import folium_static

# Load Airbnb data from the processed dataset
@st.cache_data
def load_data():
    file_path = "df_amsterdam.csv"  # Processed data from Jupyter Notebook
    df = pd.read_csv(file_path)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )
    return gdf

gdf = load_data()

# Sightseeing locations with images
sightseeing_spots = {
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
}

# Streamlit UI
st.title("📍 Travel Planner: Find the Best Airbnb for Your Trip")

# Step 1: User selects city
city = st.selectbox("Which city are you visiting?", ["Amsterdam"], index=0)

# Step 2: Show sightseeing options with images in a 5x2 grid
st.subheader("🎯 Select the sightseeing places you want to visit:")
selected_sights = []

sightseeing_list = list(sightseeing_spots.items())
first_row = sightseeing_list[:5]
second_row = sightseeing_list[5:]

# First row (5 images)
cols = st.columns(5)
for col, (sight, (lat, lon, img)) in zip(cols, first_row):
    with col:
        st.image(img, width=200)
        if st.checkbox(sight, key=sight):
            selected_sights.append((sight, lat, lon))

# Second row (5 images)
cols = st.columns(5)
for col, (sight, (lat, lon, img)) in zip(cols, second_row):
    with col:
        st.image(img, width=200)
        if st.checkbox(sight, key=sight):
            selected_sights.append((sight, lat, lon))

# Step 3: Ask for property type, room type, budget, and dates
if selected_sights:
    st.subheader("🏡 Filter Your Airbnb Preferences")
    property_types = gdf['property_type'].unique().tolist()
    room_types = gdf['room_type'].unique().tolist()
    
    selected_property_type = st.selectbox("Select property type", ["Any"] + property_types)
    selected_room_type = st.selectbox("Select room type", ["Any"] + room_types)
    
    budget = st.slider("What is your budget per night (in €)?", 50, 500, 150)
    start_date = st.date_input("Trip start date")
    end_date = st.date_input("Trip end date")

    # Step 4: Find Airbnbs in the area between selected sights
    st.subheader("🏡 Finding the best Airbnb for you...")
    gdf = gdf[gdf['price'] <= budget]  # Filter by budget
    
    if selected_property_type != "Any":
        gdf = gdf[gdf['property_type'] == selected_property_type]
    if selected_room_type != "Any":
        gdf = gdf[gdf['room_type'] == selected_room_type]
    
    if len(selected_sights) >= 3:
        polygon = Polygon([(lon, lat) for _, lat, lon in selected_sights])
        gdf = gdf[gdf.geometry.within(polygon)]  # Filter Airbnbs within the selected area
    else:
        st.warning("⚠️ Select at least 3 sightseeing locations to filter Airbnbs by area.")

    # Step 5: Display results
    st.subheader("🌍 Map of Airbnb Listings near your selected sights")
    map_amsterdam = folium.Map(location=[52.365, 4.89], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(map_amsterdam)

    for _, row in gdf.iterrows():
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
            icon=folium.Icon(color="blue")
        ).add_to(marker_cluster)
    
    folium_static(map_amsterdam)
