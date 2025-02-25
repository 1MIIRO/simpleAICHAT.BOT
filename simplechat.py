from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from deep_translator import GoogleTranslator
from googletrans import Translator as GoogleTranslatorV2
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
from retry_requests import retry
import pandas as pd
import folium
from folium import IFrame

# Load pre-trained DialoGPT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Set the model to evaluation mode
model.eval()

# Memory to keep track of previous inputs and responses (this will be hidden from the user)
conversation_history = []

# Expanded predefined responses for various greetings in multiple languages
predefined_responses = {
    # English Greetings and Responses
    "hello": "Hello there! How can I help you today?",
    "hi": "Hi! How's it going?",
    "hey": "Hey! How are you?",
    "howdy": "Howdy! What's up?",
    "greetings": "Greetings! How can I assist you?",
    "what's up": "Not much, just here to chat! How about you?",
    "what's new": "Not much, just here to chat! What's new with you?",
    "how are you": "I'm doing great, thank you for asking! How are you?",
    "how's it going": "Everything's good! How about you?",
    "good evening": "Good evening! How's your day been?",
    "what's your name": "I am an AI created to chat with you! My name is BIBA.",
    "how are you doing": "I'm doing fantastic! Thanks for asking!",
    "good morning": "Good morning! How can I help you today?",
    "good afternoon": "Good afternoon! How can I assist you?",
    "bye": "Goodbye! Have a great day!",
    "goodbye": "Goodbye! Take care!",
    "how is the weather": "I can't check the weather, but I hope it's nice outside!",

    # French Greetings
    "bonjour": "Bonjour! Comment puis-je vous aider aujourd'hui?",  # Hello! How can I help you today?
    "salut": "Salut! Comment ça va?",  # Hi! How's it going?
    "coucou": "Coucou! Comment ça va?",  # Hey! How are you?
    "bonsoir": "Bonsoir! Comment a été ta journée?",  # Good evening! How was your day?
    "bonne nuit": "Bonne nuit! Passez une bonne soirée!",  # Good night! Have a great evening!
    "comment ça va": "Ça va bien, merci de demander! Et toi?",  # I'm doing well, thanks for asking! And you?
    "quels sont les nouvelles": "Pas grand-chose, juste là pour discuter! Et toi, qu'est-ce qui est nouveau?",  # Not much, just here to chat! What's new with you?
    "quel est ton nom": "Je suis une IA créée pour discuter avec vous ! Mon nom est BIBA.",  # I am an AI created to chat with you! My name is BIBA.

    # Spanish Greetings
    "hola": "¡Hola! ¿Cómo puedo ayudarte hoy?",  # Hello! How can I help you today?
    "buenos días": "¡Buenos días! ¿Cómo puedo ayudarte?",  # Good morning! How can I help you?
    "buenas tardes": "¡Buenas tardes! ¿Cómo te va?",  # Good afternoon! How's it going?
    "buenas noches": "¡Buenas noches! ¿Cómo estuvo tu día?",  # Good evening! How was your day?
    "qué tal": "¡Todo bien! ¿Y tú?",  # All good! And you?
    "cómo estás": "¡Estoy genial! Gracias por preguntar, ¿y tú?",  # I'm great! Thanks for asking, and you?
    "qué hay de nuevo": "Nada mucho, solo aquí para charlar. ¿Y tú?",  # Not much, just here to chat. And you?
    "¿cómo te llamas": "¡Soy una IA creada para charlar contigo! Mi nombre es BIBA.",  # I am an AI created to chat with you! My name is BIBA.

    # Swahili Greetings
    "habari": "Habari! Niko hapa kusaidia. Habari yako?",  # Hello! I'm here to help. How are you?
    "hujambo": "Hujambo! Vipi?",  # Hello! How are you?
    "salama": "Salama! Habari za leo?",  # Peace! How's your day going?
    "jambo": "Jambo! Vipi leo?",  # Hello! How's it today?
    "mambo": "Mambo! Habari za asubuhi?",  # What's up! How's the morning
    "habari gani": "Nzuri, asante kwa kuuliza! Na wewe?",  # I'm good, thanks for asking! And you?
    "vipi": "Niko vizuri! Na wewe vipi?",  # I'm good! How about you?
    "jina lako nani": "Mimi ni AI iliyoumbwa kuzungumza nawe! Jina langu ni BIBA.",  # I am an AI created to chat with you! My name is BIBA.
}

search_triggers = [
    # English
    "search location details",  
    "find events in",  
    "look up location",  
    "check for events in", 
    "search for earthquakes in",  
    "any events in",  
    
    # French
    "rechercher les détails du lieu",  # Search for location details
    "trouver des événements à",  # Find events happening in a location
    "consulter l'emplacement",  # Look up information about a place
    "vérifier les événements à",  # Check for recorded events in a place
    "rechercher des tremblements de terre à",  # Search for earthquakes in a specific location
    "y a-t-il des événements à",  # Check if any events occurred in a place
    
    # Spanish
    "buscar detalles de la ubicación",  # Search for location details
    "encontrar eventos en",  # Find events happening in a location
    "consultar la ubicación",  # Look up information about a place
    "verificar eventos en",  # Check for recorded events in a place
    "buscar terremotos en",  # Search for earthquakes in a specific location
    "hay eventos en",  # Check if any events occurred in a place
    
    # Swahili
    "tafuta maelezo ya eneo",  # Search for location details
    "pata matukio katika",  # Find events happening in a location
    "angalia eneo",  # Look up information about a place
    "angalia matukio katika",  # Check for recorded events in a place
    "tafuta matetemeko ya ardhi katika",  # Search for earthquakes in a specific location
    "kuna matukio katika"  # Check if any events occurred in a place
]

