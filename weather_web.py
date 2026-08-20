import streamlit as st
import requests
import xml.etree.ElementTree as ET
import yfinance as yf # New library for free stock data
import os

# 1. Page Config
st.set_page_config(page_title="My Morning Command Center", page_icon="☀️", layout="wide")

# --- SIDEBAR: STOCK TICKERS ---
with st.sidebar:
    st.header("📈 Market Watch")
    st.write("Real-time quotes via Yahoo Finance")
    
    # Define the tickers you want to track (Index, Tech, etc.)
    # Format: {"Display Name": "Yahoo Ticker Symbol"}
    tickers_to_track = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Nvidia": "NVDA"
    }
    
    for display_name, symbol in tickers_to_track.items():
        try:
            # Fetch stock data
            ticker = yf.Ticker(symbol)
            # Fast info lookup (using historical data for price/previous close)
            history = ticker.history(period="2d")
            
            if len(history) >= 2:
                current_price = history['Close'].iloc[-1]
                prev_close = history['Close'].iloc[-2]
                price_change = current_price - prev_close
                pct_change = (price_change / prev_close) * 100
                
                # Format metrics with arrows and delta colors (Green for up, Red for down)
                st.metric(
                    label=display_name,
                    value=f"${current_price:,.2f}",
                    delta=f"{price_change:+.2f} ({pct_change:+.2f}%)"
                )
            else:
                # Fallback if market is closed or 2d history isn't loaded yet
                info = ticker.fast_info
                current_price = info.get('last_price', 0.0)
                st.metric(label=display_name, value=f"${current_price:,.2f}")
                
        except Exception as stock_err:
            st.error(f"Error loading {display_name}: {stock_err}")
            
    st.divider()
    if st.button("🔄 Refresh All Data"):
        st.rerun()

# --- MAIN PAGE ---
st.title("☀️ My Morning Command Center")
st.write("Start your day with weather, markets, and the latest headlines.")
st.divider()

# Layout main page into columns
left_col, right_col = st.columns([1, 1])

with left_col:
    # --- WEATHER SECTION ---
    st.subheader("🌤️ Minneapolis Weather")
    
# Temporary debug check
if "OPENWEATHER_API_KEY" not in st.secrets:
    st.error("⚠️ Streamlit cannot find 'OPENWEATHER_API_KEY' in your Secrets dashboard!")
    st.stop()
else:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]

    LAT = 44.9778
    LON = -93.2650

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"

    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        data = response.json()
        
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description'].title()
        wind_speed = data['wind']['speed']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Temperature", value=f"{temp} °F")
            st.metric(label="Feels Like", value=f"{feels_like} °F")
        with col2:
            st.metric(label="Humidity", value=f"{humidity}%")
            st.metric(label="Wind Speed", value=f"{wind_speed} mph")
            
        st.info(f"**Current Condition:** {description}")

    except Exception as err:
        st.error(f"Failed to fetch weather data: {err}")

with right_col:
    # --- NEWS SECTION ---
    st.subheader("📰 Top 5 News Headlines")

    rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

    try:
        news_response = requests.get(rss_url)
        news_response.raise_for_status()
        
        root = ET.fromstring(news_response.content)
        items = root.findall('./channel/item')[:5]
        
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            
            # Display clean clickable links
            st.markdown(f"🔹 **[{title}]({link})**")
            
    except Exception as e:
        st.error(f"Failed to fetch news headlines: {e}")
