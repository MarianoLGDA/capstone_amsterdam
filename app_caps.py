import streamlit as st
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
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

# Sightseeing locations (Replace with actual images and more sights)
sightseeing_spots = {
    "Rijksmuseum": (52.360001, 4.885278),
    "Anne Frank House": (52.375218, 4.883977),
    "Van Gogh Museum": (52.358416, 4.881077),
    "Dam Square": (52.373058, 4.892557),
    "Jordaan District": (52.379189, 4.880556),
    "Vondelpark": (52.358333, 4.868611),
    "Ajax Stadium": (52.314167, 4.941389),
    "A'DAM Lookout": (52.384409, 4.902568),
    "NEMO Science Museum": (52.374639, 4.912261),
    "The Heineken Experience": (52.357869, 4.891700),
}

# Streamlit UI
st.title("📍 Travel Planner: Find the Best Airbnb for Your Trip")

# Step 1: User selects city
city = st.selectbox("Which city are you visiting?", ["Amsterdam"], index=0)

# Step 2: Show sightseeing options with checkboxes
st.subheader("🎯 Select the sightseeing places you want to visit:")
selected_sights = []

for sight, coords in sightseeing_spots.items():
    if st.checkbox(sight, key=sight):
        selected_sights.append((sight, coords))

# Step 3: Ask for budget and dates
if selected_sights:
    st.subheader("💰 Select your budget and trip dates")
    budget = st.slider("What is your budget per night (in €)?", 50, 500, 150)
    start_date = st.date_input("Trip start date")
    end_date = st.date_input("Trip end date")

    # Step 4: Find nearest Airbnbs
    st.subheader("🏡 Finding the best Airbnb for you...")
    gdf = gdf[gdf['price'] <= budget]  # Filter by budget
    top_airbnbs = []
    for sight, coords in selected_sights:
        sight_location = gpd.GeoSeries([Point(coords[1], coords[0])], crs="EPSG:4326")
        gdf[f'distance_to_{sight}'] = gdf.geometry.distance(sight_location.iloc[0])
        closest_airbnbs = gdf.nsmallest(5, f'distance_to_{sight}')
        closest_airbnbs = closest_airbnbs.copy()
        closest_airbnbs["sightseeing"] = sight
        top_airbnbs.append(closest_airbnbs)
    top_airbnbs_df = pd.concat(top_airbnbs)

    # Step 5: Display results
    st.subheader("🌍 Map of Airbnb Listings near your selected sights")
    map_amsterdam = folium.Map(location=[52.365, 4.89], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(map_amsterdam)

    for sight, coords in selected_sights:
        folium.Marker(
            location=[coords[0], coords[1]],
            popup=sight,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(map_amsterdam)
    
    for _, row in top_airbnbs_df.iterrows():
        folium.Marker(
            location=[row.latitude, row.longitude],
            popup=f"Airbnb near {row['sightseeing']}\nPrice: €{row['price']}\nDistance: {row[f'distance_to_{row.sightseeing}']:.2f} meters",
            icon=folium.Icon(color="blue")
        ).add_to(marker_cluster)

    folium_static(map_amsterdam)
    
    # Step 6: Pros and Cons
    st.subheader("📌 Pros and Cons of the Area")
    pros_cons = {
        "Rijksmuseum": {"Pros": "Cultural center, near museums", "Cons": "Busy area, expensive"},
        "Anne Frank House": {"Pros": "Historic, central location", "Cons": "Crowded, limited availability"},
        "Van Gogh Museum": {"Pros": "Art district, well-connected", "Cons": "Expensive restaurants"},
        "Dam Square": {"Pros": "Lively, great public transport", "Cons": "Noisy at night"},
        "Jordaan District": {"Pros": "Trendy, local shops", "Cons": "Fewer budget stays"},
        "Vondelpark": {"Pros": "Peaceful, great for jogging", "Cons": "Far from nightlife"},
        "Ajax Stadium": {"Pros": "Sports fans, modern area", "Cons": "Far from city center"},
        "A'DAM Lookout": {"Pros": "Amazing views, modern area", "Cons": "Limited nightlife"},
        "NEMO Science Museum": {"Pros": "Family-friendly, near city center", "Cons": "Not much nightlife"},
        "The Heineken Experience": {"Pros": "Beer lovers, fun area", "Cons": "Touristy, crowded"},
    }
    for sight, _ in selected_sights:
        if sight in pros_cons:
            st.markdown(f"**{sight}**")
            st.markdown(f"✅ **Pros:** {pros_cons[sight]['Pros']}")
            st.markdown(f"❌ **Cons:** {pros_cons[sight]['Cons']}")
