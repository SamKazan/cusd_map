import streamlit as st
from streamlit_folium import st_folium
import folium
import geojson
from geopy.geocoders import Nominatim
from shapely.geometry import Point, Polygon

# Set the Streamlit page configuration
st.set_page_config(page_title="School Boundary Map", layout="wide")

# Title of the app
st.title("Arizona School Boundary Map")

# Load the GeoJSON file (school boundary)
with open('rectangle_boundary.geojson', 'r') as file:
    boundary_geojson = geojson.load(file)

# Load the GeoJSON file for schools (with names)
with open('schools.geojson', 'r') as file:
    schools_geojson = geojson.load(file)

# Extract the polygon coordinates from the GeoJSON
polygon_coords = boundary_geojson['features'][0]['geometry']['coordinates'][0]
polygon = Polygon(polygon_coords)  # Create a Shapely polygon from the coordinates

# Initialize the map, centered on Chandler, AZ
m = folium.Map(location=[33.3062, -111.8413], zoom_start=11)

# Add the boundary GeoJSON layer to the map
folium.GeoJson(boundary_geojson, name="School Boundary").add_to(m)

# Dictionary of school addresses and corresponding logo URLs
school_logos = {
    "1625 E. Frye Rd., Chandler, AZ": "https://www.cusd80.com/cms/lib/AZ01001175/Centricity/Template/GlobalAssets/images//School-logos-header/Bologna-Elementary.png",
    "5990 S. Val Vista Drive, Chandler, AZ 85249": "https://example.com/logo2.png",
    "1205 E. Frye Rd, Chandler, AZ": "https://example.com/logo3.png",
    "24901 S. Power Rd. Queen Creek, AZ 85142": "https://example.com/logo4.png",
    # Add other schools with corresponding logo URLs here
}

# Add each school with a custom icon (logo) and display the name on click
for feature in schools_geojson['features']:
    lon, lat = feature['geometry']['coordinates']
    address = feature['properties'].get("address", "School")
    name = feature['properties'].get("name", "Unnamed School")  # Get school name
    logo_url = school_logos.get(address)  # Get logo URL for the school

    if logo_url:
        # Add a marker with a custom icon using the logo URL
        icon = folium.CustomIcon(logo_url, icon_size=(50, 50))  # Adjust icon size as needed
        folium.Marker(
            [lat, lon],
            popup=f"<b>{name}</b><br>{address}",  # Show name and address in popup
            icon=icon
        ).add_to(m)
    else:
        # Default marker if logo is unavailable
        folium.Marker(
            [lat, lon],
            popup=f"<b>{name}</b><br>{address}",  # Show name and address in popup
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

# Function to check if the address is inside the boundary (polygon)
def is_within_boundary(lat, lon):
    point = Point(lon, lat)  # Create a point object using the address coordinates
    return polygon.contains(point)  # Check if the point is inside the polygon

# Function to extract coordinates from an address
def get_coordinates(address):
    geolocator = Nominatim(user_agent="school_boundary_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None

# Streamlit interface for address input
address = st.text_input("Enter your address:")

if address:
    coords = get_coordinates(address)
    if coords:
        lat, lon = coords
        # Check if the address is within the boundary
        if is_within_boundary(lat, lon):
            st.success(f"{address} is within the school boundary!")
            folium.Marker(
                [lat, lon],
                popup=address,
                icon=folium.Icon(color='green')
            ).add_to(m)
        else:
            st.warning(f"{address} is outside the school boundary.")
            folium.Marker(
                [lat, lon],
                popup=address,
                icon=folium.Icon(color='red')
            ).add_to(m)
    else:
        st.error("Address not found. Please try again.")

# Display the map in Streamlit
st_folium(m, width=700, height=500)
