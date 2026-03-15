import random
import time
import math
import json
import pandas as pd
import joblib

from grid_network import create_grid, route_power


# -----------------------------
# Load AI models
# -----------------------------

solar_model = joblib.load("../models/solar_model.pkl")
wind_model = joblib.load("../models/wind_model.pkl")
demand_model = joblib.load("../models/demand_model.pkl")


# -----------------------------
# Create grid
# -----------------------------

grid = create_grid()

areas = ["Area1", "Area2", "Area3"]


# -----------------------------
# Battery system
# -----------------------------

battery_capacity = 1000
battery_level = 500


# -----------------------------
# Lag values
# -----------------------------

previous_demands = {"Area1":350,"Area2":350,"Area3":350}
previous_ev = {"Area1":120,"Area2":120,"Area3":120}
previous_house = {"Area1":300,"Area2":300,"Area3":300}


# -----------------------------
# Weather simulation
# -----------------------------

def simulate_weather(hour):

    temperature = 25 + 8 * math.sin((hour - 6) / 24 * 2 * math.pi)

    cloud_cover = random.randint(10,80)

    wind_speed = random.uniform(3,12)

    if 6 <= hour <= 18:
        solar_radiation = 900 * math.sin((hour - 6) / 12 * math.pi)
    else:
        solar_radiation = 0

    solar_radiation = max(0, solar_radiation * (1 - cloud_cover/100))

    return temperature,cloud_cover,wind_speed,solar_radiation


# -----------------------------
# Sensor simulation
# -----------------------------

def generate_sensor_data():

    ev_load = random.randint(80,200)
    house_demand = random.randint(200,400)

    return ev_load,house_demand

# -----------------------------
# Reset logs when simulator starts
# -----------------------------

with open("../decision_log.json","w") as f:
    json.dump([],f)

with open("../grid_state.json","w") as f:
    json.dump({},f)

with open("../area_state.json","w") as f:
    json.dump({},f)

# -----------------------------
# Real-time simulation
# -----------------------------

while True:

    now = pd.Timestamp.now()

    routing_actions = []

    hour = now.hour + now.minute/60
    day = now.day
    month = now.month

    deficits = {}
    surpluses = {}
    area_states = {}

    print("\n==============================")
    print("AI SMART GRID CONTROLLER")
    print("==============================")
    print("Time:",now)
    print("Battery Level:",battery_level,"/",battery_capacity)


    for area in areas:

        temperature,cloud,wind_speed,solar_rad = simulate_weather(hour)

        ev_load,house_demand = generate_sensor_data()


        # solar prediction

        solar_input = pd.DataFrame([{
            "hour":hour,
            "temperature":temperature,
            "cloud_cover":cloud,
            "solar_radiation":solar_rad
        }])

        predicted_solar = float(max(0,solar_model.predict(solar_input)[0]))


        # wind prediction

        wind_input = pd.DataFrame([{
            "wind_speed":wind_speed,
            "hour":hour
        }])

        predicted_wind = float(max(0,wind_model.predict(wind_input)[0]))

        predicted_supply = float(predicted_solar + predicted_wind)


        # demand prediction

        demand_input = pd.DataFrame([{
            "ev_load":ev_load,
            "house_demand":house_demand,
            "temperature":temperature,
            "hour":hour,
            "day":day,
            "month":month,
            "ev_lag1":previous_ev[area],
            "house_lag1":previous_house[area],
            "demand_lag1":previous_demands[area]
        }])

        predicted_demand = float(max(0,demand_model.predict(demand_input)[0]))


        previous_ev[area] = ev_load
        previous_house[area] = house_demand
        previous_demands[area] = predicted_demand


        print("\n",area)
        print("Solar:",round(predicted_solar,2))
        print("Wind:",round(predicted_wind,2))
        print("Supply:",round(predicted_supply,2))
        print("Demand:",round(predicted_demand,2))


        area_states[area] = {
            "temperature": float(temperature),
            "wind_speed": float(wind_speed),
            "cloud_cover": float(cloud),
            "ev_load": float(ev_load),
            "house_demand": float(house_demand),
            "solar": float(predicted_solar),
            "wind": float(predicted_wind),
            "supply": float(predicted_supply),
            "demand": float(predicted_demand)
        }


        balance = predicted_supply - predicted_demand

        if balance > 0:
            surpluses[area] = float(balance)
        else:
            deficits[area] = float(abs(balance))


    print("\nSurpluses:",surpluses)
    print("Deficits:",deficits)


    # -----------------------------
    # Battery storage
    # -----------------------------

    for area in surpluses:

        surplus = surpluses[area]

        space = battery_capacity - battery_level

        stored = min(surplus,space)

        battery_level += stored
        surpluses[area] -= stored

        if stored > 0:

            routing_actions.append({
                "type":"battery_store",
                "area":area,
                "power":float(stored)
            })

            print("Stored",stored,"MW in battery")


    # -----------------------------
    # Handle deficits
    # -----------------------------

    for deficit_area in deficits:

        deficit = deficits[deficit_area]


        # battery supply

        if battery_level > 0:

            discharge = min(deficit,battery_level)

            battery_level -= discharge
            deficit -= discharge

            routing_actions.append({
                "type":"battery_supply",
                "to":deficit_area,
                "power":float(discharge)
            })

            print("Battery supplied",discharge,"MW to",deficit_area)


        # area transfer

        if deficit > 0:

            for surplus_area in surpluses:

                if surpluses[surplus_area] > 0:

                    transfer = min(deficit,surpluses[surplus_area])

                    path = route_power(grid,surplus_area,deficit_area,transfer)

                    routing_actions.append({
                        "type":"area_transfer",
                        "from":surplus_area,
                        "to":deficit_area,
                        "power":float(transfer),
                        "route":path
                    })

                    surpluses[surplus_area] -= transfer
                    deficit -= transfer

                    print("Transfer",transfer,"MW",surplus_area,"→",deficit_area)

                    if deficit <= 0:
                        break


        # plant supply

        if deficit > 0:

            path = route_power(grid,"Plant",deficit_area,deficit)

            routing_actions.append({
                "type":"plant_supply",
                "from":"Plant",
                "to":deficit_area,
                "power":float(deficit),
                "route":path
            })

            print("Plant supplied",deficit,"MW to",deficit_area)


    # -----------------------------
    # Save state
    # -----------------------------

    grid_state = {
        "time":str(now),
        "battery":float(battery_level),
        "surpluses": {k:float(v) for k,v in surpluses.items()},
        "deficits": {k:float(v) for k,v in deficits.items()}
    }

    with open("../grid_state.json","w") as f:
        json.dump(grid_state,f,indent=4)


    with open("../area_state.json","w") as f:
        json.dump(area_states,f,indent=4)


    log_entry = {
    "time": str(now),
    "surpluses": {k: float(v) for k, v in surpluses.items()},
    "deficits": {k: float(v) for k, v in deficits.items()},
    "routing": routing_actions
    }



    try:
        with open("../decision_log.json") as f:
            log = json.load(f)
    except:
        log = []


    log.insert(0,log_entry)
    log = log[:20]

    with open("../decision_log.json","w") as f:
        json.dump(log,f,indent=4)


    time.sleep(5)
