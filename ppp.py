from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from deep_translator import GoogleTranslator
from datetime import datetime
import os
import xml.etree.ElementTree as ET
import os
from collections import Counter
import re
import dateutil.parser
import statistics
import folium
from folium.plugins import MarkerCluster
from datetime import datetime, timedelta
import pandas as pd
import folium
from folium import IFrame
import json
from collections import defaultdict
import matplotlib.pyplot as plt

state_abbreviations = {
    'AK': 'Alaska', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 
    'CO': 'Colorado', 'HI': 'Hawaii', 'NC': 'North Carolina', 'NJ': 'New Jersey', 
    'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OK': 'Oklahoma', 
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'KS': 'Kansas', 'WA': 'Washington', 
    'WY': 'Wyoming', 'TX': 'Texas', 'TN': 'Tennessee'
} 

def extract_location_from_title1(title):
    """Extracts the city and place (state) from the title."""
    location_parts = title.split(' - ')
    
    if len(location_parts) > 1:
        # Split by ' of ' to focus on the city and place
        city_place_part = location_parts[-1].split(' of ')
        
        if len(city_place_part) == 2:
            # Now split by ', ' to get city and place (state)
            city_place = city_place_part[1].split(', ')
            
            if len(city_place) == 2:
                city = city_place[0].strip()  # City
                return city
    
    return None, None  # Return None for both if structure doesn't match

def parse_atom_file(file_path):

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def get_full_state_name(state_abbreviation):
    return state_abbreviations.get(state_abbreviation, state_abbreviation)

def get_event_data(entry, namespace):
    title = entry.find('atom:title', namespace).text
    link = entry.find('atom:link', namespace).get('href')
    published = entry.find('atom:updated', namespace).text
    coordinates = entry.find('ns0:point', namespace).text
    elev_text = entry.find('ns0:elev' ,namespace).text
    elev = 0.0  # Default value if elevation is missing or None
    if elev_text is not None:
            try:
                elev = float(elev_text)
            except ValueError:
                elev = 0.0  # Default value if conversion fails 
     # Extract title (assuming title contains the location)
     
    location_parts = title.split(' - ')
    if len(location_parts) > 1:
        city_place = location_parts[-1].split(', ')
        if len(city_place) == 2:
            city = city_place[0] 
            place = city_place[1]  
        else:
            city, place = '', ''  
    else:
        city, place = '', ''

    if place and place in state_abbreviations:
        place = get_full_state_name(place) 

    lat, lon = map(float, coordinates.split())    

    magnitude = None
    match = re.search(r'M\s*([\d.]+)', title)
    if match:
        magnitude = float(match.group(1))  

    # Extract age (optional) from the event entry
    age = None
    for category in entry.findall('atom:category', namespace):
        if category.get('label') == 'Age':
            age = category.get('term')
    

    published_date = published.split('T')[0]  # Getting the date part (YYYY-MM-DD)
    date_time = published.split('T')

# Step 2: Split the time part at the '+' to remove the timezone
    Published_time = date_time[1].split('+')[0]
    # Extract time, month, year, and other details
    timestamp = datetime.fromisoformat(published)
    time = timestamp.strftime('%H')  # Extract hour as a string
    month = timestamp.month
    year = timestamp.year
    date = timestamp.day
    date_obj = datetime.fromisoformat(published)
    formatted_date = date_obj.strftime('%Y-%m-%d')
    
    # Prepare the event data dictionary
    event_data = {
        'title': title,
        'link': link,
        'published': published,
        'lat' : lat,
        'lon':lon,
        'elevation': float(elev),  # Ensure elevation is a float
        'age': age,
        'magnitude': magnitude,
        'city': city,
        'place': place,
        'time': time,
        'month': month,
        'year': year,
        'timestamp': published ,
        'date':date,# Store the timestamp for time difference calculations
        'formatted_date': formatted_date,
        'Published_date': published_date,
        'Coordinates': coordinates,
        'Published_time' :Published_time
    }

    return event_data

