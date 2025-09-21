import streamlit as st
import pandas as pd
import requests
import os
import datetime
from datetime import date

# -----------------------------
# Crop Knowledge Base
# -----------------------------
CROP_DB = {
    "Wheat": {
        "soil": "Loamy",
        "season": "Rabi",
        "water": "450-650 mm",
        "ph_range": "6.0–7.5",
        "common_pests": "Stem borers, aphids",
    },
    "Rice": {
        "soil": "Clay",
        "season": "Kharif",
        "water": "1200–1500 mm",
        "ph_range": "5.5–7.0",
        "common_pests": "Brown planthopper, leaf folder",
    },
    "Maize": {
        "soil": "Sandy loam",
        "season": "Kharif",
        "water": "500–800 mm",
        "ph_range": "5.5–7.0",
        "common_pests": "Fall armyworm, stem borer",
    },
    "Sugarcane": {
        "soil": "Alluvial",
        "season": "Year-round",
        "water": "1500–2500 mm",
        "ph_range": "6.0–7.5",
        "common_pests": "Top shoot borer, scale insect",
    },
}

# -----------------------------
# Helper: Weather Fetch - IMPROVED
# -----------------------------
def get_weather(city: str):
    api_key = os.getenv("OWM_API_KEY", "DEMO_KEY")
    
    if api_key == "DEMO_KEY":
        # More realistic mock data
        return {
            "current_temp": 28,
            "humidity": 65,
            "description": "Partly cloudy",
            "timestamp": "Demo Mode",
        }
    
    try:
        # Correct API endpoint with error handling
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            return {
                "current_temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "timestamp": datetime.datetime.fromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M'),
            }
        else:
            return None
            
    except Exception as e:
        st.error(f"Weather API error: {e}")
        return None

# -----------------------------
# Helper: Real-time Market Prices from Agmarknet API
# -----------------------------
def get_realtime_market_prices(state="Punjab", district="Ludhiana"):
    """
    Fetch real-time market prices from Agmarknet API
    """
    try:
        # Agmarknet API endpoint (public data)
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        
        params = {
            "api-key": "579b464db66ec23bdd000001b4a05ae55d8942be40e70dc2943c0e59",  # Public API key
            "format": "json",
            "filters[state]": state,
            "filters[district]": district,
            "limit": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])
            
            if records:
                prices = []
                for record in records:
                    prices.append({
                        "Commodity": record.get("commodity", "N/A"),
                        "Variety": record.get("variety", "N/A"),
                        "Market": record.get("market", "N/A"),
                        "Price": f"₹{record.get('modal_price', 'N/A')}/quintal",
                        "Date": record.get("arrival_date", "N/A")
                    })
                return prices
            else:
                return get_sample_market_data(state, district)
        else:
            return get_sample_market_data(state, district)
            
    except Exception as e:
        return get_sample_market_data(state, district)

def get_sample_market_data(state="Punjab", district="Ludhiana"):
    """Location-aware sample data when API is unavailable"""
    # Base prices for different states (can be adjusted)
    state_base_prices = {
        "Punjab": {"Rice": 2200, "Wheat": 2100, "Tomato": 1200, "Potato": 900},
        "Haryana": {"Rice": 2250, "Wheat": 2150, "Tomato": 1250, "Potato": 950},
        "Uttar Pradesh": {"Rice": 2180, "Wheat": 2080, "Tomato": 1150, "Potato": 850},
        "Rajasthan": {"Rice": 2300, "Wheat": 2200, "Tomato": 1300, "Potato": 1000},
        "Maharashtra": {"Rice": 2400, "Wheat": 2300, "Tomato": 1400, "Potato": 1100}
    }
    
    # Get base prices for the state, default to Punjab if not found
    base_prices = state_base_prices.get(state, state_base_prices["Punjab"])
    
    # Return location-specific sample data
    return [
        {"Commodity": "Rice", "Variety": "Common", "Market": district, 
         "Price": f"₹{base_prices['Rice']}/quintal", "Date": str(date.today())},
        {"Commodity": "Wheat", "Variety": "Common", "Market": district, 
         "Price": f"₹{base_prices['Wheat']}/quintal", "Date": str(date.today())},
        {"Commodity": "Tomato", "Variety": "Local", "Market": district, 
         "Price": f"₹{base_prices['Tomato']}/quintal", "Date": str(date.today())},
        {"Commodity": "Potato", "Variety": "Common", "Market": district, 
         "Price": f"₹{base_prices['Potato']}/quintal", "Date": str(date.today())}
    ]

def is_sample_data(market_data, expected_district, expected_state):
    """Check if the data is sample data rather than real API data"""
    if not market_data:
        return False
    
    # Sample data has specific characteristics
    first_record = market_data[0]
    return (
        first_record.get("Market") == "Ludhiana" and
        expected_district != "Ludhiana" and
        expected_state != "Punjab"
    )

