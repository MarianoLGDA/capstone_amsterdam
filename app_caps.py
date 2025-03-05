import os
import openai
import time
import random

# Load OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure to set this up securely!

st.subheader("💬 SmartStay AI Chatbot: Plan Your Trip!")

# List of random salutations for each interaction
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

    # Check if the user has selected a valid city
    city = user_input.strip().title()
    if city not in ["Amsterdam", "Barcelona"]:
        bot_reply = "Sorry, we currently support only Amsterdam and Barcelona. Please choose one of these cities. 😊"
    else:
        bot_reply = f"Great! You're visiting **{city}**. Now, select the sightseeing places you want to visit!"

        # Display sightseeing options dynamically in two rows
        selected_sights = []
        sightseeing_list = list(sightseeing_spots[city].items())
        first_row = sightseeing_list[:5]
        second_row = sightseeing_list[5:]

        # First row (5 images)
        cols = st.columns(5)
        for col, (sight, (lat, lon, img)) in zip(cols, first_row):
            with col:
                st.image(img, width=200)
                if st.checkbox(sight, key=sight):
                    selected_sights.append((sight, lat, lon, img))

        # Second row (5 images)
        cols = st.columns(5)
        for col, (sight, (lat, lon, img)) in zip(cols, second_row):
            with col:
                st.image(img, width=200)
                if st.checkbox(sight, key=sight):
                    selected_sights.append((sight, lat, lon, img))

        # Ask budget
        bot_reply += "\n\n💰 **What is your budget per night (in €)?**"
        budget = st.number_input("Enter your budget (€):", min_value=50, max_value=500, step=10)

        # Ask property type
        bot_reply += "\n\n🏡 **What type of property are you looking for?**"
        property_types = gdf['property_type'].unique().tolist()
        selected_property_type = st.multiselect("Select property type(s):", property_types)

        # Ask for minimum review score
        bot_reply += "\n\n⭐ **Minimum review score?**"
        review_score = st.slider("Select a minimum review score (1-100):", 50, 100, 80)

        # Filter Airbnbs based on user selections
        filtered_gdf = gdf[gdf['price'] <= budget]
        if selected_property_type:
            filtered_gdf = filtered_gdf[filtered_gdf['property_type'].isin(selected_property_type)]
        filtered_gdf = filtered_gdf[filtered_gdf['review_scores_rating'] >= review_score]

        # If at least 3 sightseeing places are selected, filter within the area
        if len(selected_sights) >= 3:
            polygon = Polygon([(lon, lat) for _, lat, lon, _ in selected_sights])
            filtered_gdf = filtered_gdf[filtered_gdf.geometry.within(polygon)]
            bot_reply += "\n\n📍 **Here are the best accommodations within your selected zone:**"
        else:
            bot_reply += "\n\n⚠️ Please select at least 3 sightseeing locations to filter Airbnbs by area."

        # Display the map with filtered Airbnbs
        if not filtered_gdf.empty:
            map_city = folium.Map(location=[gdf.latitude.mean(), gdf.longitude.mean()], zoom_start=13)
            marker_cluster = MarkerCluster().add_to(map_city)

            # Add sightseeing locations to the map
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

            folium_static(map_city)

            # Generate zone-based recommendations
            bot_reply += "\n\n🛎️ **Here are some recommendations for the area you've chosen:**"
            if city == "Amsterdam":
                bot_reply += "\n- **Jordaan District**: A vibrant area full of local cafes and markets. *Pros: Artistic vibe, close to main attractions. Cons: Can be pricey.*"
                bot_reply += "\n- **De Pijp**: A lively neighborhood with great nightlife and food. *Pros: Cheaper than city center, lots of entertainment. Cons: Noisy at night.*"
            elif city == "Barcelona":
                bot_reply += "\n- **Gothic Quarter**: A historic neighborhood filled with culture. *Pros: Walkable, rich history. Cons: Can be crowded.*"
                bot_reply += "\n- **El Born**: A trendy district perfect for food lovers. *Pros: Stylish, good bars. Cons: Accommodations can be expensive.*"

    # Append bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Display bot response
    with st.chat_message("assistant"):
        st.write(bot_reply)

    # Simulate typing effect
    time.sleep(1)