state_abbreviations = {
    'AK': 'Alaska', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 
    'CO': 'Colorado', 'HI': 'Hawaii', 'NC': 'North Carolina', 'NJ': 'New Jersey', 
    'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OK': 'Oklahoma', 
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'KS': 'Kansas', 'WA': 'Washington', 
    'WY': 'Wyoming', 'TX': 'Texas', 'TN': 'Tennessee'
} 

def extract_location_from_title(title):
    """Extracts the city and place from the title."""
    location_parts = title.split(' - ')
    
    if len(location_parts) > 1:
        # Split by ' of ' to focus on the city and place
        city_place_part = location_parts[-1].split(' of ')
        
        if len(city_place_part) == 2:
            # Now split by ', ' to get city and place
            city_place = city_place_part[1].split(', ')
            if len(city_place) == 2:
                city = city_place[0].strip()  # City
                place = city_place[1].strip()  # Place (State)
                return f"{city} {place}"
    
    return None

def extract_all_locations(folder_path):
    """Extracts unique locations (places) from all .atom files in the folder."""
    global unique_locations
    unique_locations = set()
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss', 'ns0':"http://www.georss.org/georss"}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.atom'):
            file_path = os.path.join(folder_path, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                for entry in root.findall('atom:entry', namespace):
                    title = entry.find('atom:title', namespace).text
                    location = extract_location_from_title(title)
                    if location:
                        unique_locations.add(location)

            except ET.ParseError:
                print(f"Error parsing file: {file_path}")

def show_locations():
    """Displays extracted locations."""
    if unique_locations:
        return "\n".join(sorted(unique_locations))
    else:
        return "No locations found in dataset."

# Function to search for event data in .atom files
def parse_atom_file(file_path):

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

# Function to parse date
def parse_date(date_str):
    try:
        return dateutil.parser.parse(date_str).date()
    except ValueError:
        return None

# Function to parse time
def parse_time(time_str):
    try:
        return dateutil.parser.parse(time_str).time()
    except ValueError:
        return None

def search_seismic_activity(folder_path, date_range_start, date_range_end, time_range_start, time_range_end):
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss', 'ns0' : 'http://www.georss.org/georss'}
    matching_entries = []
    result_file_path = 'displayfiles//display_search_results.txt'

    with open(result_file_path, 'w', encoding='utf-8') as result_file:
        for filename in os.listdir(folder_path):
            if filename.endswith('.atom'):
                file_path = os.path.join(folder_path, filename)
                root = parse_atom_file(file_path)

                if root is not None:
                    for entry in root.findall('atom:entry', namespace):
                        updated = entry.find('atom:updated', namespace).text

                        title_elem = entry.find('atom:title', namespace)
                        title = title_elem.text if title_elem is not None else "Unknown"

                        coordinates_elem = entry.find('georss:point', namespace)
                        coordinates = coordinates_elem.text if coordinates_elem is not None else "Unknown"

                        elevation_elem = entry.find('georss:elev', namespace)
                        elevation = elevation_elem.text if elevation_elem is not None else "Unknown"

                        age = "N/A"
                        magnitude = "N/A"

                        for category in entry.findall('atom:category', namespace):
                            if category.get('label') == 'Age':
                                age = category.get('term')
                            if category.get('label') == 'Magnitude':
                                magnitude = category.get('term')

                        entry_date = updated.split('T')[0]
                        entry_time = updated.split('T')[1].split('Z')[0]

                        entry_datetime = parse_date(entry_date)
                        if date_range_start and date_range_end:
                            if not (date_range_start <= entry_datetime <= date_range_end):
                                continue

                        entry_time_obj = parse_time(entry_time)
                        if time_range_start and time_range_end:
                            if not (time_range_start <= entry_time_obj <= time_range_end):
                                continue

                        matching_entries.append({
                            'title': title,
                            'published': updated,
                            'coordinates': coordinates,
                            'elevation': elevation,
                            'age': age,
                            'magnitude': magnitude
                        })

        if matching_entries:
            for entry in matching_entries:
                result_file.write(f"Title: {entry['title']}\n")
                result_file.write(f"Published: {entry['published']}\n")
                result_file.write(f"Coordinates: {entry['coordinates']}\n")
                result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                result_file.write(f"Occurred: {entry['age']}\n")
                result_file.write(f"Magnitude: {entry['magnitude']}\n")
                result_file.write("-" * 120 + "\n")

    return result_file_path, len(matching_entries)

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
     
    location = extract_location_from_title(title) 
    if location:
        # The extract_location_from_title should return the city and place in the correct format
        city_place = location.split(' ')  # Split by space since both city and place are expected to be in the same string
        
        # If there are two parts (city and place), assign them accordingly
        if len(city_place) == 2:
            city, place = city_place[0], city_place[1]
        else:
            city, place = '', city_place[0]  # If only the place is found, set it as place
        
    if place and place.upper() in state_abbreviations:
        place = state_abbreviations[place.upper()]  # If place is a state abbreviation, expand it to full name

    # If there's no city, return only the place (could be a state or a known place)
    if not city:
        city = place 


    magnitude = None
    match = re.search(r'M\s*([\d.]+)', title)
    if match:
        magnitude = float(match.group(1))  

    # Extract age (optional) from the event entry
    age = None
    for category in entry.findall('atom:category', namespace):
        if category.get('label') == 'Age':
            age = category.get('term')

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
        'coordinates': coordinates,
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
        'formatted_date': formatted_date
    }

    return event_data