def singleplaceatom(folder_path, start_date, end_date, place, json_filename):
    """Filters earthquake data by a user-specified date range and location, then saves to JSON."""

    namespace = {
        'atom': 'http://www.w3.org/2005/Atom',
        'georss': 'http://www.georss.org/georss',
        'ns0': 'http://www.georss.org/georss'
    }

    earthquake_data = []

    # Iterate through Atom files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".atom"):
            file_path = os.path.join(folder_path, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Iterate through all entries in the Atom file
            for entry in root.findall('atom:entry', namespace):
                event_data = get_event_data(entry, namespace)
                event_date = event_data['Published_date']
                event_place = event_data['place']
                event_time =event_data['Published_time']
                title=event_data['title']
                city_fr =extract_location_from_title1(title)
                eevent= event_data["elevation"]
                if not city_fr or not event_place:
                    continue

                # Filter entries by date range and location
                if event_place and event_place.lower() == place.lower() and start_date <= event_date <= end_date:
                    # Collect only magnitude and coordinates
                    
                    magnitude = event_data.get('magnitude')
                    if not magnitude:
                       continue 
                    lat = event_data['lat']
                    lon = event_data['lon']

                    # Add relevant data to the entries list
                    earthquake_data.append({
                        "place":place,
                        "time":event_time,
                        "date": event_date,
                        "latitude": lat,
                        "longitude": lon,
                        "magnitude": magnitude,
                        "city": city_fr,
                        "elevation":eevent
                    })

    # Save data to JSON file
    with open(json_filename, 'w') as json_file:
        json.dump(earthquake_data, json_file, indent=4)

    # Print confirmation message after writing
    print(f"Data has been written to '{json_filename}'.")
    return json_filename        

def parse_xml_folder(folder_path):
    """Parse all XML files in the specified folder."""
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)
            data.extend(get_weather_data(file_path))
    return data

def get_weather_data(file_path):
    """Extract weather data from a single XML file."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'ns': "http://www.w3.org/2005/Atom"}
    weather_data = []
    for entry in root.findall("ns:entry", namespace):
        time_text = entry.find("ns:time", namespace).text
        date = time_text.split("T")[0]  # Extract date (YYYY-MM-DD)

        location_text = entry.find("ns:location", namespace).text
        lat, lon = map(float, location_text.split())  # Extract lat, lon

        weather_element = entry.find("ns:weather", namespace)
        weather_info = {}
        if weather_element is not None:
            for child in weather_element:
                tag_name = child.tag.split("}")[-1]  # Remove namespace
                weather_info[tag_name] = float(child.text)
    

       

        weather_elem = entry.find("ns:weather", namespace)
        weather_info = {}
        if weather_elem is not None:
            for child in weather_elem:
                tag_name = child.tag.split("}")[-1]  # Remove namespace
                weather_info[tag_name] = float(child.text)

        weather_data.append({
            "date": date,
            "latitude": lat,
            "longitude": lon,
            "weather": {
                "weather_code": weather_info.get("weather_code", "N/A"),
                "temperature_max": weather_info.get("temperature_2m_max", "N/A"),
                "temperature_min": weather_info.get("temperature_2m_min", "N/A"),
                "temperature_mean": weather_info.get("temperature_2m_mean", "N/A"),
                "sunshine_hours": weather_info.get("sunshine_duration", "N/A"),
                "rain_sum": weather_info.get("rain_sum", "N/A"),
                "snowfall_sum": weather_info.get("snowfall_sum", "N/A"),
                "precipitation_hours": weather_info.get("precipitation_hours", "N/A"),
                "wind_speed_max": weather_info.get("wind_speed_10m_max", "N/A")
            }
        })
    
    return weather_data

def display_weather_by_date_range(folder_path, start_date, end_date, output_file):
    """Filter weather data by date range and save as JSON."""
    all_data = parse_xml_folder(folder_path)
    filtered_data = [entry for entry in all_data if start_date <= entry["date"] <= end_date]

    with open(output_file, "w") as json_file:
        json.dump(filtered_data, json_file, indent=4)

    print(f"Filtered data saved to {output_file}")
    return output_file

def merge_json_files(earthquake_file, weather_file, output_file):
    """Merge weather data into earthquake data based on matching date, latitude, and longitude."""
    
    # Load earthquake data
    with open(earthquake_file, "r") as eq_file:
        earthquake_data = json.load(eq_file)

    # Load weather data
    with open(weather_file, "r") as w_file:
        weather_data = json.load(w_file)

    # Create a lookup dictionary for weather data
    weather_lookup = {
        (entry["date"], float(entry["latitude"]), float(entry["longitude"])): entry["weather"]
        for entry in weather_data
    }

    # Merge matching weather data into earthquake data
    for entry in earthquake_data:
        key = (entry["date"], float(entry["latitude"]), float(entry["longitude"]))
        if key in weather_lookup:
            entry["weather"] = weather_lookup[key]  # Add weather data if found

    # Save merged data
    with open(output_file, "w") as out_file:
        json.dump(earthquake_data, out_file, indent=4)

    print(f"Merged data saved to: {output_file}")
    return output_file 


start_date_input = input("Enter the start date (YYYY-MM-DD): ")
end_date_input = input("Enter the end date (YYYY-MM-DD): ")
if start_date_input and end_date_input:
    user_place = input("Enter the place (e.g., California): ")
if user_place:        
    entries = singleplaceatom("user.atomfiles", start_date_input, end_date_input, user_place, "earthquake_data.json") 
if entries:
    bb = display_weather_by_date_range("weather_userdata", start_date_input, end_date_input, "weather_data.json")
if bb:
   cc = merge_json_files("earthquake_data.json", "weather_data.json", "merged_data.json")






















































































































































































































































































