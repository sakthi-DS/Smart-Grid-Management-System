import pandas as pd
import random
import math
from datetime import datetime, timedelta


rows = []

start_time = datetime(2024,1,1,0,0)

num_hours = 24 * 60  

for i in range(num_hours):

    current_time = start_time + timedelta(hours=i)

    hour = current_time.hour

    temperature = 25 + 8 * math.sin((hour-6)/24 * 2*math.pi)

    cloud_cover = random.randint(0,80)

    wind_speed = random.uniform(3,12)

    if 6 <= hour <= 18:

        solar_radiation = 900 * math.sin((hour-6)/12 * math.pi)

    else:

        solar_radiation = 0

    solar_radiation *= (1 - cloud_cover/100)

    solar = solar_radiation * 0.35

    wind = wind_speed ** 2 * 1.2

    if 18 <= hour <= 22:
        ev_load = random.randint(120,220)

    elif 7 <= hour <= 9:
        ev_load = random.randint(80,150)

    else:
        ev_load = random.randint(40,100)


    if 18 <= hour <= 23:

        house_demand = random.randint(300,450)

    elif 6 <= hour <= 9:

        house_demand = random.randint(250,350)

    else:

        house_demand = random.randint(150,280)


    rows.append({

        "time":current_time,
        "temperature":round(temperature,2),
        "cloud_cover":cloud_cover,
        "wind_speed":round(wind_speed,2),
        "solar_radiation":round(solar_radiation,2),

        "ev_load":ev_load,
        "house_demand":house_demand,

        "solar":round(solar,2),
        "wind":round(wind,2)

    })


df = pd.DataFrame(rows)

df.to_csv("data/grid_data.csv",index=False)

print("Dataset generated successfully!")
print("Rows:",len(df))