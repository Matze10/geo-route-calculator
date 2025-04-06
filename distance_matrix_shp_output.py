# -----------------------------------------
# Farm Route Mapping and Distance Calculator
# -----------------------------------------
# Description:
#   - Reads farm coordinates from a CSV
#   - Creates KML files for locations and driving routes
#   - Calculates pairwise driving distances and durations using Google Maps API
#   - Outputs results to KML and CSV files
# -----------------------------------------

import polyline
import googlemaps
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import math
import os

# --- FILE PATHS ---
# Update these paths before running the script
INPUT_CSV_PATH = "data/farms_coordinates.csv"
API_KEY_PATH = "secrets/google_api_key.txt"
LOCATIONS_KML_PATH = "output/locations.kml"
ROUTES_KML_PATH = "output/routes.kml"
DISTANCES_CSV_PATH = "output/distances_and_durations.csv"

# Load farm coordinates from CSV
df = pd.read_csv(INPUT_CSV_PATH)

# Load Google Maps API key from file
with open(API_KEY_PATH, 'r') as file:
    api_key = file.read().strip()

# Initialize Google Maps client
gmaps = googlemaps.Client(key=api_key)

# -----------------------------------------
# Create GeoDataFrame and KML for Locations
# -----------------------------------------

# Convert DataFrame to GeoDataFrame with Point geometries
geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
geo_df = gpd.GeoDataFrame(df, geometry=geometry)

# Initialize KML document and folder for locations
doc = KML.kml()
folder = KML.Folder(KML.name('Locations'))

# Add each location as a Placemark
for _, row in geo_df.iterrows():
    point = KML.Placemark(
        KML.name(row['Location']),  # Assumes 'Location' column in CSV
        KML.Point(
            KML.coordinates(f"{row.geometry.x},{row.geometry.y}")
        )
    )
    folder.append(point)
doc.append(folder)

# Write locations.kml to file
os.makedirs(os.path.dirname(LOCATIONS_KML_PATH), exist_ok=True)
with open(LOCATIONS_KML_PATH, 'w') as file:
    file.write(etree.tostring(doc, pretty_print=True).decode())
print("✅ KML Locations file created.")

# -----------------------------------------
# Calculate Driving Routes Between Locations
# -----------------------------------------

routes = []
distances_df = pd.DataFrame(index=df['Location'], columns=df['Location'])

# Loop through all unique pairs of locations
for i in range(len(df)):
    for j in range(i + 1, len(df)):
        start = (df.loc[i, 'Latitude'], df.loc[i, 'Longitude'])
        end = (df.loc[j, 'Latitude'], df.loc[j, 'Longitude'])

        # Request driving directions from Google Maps
        directions_result = gmaps.directions(start, end, mode="driving")
        polyline_encoded = directions_result[0]['overview_polyline']['points']
        decoded_route = polyline.decode(polyline_encoded)
        routes.append(decoded_route)

        # Get distance and duration
        distance_result = gmaps.distance_matrix(start, end, mode="driving")
        distance = distance_result['rows'][0]['elements'][0]['distance']['value']  # meters
        duration = distance_result['rows'][0]['elements'][0]['duration']['value']  # seconds

        # Convert to km and hh:mm format
        distance_km = distance / 1000
        hours = math.floor(duration / 3600)
        minutes = math.floor((duration % 3600) / 60)
        duration_formatted = f"{hours:02d}:{minutes:02d}"

        # Save distance & duration symmetrically
        loc_i = df.loc[i, 'Location']
        loc_j = df.loc[j, 'Location']
        distances_df.loc[loc_i, loc_j] = f"{distance_km:.2f} km, {duration_formatted}"
        distances_df.loc[loc_j, loc_i] = f"{distance_km:.2f} km, {duration_formatted}"

print("✅ All distances and durations calculated.")

# -----------------------------------------
# Save KML Routes File
# -----------------------------------------

# Create GeoDataFrame for routes
geometry = [LineString(route) for route in routes]
routes_df = gpd.GeoDataFrame(geometry=geometry)

# Create KML document for routes
doc_routes = KML.kml()
folder_routes = KML.Folder(KML.name('Routes'))

# Add each route as a LineString Placemark
for _, row in routes_df.iterrows():
    linestring = KML.Placemark(
        KML.LineString(
            KML.coordinates(' '.join(f"{coord[1]},{coord[0]}" for coord in row.geometry.coords))
        )
    )
    folder_routes.append(linestring)
doc_routes.append(folder_routes)

# Write routes.kml to file
with open(ROUTES_KML_PATH, 'w') as file:
    file.write(etree.tostring(doc_routes, pretty_print=True).decode())
print("✅ KML Routes file created.")

# -----------------------------------------
# Export Distance Matrix to CSV
# -----------------------------------------

distances_df.to_csv(DISTANCES_CSV_PATH)
print(f"✅ Distances and durations CSV saved at:\n   {DISTANCES_CSV_PATH}")
