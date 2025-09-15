import streamlit as st
import requests
import numpy as np
import pandas as pd
import joblib
import plotly.express as px

# -----------------------
# 1. Config
# -----------------------
API_KEY = "3be1499df7555fcbab646b12d80116ce"  # Replace with your OpenWeatherMap API key
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "http://openweathermap.org/img/wn/"

# Load ML model
model = joblib.load("rainfall_model.pkl")

# -----------------------
# 2. Streamlit UI
# -----------------------
st.set_page_config(page_title="Weather & Rainfall Forecast", layout="wide")
st.title("🌦️ Weather & Rainfall Forecast")

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------
# 3. User Input
# -----------------------
cities_input = st.text_input("Enter City Names (comma-separated):", "Delhi,Mumbai,Bangalore")
cities = [city.strip() for city in cities_input.split(",")]

city_data = []

for city in cities:
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        forecast_list = data["list"]
        city_info = data["city"]

        records = []
        for entry in forecast_list:
            dt_txt = entry["dt_txt"]
            main = entry["main"]
            wind = entry["wind"]
            clouds = entry["clouds"]["all"]
            rain = entry.get("rain", {}).get("3h", 0)
            weather_desc = entry["weather"][0]["description"]
            icon = entry["weather"][0]["icon"]

            temp = main["temp"]
            temp_min = main["temp_min"]
            temp_max = main["temp_max"]
            humidity = main["humidity"]
            pressure = main["pressure"]
            wind_speed = wind["speed"]
            wind_deg = wind.get("deg", 0)

            # ML Rain Prediction
            features = np.array([[temp, humidity, pressure]])
            prob_rain = model.predict_proba(features)[0][1] * 100
            prediction = "🌧️ Rain Likely" if prob_rain > 50 else "☀️ No Rain"

            records.append([
                dt_txt, temp, temp_min, temp_max, humidity, pressure,
                wind_speed, wind_deg, clouds, rain, weather_desc, icon,
                prob_rain, prediction
            ])

        columns = [
            "DateTime", "Temp (°C)", "Temp Min (°C)", "Temp Max (°C)",
            "Humidity (%)", "Pressure (hPa)", "Wind Speed (m/s)",
            "Wind Deg (°)", "Cloudiness (%)", "Rain (mm/3h)",
            "Weather", "Icon", "Rain Probability (%)", "Prediction"
        ]

        df = pd.DataFrame(records, columns=columns)
        df["Date"] = pd.to_datetime(df["DateTime"]).dt.date

        city_data.append({
            "name": city,
            "df": df,
            "city_info": city_info,
            "current": df.iloc[0]
        })
    else:
        st.error(f"❌ City '{city}' not found or API error.")

# -----------------------
# 4. Display Multi-City Weather Cards with Alerts
# -----------------------
st.subheader("🌇 Current Weather for Cities")
for city_entry in city_data:
    city_name = city_entry["name"]
    current = city_entry["current"]
    prob_rain = current["Rain Probability (%)"]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(f"{ICON_URL}{current['Icon']}@2x.png", width=100)
    with col2:
        st.markdown(f"### {city_name}")
        st.metric("Temperature", f"{current['Temp (°C)']} °C")
        st.metric("Humidity", f"{current['Humidity (%)']} %")
        st.metric("Pressure", f"{current['Pressure (hPa)']} hPa")
        st.metric("Wind Speed", f"{current['Wind Speed (m/s)']} m/s")
        st.metric("Cloudiness", f"{current['Cloudiness (%)']} %")
        st.markdown(f"**Weather:** {current['Weather'].title()}")

        # Color-coded rain alert
        st.markdown(f"**Rain Probability:** {prob_rain:.1f}%")
        if prob_rain < 30:
            st.success("☀️ Low chance of rain")
        elif prob_rain < 60:
            st.warning("⛅ Moderate chance of rain")
        else:
            st.error("🌧️ High chance of rain")

# -----------------------
# 5. Multi-City Hourly Rain Probability Chart (Colored Dots)
# -----------------------
st.subheader("📈 Hourly Rain Probability Trend (Colored by Risk)")

fig = px.scatter()
for city_entry in city_data:
    df = city_entry["df"]

    # Assign color based on probability
    def get_color(prob):
        if prob < 30:
            return "green"
        elif prob < 60:
            return "yellow"
        else:
            return "red"

    df["Color"] = df["Rain Probability (%)"].apply(get_color)

    fig.add_scatter(
        x=df["DateTime"],
        y=df["Rain Probability (%)"],
        mode="lines+markers",
        marker=dict(color=df["Color"], size=10),
        name=city_entry["name"]
    )

fig.update_layout(
    yaxis_title="Rain Probability (%)",
    xaxis_title="DateTime",
    xaxis=dict(tickangle=45)
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 6. Hourly Forecast Table per City (clean border)
# -----------------------
for city_entry in city_data:
    st.subheader(f"⏰ Hourly Forecast - {city_entry['name']}")
    df = city_entry["df"]
    display_cols = ["DateTime", "Temp (°C)", "Humidity (%)", "Pressure (hPa)",
                    "Wind Speed (m/s)", "Cloudiness (%)", "Rain (mm/3h)",
                    "Weather", "Rain Probability (%)", "Prediction"]
    st.dataframe(df[display_cols].style.set_properties(**{'border': 'none'}).format({"Rain Probability (%)": "{:.1f}%"}))

# -----------------------
# 7. Interactive Map with Hover Tooltips
# -----------------------
st.subheader("🗺️ Interactive City Map with Rain Alerts")

if city_data:
    map_df = pd.DataFrame([{
        "lat": c['city_info']['coord']['lat'],
        "lon": c['city_info']['coord']['lon'],
        "city": c['name'],
        "rain_prob": c["current"]["Rain Probability (%)"]
    } for c in city_data])

    # Color logic
    def get_map_color(prob):
        if prob < 30:
            return "green"
        elif prob < 60:
            return "yellow"
        else:
            return "red"

    map_df["color"] = map_df["rain_prob"].apply(get_map_color)

    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        hover_name="city",
        hover_data={"rain_prob": True, "lat": False, "lon": False},
        color="color",
        size=np.full(len(map_df), 15),
        zoom=4,
        mapbox_style="carto-positron"
    )

    st.plotly_chart(fig_map, use_container_width=True)
