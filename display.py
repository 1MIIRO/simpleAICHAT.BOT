import xml.dom.minidom
import os

# Define input and output folder paths
input_folder = "weather_outputs"  # Folder containing generated weather XML files
formatted_output_folder = "weather_userdata"
os.makedirs(formatted_output_folder, exist_ok=True)

# Process each XML file in the weather_outputs folder
for filename in os.listdir(input_folder):
    if filename.endswith(".xml"):
        input_file = os.path.join(input_folder, filename)
        formatted_output_file = os.path.join(formatted_output_folder, filename)
        
        # Read and parse XML content
        with open(input_file, 'r') as file:
            xml_content = file.read()
        dom = xml.dom.minidom.parseString(xml_content)
        formatted_xml = dom.toprettyxml(indent="  ")
        
        # Save formatted XML
        with open(formatted_output_file, 'w') as output_file:
            output_file.write(formatted_xml)
        
        print(f"Formatted XML saved to {formatted_output_file}")