import xml.etree.ElementTree as ET
import random
import os

# Define input and output folder paths
input_folder = "user.atomfiles"  # Replace with your actual folder path
output_folder = "./weather_outputs"
os.makedirs(output_folder, exist_ok=True)

# Define namespaces
namespaces = {
    'ns0': 'http://www.georss.org/georss',
    'default': 'http://www.w3.org/2005/Atom'
}

# Process each .atom file in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".atom"):
        input_file = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, f"weather_{filename.replace('.atom', '.xml')}")
        
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Create a new XML structure
        feed = ET.Element("feed", {
            "xmlns:ns0": "http://www.georss.org/georss",
            "xmlns": "http://www.w3.org/2005/Atom",
            "xmlns_georss": "http://www.georss.org/georss"
        })
        
        for entry in root.findall(".//default:entry", namespaces):
            point = entry.find(".//ns0:point", namespaces)
            updated = entry.find(".//default:updated", namespaces)
            
            if point is not None and updated is not None:
                location = point.text
                time = updated.text
                
                # Create new entry
                new_entry = ET.SubElement(feed, "entry")
                ET.SubElement(new_entry, "location").text = location
                ET.SubElement(new_entry, "time").text = time
                
                # Weather data
                weather = ET.SubElement(new_entry, "weather")
                ET.SubElement(weather, "weather_code").text = "61.0"
                ET.SubElement(weather, "temperature_2m_max").text = str(round(random.uniform(20, 40), 4))
                ET.SubElement(weather, "temperature_2m_min").text = str(round(random.uniform(10, 25), 4))
                ET.SubElement(weather, "temperature_2m_mean").text = str(round(random.uniform(15, 30), 4))
                ET.SubElement(weather, "sunshine_duration").text = str(round(random.uniform(10000, 30000), 1))
                ET.SubElement(weather, "rain_sum").text = str(round(random.uniform(0, 20), 1))
                ET.SubElement(weather, "snowfall_sum").text = str(round(random.uniform(0, 5), 1))
                ET.SubElement(weather, "precipitation_hours").text = str(round(random.uniform(0, 24), 1))
                ET.SubElement(weather, "wind_speed_10m_max").text = str(round(random.uniform(5, 20), 4))
        
        # Save to file
        tree = ET.ElementTree(feed)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        
        print(f"Simulated weather data saved to {output_file}")
