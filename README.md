# geo-route-calculator
🌿 Orchard Routing & Distance Mapping Tool
A Python-based geospatial tool to calculate driving routes, distances, and durations between agricultural or field sites using the Google Maps API. Outputs include KML files for visualization in tools like Google Earth and CSV files for analysis and reporting.

📦 Features
Calculates driving directions between all pairs of locations
Extracts distances (in km) and travel durations (hh:mm)
Generates KML files for:
Individual location points
Driving routes between locations
Exports a CSV matrix of all distances and durations

🧰 Requirements
Python 3.9+

Google Maps API key with access to:
Directions API
Distance Matrix API

Required Pyhton packages:

pip install googlemaps pandas geopandas shapely lxml polyline
📂 Input
CSV file with the following columns:

Location	Latitude	Longitude
Site A	-27.123	153.456
Site B	-28.987	152.321
Site C ...
Site D ...

🚀 Usage
Add your coordinates CSV to the script path.

Place your API key in a plain .txt file:
path/to/api_key.txt

Run the script:
python generate_routes_and_distances.py

Output:
locations.kml – Point locations
routes.kml – Driving paths
distances_and_durations.csv – Distance + duration matrix

🔐 Privacy
This repository is private. All location data and API keys should be treated confidentially.

📌 Notes
Ensure your IP or host has access to the required Google Maps APIs.
Long-distance calculations may require quota management or batching.

📄 License
This project is intended for research and academic purposes. Licensing terms may be added as needed.