def get_weather_data(entry, namespace):
    location = entry.find('{http://www.w3.org/2005/Atom}location').text
    lat, lon = map(float, location.split()) 
    time_text = entry.find('{http://www.w3.org/2005/Atom}time').text
    timestamp = datetime.fromisoformat(time_text[:-6])  
    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S') 
    formatted_date = timestamp.strftime('%Y-%m-%d')
    weather_element = entry.find('{http://www.w3.org/2005/Atom}weather')
    
    weather_code = float(weather_element.find('{http://www.w3.org/2005/Atom}weather_code').text)
    temperature_max = float(weather_element.find('{http://www.w3.org/2005/Atom}temperature_2m_max').text)
    temperature_min = float(weather_element.find('{http://www.w3.org/2005/Atom}temperature_2m_min').text)
    temperature_mean = float(weather_element.find('{http://www.w3.org/2005/Atom}temperature_2m_mean').text)
    sunshine_duration = float(weather_element.find('{http://www.w3.org/2005/Atom}sunshine_duration').text)
    rain_sum = float(weather_element.find('{http://www.w3.org/2005/Atom}rain_sum').text)
    snowfall_sum = float(weather_element.find('{http://www.w3.org/2005/Atom}snowfall_sum').text)
    precipitation_hours = float(weather_element.find('{http://www.w3.org/2005/Atom}precipitation_hours').text)
    wind_speed_max = float(weather_element.find('{http://www.w3.org/2005/Atom}wind_speed_10m_max').text)
    
    weather_data = {
        'location': (lat, lon), 
        'time': formatted_time, 
        'formatted_date': formatted_date, 
        'weather_code': weather_code,
        'temperature_max': temperature_max,
        'temperature_min': temperature_min,
        'temperature_mean': temperature_mean,
        'sunshine_duration': sunshine_duration,
        'rain_sum': rain_sum,
        'snowfall_sum': snowfall_sum,
        'precipitation_hours': precipitation_hours,
        'wind_speed_max': wind_speed_max,
    }

    return weather_data

def get_entries_from_files(folder_path, start_date, end_date):
    entries = []
    
    # Loop through all XML files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(folder_path, filename)
            
            # Parse the XML file
            root = parse_atom_file(file_path)
            if root is not None:
                # Find all the entries in the file
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    weather_data = get_weather_data(entry, '{http://www.w3.org/2005/Atom}')
                    entry_date_str = weather_data['formatted_date']
                    
                    # Convert the entry date string to a datetime object
                    try:
                        entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d")  # Assuming the date is in YYYY-MM-DD format
                    except ValueError:
                        continue  # If the date format is invalid, skip this entry
                    
                    # Check if the entry's date is within the specified range
                    if start_date <= entry_date <= end_date:
                        entries.append(weather_data)

    return entries

