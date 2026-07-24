import streamlit as st
from groq import Groq
import base64
from pathlib import Path
import re
import urllib.parse
import streamlit.components.v1 as components # For embedding live maps
# 🎙️ Browser-level mic recorder
from streamlit_mic_recorder import speech_to_text

# SECURE YOUR API KEY: Deactivate this key in Groq and use st.secrets instead!
client = Groq(api_key="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")

def set_background():
    # A calm, peaceful light sea-blue beach horizon background
    img_url = "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1920&q=80"
    
    css = f"""
    <style>
    /* Full page background style */
    .stApp {{
        background-image: url("{img_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Keeps all background text dark gray for premium legibility */
    h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown div p {{
        color: #1e293b !important;
    }}

    /* Wraps the main center area into a beautiful white frosted-glass card */
    .stMainBlockContainer {{
        background-color: rgba(255, 255, 255, 0.92) !important;
        padding: 2.5rem !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08) !important;
        margin-top: 2rem !important;
    }}

    /* Wraps the left sidebar area into a separate matching white card container */
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
        box-shadow: 4px 0 15px rgba(0, 0, 0, 0.05) !important;
    }}
    
    /* Make input text fields contrast cleanly against the background cards */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {{
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }}

    /* 
       FIX: Forces the sidebar scrolling container to allow dropdowns to render 
       outside its visible bottom area, preventing cutting off options at the bottom.
    */
    section[data-testid="stSidebar"] div.st-emotion-cache-1cypcdb {{
        overflow: visible !important;
    }}
    
    div[data-baseweb="popover"] {{
        z-index: 999999 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Helper function to inject Google Maps links dynamically
def inject_google_maps_links(text, destination_city):
    """
    Scans the text for hotel or restaurant list items and appends
    a dynamic Google Maps link with custom icons and text.
    """
    processed_lines = []
    for line in text.split('\n'):
        # Matches bullet points like: - Hotel Name or * Restaurant Name
        match = re.match(r"^(\s*[-*+]\s+)([^:\-\n]+)(.*)$", line)
        if match:
            prefix = match.group(1)       # Bullet structure (e.g., "- ")
            entity_name = match.group(2).strip()  # The name of the place
            rest_of_line = match.group(3) # Rest of the text in that line
            
            # Avoid adding maps to general sentences or non-entities
            if len(entity_name) > 3 and not entity_name.startswith(("Give", "Recommend", "Mention", "Hotel Suggestions", "Restaurant Suggestions")):
                # Create encoded Google Maps query
                query_string = f"{entity_name}, {destination_city}"
                encoded_query = urllib.parse.quote_plus(query_string)
                maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
                
                # Appends a clean, styled locator pin next to each result
                line = f"{prefix}**{entity_name}** [📍 Locate]({maps_url}){rest_of_line}"
                
        processed_lines.append(line)
    return '\n'.join(processed_lines)

# Helper function to render a live, embedded interactive map
def render_embedded_map(city_name):
    """
    Renders an interactive embedded Google Map of the destination city.
    """
    encoded_city = urllib.parse.quote_plus(city_name)
    # Using Google's public embed search endpoint
    map_url = f"https://maps.google.com/maps?q={encoded_city}&t=&z=13&ie=UTF8&iwloc=&output=embed"
    
    # Render inside an iframe
    components.iframe(map_url, height=350, scrolling=False)

# 1. Page layout configuration
st.set_page_config(
    page_title="AI Travel Guide Chatbot",
    page_icon="✈️",
    layout="wide"
)

# 2. Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Trigger the bright beach background
set_background()

# Title
st.title("🌍 AI Travel Guide Chatbot")
st.write("Plan your perfect trip with AI ✈️")

# Sidebar UI (ORIGINAL LAYOUT RESTORED)
st.sidebar.header("🧳 Travel Preferences")

# 1. Budget Inputs
budget_amount = st.sidebar.number_input(
    "💰 Enter your Budget (in ₹)",
    min_value=100, 
    max_value=500000, 
    value=1000, 
    step=500
)
budget_type = st.sidebar.radio("Budget Mode", ["Total Budget", "Budget Per Day"], horizontal=True)
budget = f"₹{budget_amount:,} ({budget_type})"

# 2. Duration Slider
days = st.sidebar.slider(
    "📅 Trip Duration (Days)",
    1, 15, 3
)

# 3. Companion Selectbox
companion = st.sidebar.selectbox(
    "👨‍👩‍👧 Travel Companion",
    ["Solo", "Friends", "Family", "Couple"]
)

# 4. Transportation Selectbox
transport = st.sidebar.selectbox(
    "🚌 Transportation",
    [
        "🚗 Private Car",
        "🚌 Public Bus",
        "🚄 Train Journey",
        "✈️ Flight",
        "🏍️ Motor Bike",
        "🚲 Bicycle"
    ]
)

# 5. Travel Type Selectbox
travel_type = st.sidebar.selectbox(
    "🏕 Travel Type",
    [
        "🧗 Adventure",
        "🏛️ Historical",
        "🏖️ Beach & Coastal",
        "💎 Luxury & Comfort",
        "🛣️ Road Trip",
        "🌿 Nature & Eco-Tourism",
        "🕌 Cultural & Heritage",
        "🏔️ Hill Station",
        "🙏 Pilgrimage",
        "🦁 Wildlife & Safari",
    ]
)

# 6. Food Preference Selectbox (Original Position)
food = st.sidebar.selectbox(
    "🍽 Food Preference",
    [
        "🥞 Breakfast & Brunch",
        "🍗 Non-Vegetarian",
        "🥗 Vegetarian",
        "🌱 Healthy & Organic",
        "🐟 Seafood & Coastal Cuisine",
        "🍢 Snacks & Street Food",
        "🍰 Desserts & Sweets",
        "🍽 Any"
    ]
)

# Invisible spacer to ensure you can always scroll down to see the food list expansion completely
st.sidebar.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)

# --- MAIN PAGE INPUTS ---

# 🎤 Voice processing helper
st.write("🎙️ **Voice input:**")
voice_input = speech_to_text(
    start_prompt="Click to start speaking your destination",
    stop_prompt="Stop recording",
    language='en',
    use_container_width=True,
    key='speech'
)

# 📍 Two-column route search layout
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("🛫 From (Departure City)", value="Vijayawada")

with col2:
    destination = st.text_input("🛬 To (Destination City)", value=voice_input if voice_input else "")

# Only trigger the planner if both fields are filled out
if origin and destination:
    route_query = f"from {origin} to {destination}"

    system_prompt = f"""
    You are an expert AI Travel Planner.
    
    User Preferences:
    Route: {origin} to {destination}
    Budget: {budget}
    Trip Duration: {days} Days
    Transportation: {transport}
    Travel Companion: {companion}
    Travel Type: {travel_type}
    Food Preference: {food}
    
    Generate a personalized travel plan taking the route and budget into consideration.
    If the budget is low (e.g., under ₹3,000), prioritize budget stays, hostels, public transit, and local street eats. No shopping will be included.
    
    Answer using these headings only:
    🌍 Route Overview
    - Give a brief description of traveling from {origin} to {destination}.
    
    🌤 Best Time to Visit
    
    📅 {days}-Day Itinerary (at {destination})
    
    🏞 Top Attractions (at {destination})
    
    🏨 Hotel Suggestions
    - Recommend 7 accommodations in {destination} according to the selected budget of {budget}.
    - Mention approximate price per night.
    
    🍽 Restaurant Suggestions
    - Recommend 7 famous restaurants/food spots in {destination} matching the food profile and budget.
    - Mention their famous dishes.
    
    🚌 Route & Transportation
    - Explain the best route options from {origin} to {destination} and why {transport} is a good option.
    - Mention approximate travel time for this option.
    
    💰 Estimated Budget
    - Hotel
    - Food
    - Transportation
    - Total Cost (Must not exceed {budget})
    
    💡 Travel Tips
    
    Keep answers simple and in bullet points.
    """

    if st.button("🗺️ Generate Travel Plan"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Create a complete personalized travel plan from {origin} to {destination}."
                }
            ]
        )

        raw_answer = response.choices[0].message.content
        
        # Parse the raw LLM text and inject custom icon map links dynamically!
        formatted_answer = inject_google_maps_links(raw_answer, destination)

        st.session_state.messages.append(("You", f"Trip from {origin} to {destination} ({budget})"))
        st.session_state.messages.append(("Bot", formatted_answer))
        
        # Store the destination city so we can render its live map below
        st.session_state.last_destination = destination

# Display interactive map if a destination has been searched
if "last_destination" in st.session_state:
    st.write(f"🗺️ **Interactive Map for {st.session_state.last_destination}:**")
    render_embedded_map(st.session_state.last_destination)

# Display clean chat history
if st.session_state.messages:
    st.subheader("💬 Chat History")
    for role, message in st.session_state.messages:
        if role == "You":
            st.write(f"👤 **{role}:** {message}")
        else:
            st.write(f"🤖 **{role}:** {message}")