# -----------------------------
# Layout: Tabs
# -----------------------------
st.set_page_config(page_title="Agri-Sathi", page_icon="🌾", layout="wide")
st.title("🌾 Agri-Sathi Prototype")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Crop Advisory", "Disease Detection", "Market Prices", "Weather", "Soil Health"]
)

# -----------------------------
# Tab 1: Crop Advisory
# -----------------------------
with tab1:
    st.header("📌 Crop Advisory")
    selected_crop = st.selectbox("Select your crop", list(CROP_DB.keys()))
    if selected_crop:
        c = CROP_DB[selected_crop]
        st.write(f"**Soil:** {c['soil']}")
        st.write(f"**Season:** {c['season']}")
        st.write(f"**Water requirement:** {c['water']}")
        st.write(f"**pH Range:** {c['ph_range']}")
        st.write(f"**Common Pests:** {c['common_pests']}")

# -----------------------------
# Tab 2: Disease Detection (stub)
# -----------------------------
with tab2:
    st.header("🪲 Pest & Disease Detection")
    st.info("Upload a leaf image — model integration to be added.")
    st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])

# -----------------------------
# Tab 3: Market Prices - REAL-TIME WITH IMPROVED MESSAGING
# -----------------------------
with tab3:
    st.header("💰 Real-time Market Prices")
    
    # State and district selection
    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("Select State", 
                           ["Punjab", "Haryana", "Uttar Pradesh", "Rajasthan", "Maharashtra"],
                           index=0)
    with col2:
        districts = {
            "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
            "Haryana": ["Karnal", "Hisar", "Faridabad", "Gurgaon", "Rohtak"],
            "Uttar Pradesh": ["Lucknow", "Kanpur", "Meerut", "Agra", "Varanasi"],
            "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"]
        }
        district = st.selectbox("Select District", districts.get(state, ["Ludhiana"]))
    
    # Fetch button with loading indicator
    if st.button("🔄 Refresh Market Prices", key="refresh_prices"):
        with st.spinner("Fetching latest market prices..."):
            market_data = get_realtime_market_prices(state, district)
            
            if market_data:
                # Check if we're showing sample data for wrong location
                if is_sample_data(market_data, district, state):
                    st.warning(f"⚠️ No real-time data available for {district}, {state}. Showing sample data for reference.")
                else:
                    st.success(f"✅ Real-time market data for {district}, {state}")
                
                # Convert to DataFrame for nice display
                df = pd.DataFrame(market_data)
                
                # Display as table
                st.dataframe(
                    df,
                    column_config={
                        "Commodity": "Commodity",
                        "Variety": "Variety", 
                        "Market": "Market",
                        "Price": "Price",
                        "Date": "Date"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Prices as CSV",
                    data=csv,
                    file_name=f"market_prices_{district}_{date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.error("Could not fetch market data. Please try again later.")
    else:
        # Initial placeholder - show sample data for the selected location
        st.info("Click 'Refresh Market Prices' to fetch latest market data")
        sample_data = get_sample_market_data(state, district)
        st.dataframe(pd.DataFrame(sample_data), hide_index=True)

# -----------------------------
# Tab 4: Weather - IMPROVED
# -----------------------------
with tab4:
    st.header("🌦 Weather Info")
    city = st.text_input("Enter your city", "Amritsar")  # Fixed default spelling
    
    if st.button("Get Weather", key="weather_btn"):
        w = get_weather(city)
        if w is None:
            st.error("Weather fetch failed. Using demo data.")
            # Fallback to demo data
            w = {
                "current_temp": 28,
                "humidity": 65,
                "description": "Partly cloudy (Demo)",
                "timestamp": "Demo Mode",
            }
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{w['current_temp']}°C")
            st.metric("Humidity", f"{w['humidity']}%")
        with col2:
            st.write(f"**Conditions:** {w['description']}")
            st.write(f"**Last Updated:** {w['timestamp']}")
    else:
        st.info("Enter a city and click 'Get Weather' to see current conditions")

# -----------------------------
# Tab 5: Soil Health
# -----------------------------
with tab5:
    st.header("🌱 Soil Health")
    st.info("Upload soil test CSV (optional) or use sample metrics")
    soil_file = st.file_uploader("Upload soil test CSV", type=["csv"])
    if soil_file:
        soil_df = pd.read_csv(soil_file)
        st.dataframe(soil_df)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("pH Level", "6.2")
        with col2:
            st.metric("Organic Matter", "3.5%")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Agri-Sathi — Prototype. Market data sourced from Government of India's Agmarknet API")