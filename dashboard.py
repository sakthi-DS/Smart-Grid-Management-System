import streamlit as st
import json
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

st_autorefresh(interval=3000, key="refresh")

st.title("Smart Grid Management System")

def load_json(file):
    try:
        with open(file) as f:
            return json.load(f)
    except:
        return {}

area_data = load_json("area_state.json")
grid_state = load_json("grid_state.json")

try:
    with open("decision_log.json") as f:
        log_data = json.load(f)
except:
    log_data = []

st.subheader("Area Status")

cols = st.columns(3)

areas = ["Area1","Area2","Area3"]

for i,area in enumerate(areas):

    with cols[i]:

        st.markdown(f"### {area}")

        if area in area_data:

            data = area_data[area]

            st.metric("Solar Production (MW)", round(data["solar"],2))
            st.metric("Wind Production (MW)", round(data["wind"],2))

            st.metric("Supply (MW)", round(data["supply"],2))
            st.metric("Demand (MW)", round(data["demand"],2))

            balance = data["supply"] - data["demand"]

            if balance >= 0:
                st.success("Grid Stable")
            else:
                st.error("Grid Deficit")

            st.caption(
                f"""
Temperature: {round(data['temperature'],2)} °C  
Cloud Cover: {data['cloud_cover']} %  
Wind Speed: {round(data['wind_speed'],2)} m/s  
EV Load: {data['ev_load']} MW  
House Demand: {data['house_demand']} MW
"""
            )

        else:
            st.info("Waiting for simulator data...")


st.divider()

st.subheader("Battery Status")

battery = grid_state.get("battery",0)
capacity = 1000

percent = battery / capacity if capacity > 0 else 0

st.progress(percent)

c1,c2,c3 = st.columns(3)

c1.metric("Battery Level (MW)", round(battery,2))
c2.metric("Battery Capacity (MW)", capacity)
c3.metric("Charge %", round(percent*100,2))


st.divider()

st.subheader("Grid Decisions")

def format_routing(routes):

    if not routes:
        return ["No routing"]

    output = []

    for r in routes:

        if r["type"] == "battery_supply":
            output.append(
                f"🔋 Battery → {r['to']} : {round(r['power'],2)} MW"
            )

        elif r["type"] == "battery_store":
            output.append(
                f"⚡ {r['area']} → Battery : {round(r['power'],2)} MW"
            )

        elif r["type"] == "area_transfer":
            route_path = " → ".join(r["route"])
            output.append(
                f"🔁 {r['from']} → {r['to']} : {round(r['power'],2)} MW | {route_path}"
            )

        elif r["type"] == "plant_supply":
            route_path = " → ".join(r["route"])
            output.append(
                f"🏭 Plant → {r['to']} : {round(r['power'],2)} MW | {route_path}"
            )

    return output


if len(log_data) > 0:

    for entry in log_data[:10]:

        st.markdown(f"### ⏱ {entry['time']}")

        routes = format_routing(entry["routing"])

        for r in routes:

            st.markdown(
                f"<p style='font-size:22px; font-weight:600;'>{r}</p>",
                unsafe_allow_html=True
            )

        st.divider()

else:

    st.info("Waiting for decisions...")
