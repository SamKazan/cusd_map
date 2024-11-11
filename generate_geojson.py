import geojson
from geopy.geocoders import Nominatim
import time

# Initialize geocoder
geolocator = Nominatim(user_agent="school_boundary_app")

# Function to extract coordinates from address
def get_coordinates(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.longitude, location.latitude)
        else:
            print(f"Address not found: {address}")
            return None
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None

# List of addresses with their corresponding school names
school_data = [
    {"name": "Bologna Elementary", "address": "1625 E. Frye Rd., Chandler, AZ"},
    {"name": "School 2", "address": "5990 S. Val Vista Drive, Chandler, AZ 85249"},
    {"name": "School 3", "address": "1205 E. Frye Rd, Chandler, AZ"},
    {"name": "School 4", "address": "24901 S. Power Rd. Queen Creek, AZ 85142"},
    {"name": "School 5", "address": "2626 E. Pecos Road, Chandler, AZ 85225"},
    {"name": "School 6", "address": "3700 S. Arizona Avenue, Chandler, AZ 85248"},
    {"name": "School 7", "address": "290 S. Cooper Road, Chandler, AZ 85225"},
    {"name": "School 8", "address": "1919 E. Queen Creek, Gilbert, AZ 85297"}
]

# Initialize min/max values to store bounding box
min_lat = float('inf')
max_lat = float('-inf')
min_lon = float('inf')
max_lon = float('-inf')

# Prepare features for schools and update bounding box coordinates
school_features = []
for school in school_data:
    coordinates = get_coordinates(school["address"])
    if coordinates:
        lon, lat = coordinates
        # Update bounding box coordinates
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lon = min(min_lon, lon)
        max_lon = max(max_lon, lon)
        
        # Create a GeoJSON feature for each school with name and address
        school_feature = geojson.Feature(
            geometry=geojson.Point((lon, lat)),
            properties={"name": school["name"], "address": school["address"]}
        )
        school_features.append(school_feature)
    
    # Respect Nominatim's rate limit
    time.sleep(1)

# Save schools data as `schools_with_names.geojson`
schools_feature_collection = geojson.FeatureCollection(school_features)
with open('schools.geojson', 'w') as file:
    geojson.dump(schools_feature_collection, file, indent=2)

# Define the coordinates of the rectangle (bounding box)
bottom_left = [min_lon, min_lat]
top_right = [max_lon, max_lat]
top_left = [min_lon, max_lat]
bottom_right = [max_lon, min_lat]

# Define the rectangle as a polygon (a list of coordinates for the 4 corners)
rectangle_coordinates = [bottom_left, top_left, top_right, bottom_right, bottom_left]

# Create the GeoJSON feature for the rectangle boundary
boundary_feature = geojson.Feature(
    geometry=geojson.Polygon([rectangle_coordinates]),
    properties={"name": "School Boundary"}
)

# Create the GeoJSON FeatureCollection for the rectangle boundary
boundary_feature_collection = geojson.FeatureCollection([boundary_feature])

# Save to `rectangle_boundary.geojson`
with open('rectangle_boundary.geojson', 'w') as file:
    geojson.dump(boundary_feature_collection, file, indent=2)

print("GeoJSON files created: rectangle_boundary.geojson and schools_with_names.geojson")