# Function to generate a weather icon URL based on the weather code
def get_weather_icon_url(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

# Function to create a popup HTML table for weather data
def get_weather_icon_url(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

# Function to display entries on the map with popup
def display_entries_on_map(entries):
    # Create a folium map centered at an approximate global location
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Loop through the entries and add markers to the map
    for entry in entries:
        lat, lon = entry['location']  # Extract latitude and longitude from entry
        
        # Extract weather data for popup content
        rain_sum = entry['rain_sum']
        wind_speed = entry['wind_speed_max']
        sunshine_duration = entry['sunshine_duration']
        snowfall_sum = entry['snowfall_sum']
        temp_max = entry['temperature_max']
        temp_min = entry['temperature_min']
        temp_mean = entry['temperature_mean']
        icon_code = entry['weather_code']
        time = entry['time']
        
        # Get the weather icon URL based on the weather code
        weather_icon_url = get_weather_icon_url(icon_code)

        # Create the HTML content for the popup with weather icons included
        popup_content = f"""
        <table border="1" cellpadding="5" cellspacing="0">
            <tr><td colspan="2"><strong>Weather Data</strong></td></tr>
            <tr><td>Weather Icon</td><td><img src="{weather_icon_url}" alt="Weather Icon" width="40" height="40"></td></tr>
            <tr><td>Rainfall Sum</td><td>{rain_sum} mm</td></tr>
            <tr><td>Rain Icon</td><td><img src="{get_weather_icon_url('10d')}" alt="Rain" width="40" height="40"></td></tr>
            <tr><td>Wind Speed</td><td>{wind_speed} km/h</td></tr>
            <tr><td>Wind Icon</td><td><img src="{get_weather_icon_url('50d')}" alt="Wind" width="40" height="40"></td></tr>
            <tr><td>Snowfall</td><td>{snowfall_sum} mm</td></tr>
            <tr><td>Snow Icon</td><td><img src="{get_weather_icon_url('13d')}" alt="Snow" width="40" height="40"></td></tr>
            <tr><td>Sunshine Duration</td><td>{sunshine_duration} hours</td></tr>
            <tr><td>Sunshine Icon</td><td><img src="https://img.icons8.com/ios-filled/50/000000/sun.png" alt="Sunshine" width="40" height="40"></td></tr>
            <tr><td>Max Temperature</td><td>{temp_max}°C</td></tr>
            <tr><td>Min Temperature</td><td>{temp_min}°C</td></tr>
            <tr><td>Avg Temperature</td><td>{temp_mean}°C</td></tr>
            <tr><td>Temperature Icon</td><td><img src="https://img.icons8.com/ios-filled/50/000000/temperature.png" alt="Temperature" width="40" height="40"></td></tr>
            <tr><td>Time</td><td>{time}</td></tr>
        </table>
        """

        # Create the marker and add it to the map with the popup content
        folium.Marker(
            location=[lat, lon],  # Marker at latitude and longitude
            popup=folium.Popup(popup_content, max_width=300),  # Popup with weather data table
            icon=folium.Icon(color='blue')  # Blue marker icon
        ).add_to(m)

    # Save the map to an HTML file
    m.save("weather_map_with_icons.html")
    return m

def calculate_statistics(folder_path ):
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss' , 'ns0':"http://www.georss.org/georss"}
    entries = []
    places = []
    times = []
    months = []
    years = []
    elevations = []
    magnitudes = []
    timestamps = []  # Store timestamps to calculate time differences

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.atom'):
            file_path = os.path.join(folder_path, filename)
            root = parse_atom_file(file_path)
            
            # Loop through the entries and get the data from get_event_data
            for entry in root.findall('atom:entry', namespace):
                event_data = get_event_data(entry, namespace)

                # Append the relevant data
                entries.append(event_data['title'])
                places.append(event_data['place'])
                times.append(event_data['time'])
                months.append(event_data['month'])
                years.append(event_data['year'])
                elevations.append(event_data['elevation'])
                magnitudes.append(event_data['magnitude'])
                timestamps.append(event_data['timestamp'])

    total_entries = len(entries)

    # Most and least frequent places
    place_counts = Counter(places)
    most_frequent_place = place_counts.most_common(1)[0][0]
    least_frequent_place = place_counts.most_common()[-1][0]

    # Average time (HH)
    total_hours = sum(int(time) for time in times)
    average_time = total_hours / total_entries if total_entries else 0

    # Most frequent month and year
    month_counts = Counter(months)
    most_frequent_month = month_counts.most_common(1)[0][0]

    year_counts = Counter(years)
    most_frequent_year = year_counts.most_common(1)[0][0]

    # Percentage of entries before and after noon
    before_noon = sum(1 for time in times if 1 <= int(time) <= 12)
    after_noon = total_entries - before_noon
    percentage_before_noon = (before_noon / total_entries) * 100 if total_entries else 0
    percentage_after_noon = (after_noon / total_entries) * 100 if total_entries else 0

    # Highest and lowest elevation
    highest_elevation_index = elevations.index(max(elevations))
    lowest_elevation_index = elevations.index(min(elevations))
    highest_elevation_title = entries[highest_elevation_index]
    lowest_elevation_title = entries[lowest_elevation_index]

    # Percentage of negative and positive elevations
    negative_elevations = sum(1 for elev in elevations if elev < 0)
    positive_elevations = total_entries - negative_elevations
    percentage_negative_elevations = (negative_elevations / total_entries) * 100 if total_entries else 0
    percentage_positive_elevations = (positive_elevations / total_entries) * 100 if total_entries else 0
    
    magnitudes = [m for m in magnitudes if m is not None]

    # Average magnitude
    average_magnitude = sum(magnitudes) / total_entries if total_entries and magnitudes else 0

    # Median Magnitude
    median_magnitude = statistics.median(magnitudes) if magnitudes else 0

    # Standard Deviation of Magnitudes
    stdev_magnitude = statistics.stdev(magnitudes) if len(magnitudes) > 1 else 0

    # Median Elevation
    median_elevation = statistics.median(elevations) if elevations else 0

    # Standard Deviation of Elevations
    stdev_elevation = statistics.stdev(elevations) if len(elevations) > 1 else 0

    # Longest Time Between Earthquakes
    timestamp_diffs = []
    for i in range(1, len(timestamps)):
        time_diff = (datetime.fromisoformat(timestamps[i]) - datetime.fromisoformat(timestamps[i-1])).total_seconds() / 3600
        timestamp_diffs.append(time_diff)
    longest_time_between = max(timestamp_diffs) if timestamp_diffs else 0
    shortest_time_between = min(timestamp_diffs) if timestamp_diffs else 0
    average_time_between = sum(timestamp_diffs) / len(timestamp_diffs) if timestamp_diffs else 0
    


    # Total Magnitude of All Earthquakes
    total_magnitude = sum(magnitudes)

    # Number of Earthquakes with Magnitude >= 5
    num_magnitudes_ge5 = sum(1 for mag in magnitudes if mag >= 5)

    # Number of Earthquakes with Magnitude < 3
    num_magnitudes_lt3 = sum(1 for mag in magnitudes if mag < 3)

    # Total Elevation Above Sea Level
    total_positive_elevation = sum(elev for elev in elevations if elev > 0)

    # Total Elevation Below Sea Level
    total_negative_elevation = sum(elev for elev in elevations if elev < 0)

    # Percentage of Earthquakes with Magnitude >= 6
    percentage_ge6_magnitude = (sum(1 for mag in magnitudes if mag >= 6) / total_entries) * 100 if total_entries else 0

    earthquake_by_week = Counter([datetime.fromisoformat(timestamp).strftime('%Y-%U') for timestamp in timestamps])  # Week number
    earthquake_by_month = Counter([datetime.fromisoformat(timestamp).strftime('%Y-%m') for timestamp in timestamps])
    earthquake_by_year = Counter([datetime.fromisoformat(timestamp).strftime('%Y') for timestamp in timestamps])

    # Write the statistics to a text file
    with open("displayfiles//user_view_screen.txt", "w", encoding="utf-8") as file:
        file.write("===============================================================\n")
        file.write("Earthquake statistics report\n")
        file.write("===============================================================\n")
        file.write(f"Total number of earthquakes\n{total_entries}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Place that experienced the most earthquakes\n{most_frequent_place}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Place that experienced the least earthquakes\n{least_frequent_place}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Average time the earthquakes were recorded\n{average_time} hours\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"The Month that is recorded the most earthquakes\n{most_frequent_month}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"The YEAR that is recorded the most earthquakes\n{most_frequent_year}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Percentage of the earthquakes that took place before noon\n{percentage_before_noon}%\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Percentage of the earthquakes that took place after noon\n{percentage_after_noon}%\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Location of earthquake recorded with the highest altitude\n{highest_elevation_title}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Percentage of the earthquakes that took place below sea level\n{percentage_negative_elevations}%\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Percentage of earthquakes that took place above sea level\n{percentage_positive_elevations}%\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Location of earthquake recorded with the lowest altitude\n{lowest_elevation_title}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Average magnitude of the earthquakes experienced\n{average_magnitude}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Median Magnitude\n{median_magnitude}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Standard Deviation of Magnitudes\n{stdev_magnitude}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Median Elevation\n{median_elevation}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Standard Deviation of Elevations\n{stdev_elevation}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Longest time between earthquakes\n{longest_time_between} hours\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Shortest time between earthquakes\n{shortest_time_between} hours\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Average duration between earthquakes\n{average_time_between} hours\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Total Magnitude of All Earthquakes\n{total_magnitude}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Number of Earthquakes with Magnitude >= 5\n{num_magnitudes_ge5}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Number of Earthquakes with Magnitude < 3\n{num_magnitudes_lt3}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Total Elevation Above Sea Level\n{total_positive_elevation} meters\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Total Elevation Below Sea Level\n{total_negative_elevation} meters\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Percentage of Earthquakes with Magnitude >= 6\n{percentage_ge6_magnitude}%\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Frequency by Week\n{dict(earthquake_by_week)}\n")
        file.write(f"Frequency by Month\n{dict(earthquake_by_month)}\n")
        file.write(f"Frequency by Year\n{dict(earthquake_by_year)}\n")
        file.write("----------------------------------------------------------------\n")
  
# Function to check magnitude
def check_magnitude(magnitude, search_type):
    try:
        if search_type.startswith('='):
            return magnitude == float(search_type[1:])
        elif search_type.startswith('<'):
            if search_type.startswith('<='):
                return magnitude <= float(search_type[2:])
            return magnitude < float(search_type[1:])
        elif search_type.startswith('>'):
            if search_type.startswith('>='):
                return magnitude >= float(search_type[2:])
            return magnitude > float(search_type[1:])
        else:
            return magnitude == float(search_type)
    except ValueError:
        return False

def search_magnitude(folder_path, search_type):
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss', 'ns0' : 'http://www.georss.org/georss'}
    matching_entries = []
    result_file_path = 'displayfiles//display_search_results.txt'

    with open(result_file_path, 'w', encoding='utf-8') as result_file:
        for filename in os.listdir(folder_path):
            if filename.endswith('.atom'):
                file_path = os.path.join(folder_path, filename)
                root = parse_atom_file(file_path)

                if root is not None:
                    for entry in root.findall('atom:entry', namespace):
                        event_data = get_event_data(entry, namespace)
                        if event_data['magnitude'] is not None and check_magnitude(event_data['magnitude'], search_type):
                            matching_entries.append(event_data)

                    if matching_entries:
                        for entry in matching_entries:
                            result_file.write(f"Title: {entry['title']}\n")
                            result_file.write(f"Published: {entry['published']}\n")
                            result_file.write(f"Coordinates: {entry['coordinates']}\n")
                            result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                            result_file.write(f"Occurred: {entry['age']}\n")
                            result_file.write(f"Magnitude: {entry['magnitude']}\n")
                            result_file.write("-" * 120 + "\n")

    return result_file_path, len(matching_entries)    

def search_atom_files(folder_path, search_place):
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss', 'ns0' : 'http://www.georss.org/georss'}
    matching_entries = []
    result_file_path = 'displayfiles/display_search_results.txt'

    with open(result_file_path, 'w', encoding='utf-8') as result_file:
        for filename in os.listdir(folder_path):
            if filename.endswith('.atom'):
                file_path = os.path.join(folder_path, filename)
                root = parse_atom_file(file_path)

                if root is not None:
                    for entry in root.findall('atom:entry', namespace):
                        event_data = get_event_data(entry, namespace)
                        if search_place.lower() == event_data.get('place', '').lower():
                            matching_entries.append(event_data)

                    if matching_entries:
                        for entry in matching_entries:
                            result_file.write(f"Title: {entry['title']}\n")
                            result_file.write(f"Published: {entry['published']}\n")
                            result_file.write(f"Coordinates: {entry['coordinates']}\n")
                            result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                            result_file.write(f"Occurred: {entry['age']}\n")
                            result_file.write(f"Magnitude: {entry['magnitude']}\n")
                            result_file.write("-" * 120 + "\n")

    # Ensure the function always returns a tuple
    return result_file_path, len(matching_entries)

def parse_atom_files_by_place_and_date(folder_path, start_date, end_date, place):
    entries = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".atom"):
            file_path = os.path.join(folder_path, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title = entry.find("{http://www.w3.org/2005/Atom}title").text
                updated = entry.find("{http://www.w3.org/2005/Atom}updated").text
                point = entry.find("{http://www.georss.org/georss}point").text if entry.find("{http://www.georss.org/georss}point") is not None else None
                
                if title and updated and point:
                    title_parts = title.split()
                    location_in_title = title_parts[-1]  
                
                    if location_in_title.lower() == place.lower():
                        date = datetime.strptime(updated.split('T')[0], '%Y-%m-%d')
                        if start_date <= date <= end_date:
                            magnitude = None
                            match = re.search(r'M\s([-]?[\d\.]+)', title)  
                            if match:
                                try:
                                    magnitude = float(match.group(1))  
                                except ValueError as e:
                                    print(f"Error converting magnitude for {title}: {e}")
                                    continue
                            else:
                                print(f"No magnitude found in title for {title}")
                                continue
                            
                            entries.append((date, point, magnitude))  
    return entries

def get_marker_color(magnitude):
    if magnitude >= 5:
        return 'red'
    elif 3 <= magnitude < 5:
        return 'orange'
    elif 1.5 <= magnitude < 3:
        return 'purple'
    elif magnitude < 1.5:
        return 'green'
    else:
        return 'blue'

def plot_on_map(entries):
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    marker_cluster = MarkerCluster().add_to(m)
    
    for date, point, magnitude in entries:
        lat, lon = map(float, point.split())
        marker_color = get_marker_color(magnitude)  
        
        folium.Marker(
            location=[lat, lon],
            popup=f"{date}<br>Magnitude: {magnitude}<br>Latitude: {lat}, Longitude: {lon}",
            icon=folium.Icon(color=marker_color, icon_size=(40, 40)) 
        ).add_to(marker_cluster)
    
    return m

def get_single_date(user_input):
    try:
        if user_input.lower() == "all":  # If the input is "all", select all available data
            # Use a very broad date range that encompasses all possible dates
            start_date = datetime(1900, 1, 1)  # Set a start date far in the past
            end_date = datetime.now()  # Set the end date as today
            return start_date, end_date
        elif len(user_input) == 7:  # If the input is in the format YYYY-MM (month precision)
            start_date = datetime.strptime(f"{user_input}-01", "%Y-%m-%d")
            end_date = (start_date.replace(day=28) + timedelta(days=4)) - timedelta(days=start_date.replace(day=28).day)
            return start_date, end_date
        elif len(user_input) == 4:  # If only year is entered (YYYY)
            start_date = datetime.strptime(f"{user_input}-01-01", "%Y-%m-%d")
            end_date = datetime.strptime(f"{user_input}-12-31", "%Y-%m-%d")
            return start_date, end_date
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None, None

def get_date_range(start_date_input, end_date_input):
    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
        
        if start_date > end_date:
            print("Error: Start date cannot be later than the end date.")
            return None, None
        return start_date, end_date
    except Exception as e:
        print(f"Error parsing date range: {e}")
        return None, None

def show_help():
    help_text = """
       'translate' : This phrase is added at every sentence to get the french , spanish and swahili translation
      
        'translate'  : Cette phrase est ajoutée à chaque phrase pour obtenir la traduction en français, espagnol et swahili.  
      
        'translate' : Esta frase se añade a cada oración para obtener la traducción al francés, español y suajili.
       
       'translate' : Hii kifungu imeongezwa kwenye kila sentensi kupata tafsiri ya Kifaransa, Kihispania na Kiswahili.
       
        'date' :  You can always ask me for the date 
         
        'date' :  Tu peux toujours me demander la date
        
        'fecha':   Siempre puedes pedirme la fecha
        
        'tarehe':  Unaweza kila wakati kuniuliza tarehe

        'time' :   anytime you need the current time in your timezone you can always ask me 

        temps : Chaque fois que tu as besoin de l'heure actuelle dans ton fuseau horaire, tu peux toujours me demander.

        tiempo: Siempre que necesites la hora actual en tu zona horaria, siempre puedes pedírmelo.

        wakati:  Wakati wowote unapotaka saa ya sasa katika eneo lako la muda, unaweza kila wakati kuniuliza.

        'earthquake_report_data': This command prompts me to give you statistics on siesmic activity from 2005 -2025

        'earthquake_report_data':  Cette commande me demande de vous donner des statistiques sur l'activité sismique de 2005 à 2025.

        'earthquake_report_data':  Este comando me pide que te dé estadísticas sobre la actividad sísmica de 2005 a 2025.

        'earthquake_report_data':   Amri hii inanilazimisha kutoa takwimu za shughuli za kutikisa ardhi kuanzia 2005 hadi 2025.
   
        you can always ask me if you need to view siesmic activity over a period of time between 2005 and 2025 

        Tu peux toujours me demander si tu as besoin de voir l'activité sismique sur une période de temps entre 2005 et 2025.
   
        Siempre puedes pedirme si necesitas ver la actividad sísmica durante un período de tiempo entre 2005 y 2025.

        Unaweza kila wakati kuniuliza ikiwa unahitaji kuona shughuli za kutikisa ardhi katika kipindi cha muda kati ya 2005 na 2025.
        
        'mag_size' : this command allows you to see all seismic activity of a magnitude of your choosing 

        'mag_size' : Cette commande vous permet de voir toute l'activité sismique d'une magnitude de votre choix.

        'mag_size' : Este comando te permite ver toda la actividad sísmica de una magnitud de tu elección.

        'mag_size' : Amri hii inakuwezesha kuona shughuli zote za kutikisa ardhi za ukubwa wa uchaguzi wako

        'map_view' : View hotspots on the map in your web browser 

        'map_view' : Afficher les points chauds sur la carte dans votre navigateur web.

        'map_view' : Ver los puntos calientes en el mapa en tu navegador web.

        'map_view' :Tazama maeneo ya moto kwenye ramani katika kivinjari chako cha mtandao.
    """
    return help_text

# Function to generate a response based on the input
def generate_response(input_text):
    
    user_input_lower = input_text.lower()


    if input_text.lower() == "help":
        return show_help()
    
    if input_text.lower() == "history":
        # Request the start and end dates
        start_date_input = input("Enter the start date (YYYY-MM-DD): ")
        end_date_input = input("Enter the end date (YYYY-MM-DD): ")

        try:
            start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format. Please use the format YYYY-MM-DD."
        
        if start_date and end_date:
           
            # Fetch entries based on the date range and place
            entries = get_entries_from_files("weather_userdata", start_date, end_date)
            
            if entries:
                # Plot the entries on the map
                map_obj = display_entries_on_map(entries)
                map_file = "weather_map_with_icons.html"
                
                # Save the generated map
                map_obj.save(map_file)
                
                # Return the path to the saved map
                return f"Map has been saved. Open the following link to view it: file://{os.path.abspath(map_file)}"
            else:
                return f"No entries found for '{user_place}' within {start_date} to {end_date}."
    else:
            return "Invalid date range input. Please provide a valid start and end date."












    # Check if the sentence ends with "Translate" and translate
    if input_text.lower().endswith(" translate"):
        text_to_translate = input_text[:-9].strip()  # Remove the word "Translate"
        return translate_text(text_to_translate)  # Call translate_text function to handle translation
    
    # Check if the input asks for the date or time in English, French, Spanish, or Swahili
    if any(phrase in input_text.lower() for phrase in ["date", "jour", "día", "muda", "siku"]):
        return get_current_date()

    if any(phrase in input_text.lower() for phrase in ["time", "heure", "hora", "wakati"]):
        return get_current_time()
    
    # Check if the input is in the predefined responses dictionary (case insensitive)
    user_input_lower = input_text.lower()  # Convert input to lowercase
    
    if "earthquake_report_data" in input_text.lower():
        # Assuming you need to get the namespace from the XML or relevant data
        calculate_statistics('user.atomfiles')  # Pass the folder path and namespace to calculate_statistics
        return "Earthquake statistics report has been generated. Check the 'displayfiles/user_view_screen.txt' file for details."
    
    if user_input_lower in predefined_responses:
        return predefined_responses[user_input_lower]
    
    view_seismic_triggers = [
        "i would like to view seismic activity over a time range",
        "je voudrais voir l'activité sismique sur une période de temps",  # French
        "quisiera ver la actividad sísmica en un rango de tiempo",  # Spanish
        "ningependa kuona shughuli za mitetemeko ya ardhi kwa muda fulani"  # Swahili
    ]
    
    if any(trigger in input_text.lower() for trigger in view_seismic_triggers):
        print("You can choose from the following options:")
        print("1. Search by Date Range")
        print("2. Search by Time Range")
        print("3. Search by Both Date and Time Range")
        search_type = input("Enter your choice (1/2/3): ").strip()

        folder_path = 'user.atomfiles'
        date_range_start, date_range_end, time_range_start, time_range_end = None, None, None, None

        if search_type == '1':
            date_range_start = parse_date(input("Enter start date (YYYY-MM-DD): ").strip())
            date_range_end = parse_date(input("Enter end date (YYYY-MM-DD): ").strip())
        elif search_type == '2':
            time_range_start = parse_time(input("Enter start time (HH:MM): ").strip())
            time_range_end = parse_time(input("Enter end time (HH:MM): ").strip())
        elif search_type == '3':
            date_range_start = parse_date(input("Enter start date (YYYY-MM-DD): ").strip())
            date_range_end = parse_date(input("Enter end date (YYYY-MM-DD): ").strip())
            time_range_start = parse_time(input("Enter start time (HH:MM): ").strip())
            time_range_end = parse_time(input("Enter end time (HH:MM): ").strip())
        else:
            return "Invalid choice. Please enter 1, 2, or 3."

        file_path, count = search_seismic_activity(folder_path, date_range_start, date_range_end, time_range_start, time_range_end)
        return f"Search completed. {count} matching entries found. Results saved in: {file_path}"
    
    if "mag_size" in input_text.lower():
        search_type = input("Enter the magnitude size or range (e.g., 1.5, >2, <=3.0): ").strip()
        file_path, count = search_magnitude('user.atomfiles', search_type)
        print(f"Magnitude search results saved to {file_path}")
        return f"Magnitude search completed. Data saved in: {file_path}"



    # Add the user input to the conversation history (this will be used for context generation)
    conversation_history.append(f"Human: {input_text}")
    
    # Join all previous conversation turns for context (hidden from user)
    context = "\n".join(conversation_history) + "\nAI:"
    
    # Encode the context to pass to the model
    inputs = tokenizer.encode(context, return_tensors="pt")
    
    # Create an attention mask: All tokens should be attended to (no padding)
    attention_mask = torch.ones(inputs.shape, device=inputs.device)
      
    # List of possible ways users may ask for locations
    location_triggers = [
        # English
        "show locations", "list locations", "list places",
        "display locations", "show places",
        "where did events occur", "what locations are in the records",
        "which places are available",
        
        # French
        "afficher les emplacements", "lister les emplacements", "lister les lieux",
        "afficher les lieux", "où les événements se sont-ils produits",
        "quels lieux sont dans les archives", "quels endroits sont disponibles",
        
        # Spanish
        "mostrar ubicaciones", "listar ubicaciones", "listar lugares",
        "mostrar lugares", "dónde ocurrieron los eventos",
        "qué ubicaciones están en los registros", "qué lugares están disponibles",
        
        # Swahili
        "onyesha maeneo", "orodhesha maeneo", "orodhesha sehemu",
        "onyesha sehemu", "wapi matukio yalitokea",
        "ni maeneo gani yako kwenye rekodi", "ni sehemu zipi zinapatikana"
    ]
    if input_text.lower().strip() in location_triggers:
    # Use the show_locations function to get the formatted list of locations
     locations_display = show_locations()
    print(f"\nBIBA: {locations_display}\n")


    search_keywords = [
    # English
    "search earthquake data", "find events in", "lookup location", "earthquake report", "seismic activity in", 
    "quake data for", "find seismic events", "earthquake history", "tremor records", "recent earthquakes near", 
    "lookup seismic activity",
    
    # Spanish
    "buscar datos de terremotos",  # search earthquake data
    "encontrar eventos en",        # find events in
    "buscar ubicación",            # lookup location
    "informe de terremoto",        # earthquake report
    "actividad sísmica en",        # seismic activity in
    "datos de sismos para",        # quake data for
    "encontrar eventos sísmicos",  # find seismic events
    "historial de terremotos",     # earthquake history
    "registros de temblores",      # tremor records
    "terremotos recientes cerca de", # recent earthquakes near
    "buscar actividad sísmica",    # lookup seismic activity

    # French
    "rechercher des données sur les tremblements de terre",  # search earthquake data
    "trouver des événements à",   # find events in
    "rechercher un emplacement",  # lookup location
    "rapport sur le tremblement de terre",  # earthquake report
    "activité sismique à",        # seismic activity in
    "données sur les séismes pour",  # quake data for
    "trouver des événements sismiques",  # find seismic events
    "historique des tremblements de terre",  # earthquake history
    "enregistrements de secousses",  # tremor records
    "tremblements de terre récents près de",  # recent earthquakes near
    "rechercher une activité sismique",  # lookup seismic activity

    # Swahili
    "tafuta data za tetemeko la ardhi",  # search earthquake data
    "tafuta matukio katika",  # find events in
    "angalia eneo",  # lookup location
    "ripoti ya tetemeko la ardhi",  # earthquake report
    "shughuli za seismic katika",  # seismic activity in
    "data za tetemeko kwa",  # quake data for
    "tafuta matukio ya seismic",  # find seismic events
    "historia ya mitetemeko",  # earthquake history
    "rekodi za mitetemeko",  # tremor records
    "mitetemeko ya hivi karibuni karibu na",  # recent earthquakes near
    "tafuta shughuli za seismic"  # lookup seismic activity
]

    if any(keyword in input_text.lower() for keyword in search_keywords):
        search_place = input("Enter the place (city) to search for: ").strip()
        file_path, count = search_atom_files('user.atomfiles', search_place)
        return f"Search results saved to {file_path}. Number of matching entries: {count}"

    if input_text.lower() == "map_view":
        choice = input("Enter 'single' for a single date or 'range' for a date range: ").lower()
        
        if choice == 'single':
            user_input_date = input("Enter the date (YYYY, YYYY-MM, or 'all' for all data): ")
            start_date, end_date = get_single_date(user_input_date)
        elif choice == 'range':
            start_date_input = input("Enter the start date (YYYY-MM-DD): ")
            end_date_input = input("Enter the end date (YYYY-MM-DD): ")
            start_date, end_date = get_date_range(start_date_input, end_date_input)
        else:
            return "Invalid choice. Please enter 'single' or 'range'."
        
        if start_date and end_date:
            user_place = input("Enter the place (e.g., California): ")
            entries = parse_atom_files_by_place_and_date("user.atomfiles", start_date, end_date, user_place)
            if entries:
                map_obj = plot_on_map(entries)
                map_file = "earthquake_map.html"
                map_obj.save(map_file)
                return f"Map has been saved. Open the following link to view it: file://{os.path.abspath(map_file)}"
            else:
                return f"No entries found for '{user_place}' within {start_date} to {end_date}."
        else:
            return "Invalid date range input."
   

    # Generate a response with the following parameters:
    outputs = model.generate(
        inputs, 
        attention_mask=attention_mask, 
        max_length=200,  # Increase the response length to allow more details
        num_return_sequences=1, 
        no_repeat_ngram_size=3,  # Prevent repeating trigrams
        temperature=0.8,  # Controls randomness, higher = more creative
        top_p=0.9,  # Sampling from the top 90% of logits
        top_k=50,    # Limits the sampling pool to the top 50 tokens
        eos_token_id=tokenizer.eos_token_id,  # Stop generating when eos token is reached
        do_sample=True  # Enable sampling to use temperature and top_p
    )
    
    # Decode the response and return it
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Add the bot's response to the conversation history (this will also be used for context)
    conversation_history.append(f"AI: {response.strip()}")
    
    return response.strip()

# Function to translate the input text into Spanish, French, and Swahili using deep-translator
def translate_text_deep_translator(text):
    translations = {}
    translations['Spanish'] = GoogleTranslator(source='en', target='es').translate(text)
    translations['French'] = GoogleTranslator(source='en', target='fr').translate(text)
    translations['Swahili'] = GoogleTranslator(source='en', target='sw').translate(text)
    
    # Format the translations
    result = f"Spanish: {translations['Spanish']}\nFrench: {translations['French']}\nSwahili: {translations['Swahili']}"
    return result

# Function to switch between translators (deep-translator or googletrans)
def translate_text(text):
    # Randomly choose whether to use deep-translator or googletrans
    import random
    if random.choice([True, False]):
        return translate_text_deep_translator(text)
    else:
        return translate_text_deep_translator(text)

# Function to get the current date in a readable format
def get_current_date():
    current_date = datetime.now()
    return f"Today's date is {current_date.strftime('%A, %B %d, %Y')}."

# Function to get the current time in a readable format
def get_current_time():
    current_time = datetime.now()
    return f"The current time is {current_time.strftime('%I:%M %p')}."

extract_all_locations('user.atomfiles')

# Chat loop

print("Hello! I am your AI Chatbot BIBA powered by DialoGPT. Type 'exit' to end the conversation.")
print("You can type your message followed by 'Translate' to get translations in Spanish, French, and Swahili.")

while True:
    user_input = input("You: ")

    # If user types 'exit', end the conversation
    if user_input.lower() == 'exit':
        print("Goodbye!\nAu revoir!\nKwaheri!\n¡Adiós!")
        break

    # Generate and print the response (either predefined or generated)
    bot_response = generate_response(user_input)
    print(f"BIBA: {bot_response}")