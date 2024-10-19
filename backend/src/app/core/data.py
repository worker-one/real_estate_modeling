import math

import pandas as pd


data = pd.read_csv("./backend/data/prices.csv")

# Haversine formula to calculate the distance between two points on Earth
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in kilometers
    return distance


# Function to return all prices within a specified radius
def get_prices_within_radius(center_lat, center_lon, radius):
    prices_within_radius = []

    for _, entry in data.iterrows():
        distance = haversine(center_lat, center_lon, entry["latitude"], entry["longitude"])
        if distance <= radius:
            prices_within_radius.append(entry.to_dict())

    return prices_within_radius
