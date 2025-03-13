import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Set the output folder for saving pie charts
OUTPUT_FOLDER = "pie_charts"

# Check if the directory exists, if it does, delete all files in it, otherwise create the folder
if os.path.exists(OUTPUT_FOLDER):
    for file in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, file))
else:
    os.makedirs(OUTPUT_FOLDER)
  
analysis_folder ="rain_analysis"  

if os.path.exists(analysis_folder):
    for file in os.listdir(analysis_folder):
        os.remove(os.path.join(analysis_folder, file))
else:
    os.makedirs(analysis_folder)
  
# Your function to create pie chart for analysis
def create_pie_chart_analysis(data, labels, title, filename):
    if not data or all(d == 0 for d in data):
        print(f"Skipping pie chart generation for {title} because there is no valid data to plot.")
        return  

    plt.figure(figsize=(8, 8))
    colors = plt.cm.Paired.colors[:len(labels)]  # Assign unique colors, ensuring no repeats

    # Create pie chart without displaying labels or percentages on the pie itself
    wedges, _ = plt.pie(
        data, labels=None, startangle=140, colors=colors, pctdistance=1.2, 
        wedgeprops={'edgecolor': 'black'}
    )

    # Calculate percentages and prepare labels for the legend
    total = sum(data)
    legend_labels = [f"{label} - {data[i] / total * 100:.1f}%"
                     for i, label in enumerate(labels)]
    
    # Create legend with the color, label, and percentage
    plt.legend(wedges, legend_labels, title="Legend", loc="center left", bbox_to_anchor=(1, 0.5))

    # Set title
    plt.title(title, fontsize=10)

    # Save chart without any internal labels
    plt.savefig(os.path.join(analysis_folder, filename), bbox_inches='tight')
    plt.close()

# Your function to create pie chart
def create_pie_chart(data, labels, title, filename):
    if not data or all(d == 0 for d in data):
        print(f"Skipping pie chart generation for {title} because there is no valid data to plot.")
        return  

    plt.figure(figsize=(8, 8))
    colors = plt.cm.Paired.colors[:len(labels)]  # Assign unique colors, ensuring no repeats

    # Create pie chart without displaying labels or percentages on the pie itself
    wedges, _ = plt.pie(
        data, labels=None, startangle=140, colors=colors, pctdistance=1.2, 
        wedgeprops={'edgecolor': 'black'}
    )

    # Calculate percentages and prepare labels for the legend
    total = sum(data)
    legend_labels = [f"{label} - {data[i] / total * 100:.1f}%"
                     for i, label in enumerate(labels)]
    
    # Create legend with the color, label, and percentage
    plt.legend(wedges, legend_labels, title="Legend", loc="center left", bbox_to_anchor=(1, 0.5))

    # Set title
    plt.title(title, fontsize=10)

    # Save chart without any internal labels
    plt.savefig(os.path.join(OUTPUT_FOLDER, filename), bbox_inches='tight')
    plt.close()

# Function to classify rainfall data by magnitude
def classify_magnitude(magnitude):
    if magnitude <= 2:
        return 'Low Magnitude'
    elif 3 <= magnitude <= 5:
        return 'Medium Magnitude'
    elif magnitude >= 5:
        return 'High Magnitude'
    return None  # If there's no valid data for magnitude

# Function to classify elevation
def classify_elevation(elevation):
    if elevation <= 10:
        return 'Below Sea Level'
    elif 11 <= elevation <= 30:
        return 'Sea Level'
    elif 31 <= elevation <= 60:
        return 'Ground Level'
    elif 61 <= elevation <= 90:
        return 'Ground Level Mid'
    elif elevation > 90:
        return 'Ground Level High'
    return None

# Function to classify rainfall categories
def classify_rainfall(rain_sum):
    if rain_sum <= 5:
        return 'Low'
    elif 6 <= rain_sum <= 10:
        return 'Medium'
    elif rain_sum >= 10:
        return 'High'
    return None  # If there's no valid data for rainfall sum

# Function to categorize time of day
def categorize_time_of_day(time_str):
    # Split time_str by ':' and get the hour part
    hour = int(time_str.split(':')[0])  # Extract hour as an integer
    
    if 0 <= hour < 10:
        return 'Morning'
    elif 10 <= hour < 13:
        return 'Mid-Morning'
    elif 13 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 20:
        return 'Evening'
    elif 20 <= hour < 24:
        return 'Night'
    return None

# Load your JSON data from the file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Process data and create a pie chart for rainfall categories
def process_rainfall_data_and_create_pie_chart(json_data):
    rainfall_categories = {'Low': 0, 'Medium': 0, 'High': 0}

    # Iterate over each record and classify the rainfall
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        category = classify_rainfall(rain_sum)
        if category:
            rainfall_categories[category] += 1

    # Prepare data for pie chart
    data = list(rainfall_categories.values())
    labels = list(rainfall_categories.keys())

    # Create pie chart
    create_pie_chart(data, labels, "Rainfall Distribution", "rainfall_distribution.png")

# Process data and create a pie chart for rain_sum by time of day
def process_rain_sum_by_time_of_day_and_create_pie_chart(json_data):
    time_of_day_categories = {'Morning': 0, 'Mid-Morning': 0, 'Afternoon': 0, 'Evening': 0, 'Night': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        time_str = entry.get('time', "")
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        time_category = categorize_time_of_day(time_str)

        if time_category:
            time_of_day_categories[time_category] += rain_sum

    # Prepare data for pie chart
    data = list(time_of_day_categories.values())
    labels = list(time_of_day_categories.keys())

    # Create pie chart
    create_pie_chart(data, labels, "Rainfall by Time of Day", "rainfall_by_time_of_day.png")

# Process data and create a pie chart for rain_sum by elevation
def process_rain_sum_by_elevation_and_create_pie_chart(json_data):
    elevation_categories = {'Below Sea Level': 0, 'Sea Level': 0, 'Ground Level': 0, 
                            'Ground Level Mid': 0, 'Ground Level High': 0}

    # Iterate over each record and classify the elevation
    for entry in json_data:
        elevation = entry.get('elevation', 0)
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        elevation_category = classify_elevation(elevation)

        if elevation_category:
            elevation_categories[elevation_category] += rain_sum

    # Prepare data for pie chart
    data = list(elevation_categories.values())
    labels = list(elevation_categories.keys())

    # Create pie chart
    create_pie_chart(data, labels, "Rainfall by Elevation", "rainfall_by_elevation.png")

def process_rain_sum_by_city_and_create_pie_chart(json_data):
    city_rainfall = {}
    total_rain_sum = 0

    # Iterate over each record and calculate total rain_sum by city
    for entry in json_data:
        city = entry.get('city', "")
        
        # Skip entries where the city is None, empty, or a list
        if not city or isinstance(city, list):
            continue

        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        total_rain_sum += rain_sum

        if city:
            if city not in city_rainfall:
                city_rainfall[city] = 0
            city_rainfall[city] += rain_sum

    # Prepare data for pie chart: calculate percentage for each city
    cities = list(city_rainfall.keys())
    percentages = [(city_rainfall[city] / total_rain_sum) * 100 for city in cities]

    # Create pie chart for city rainfall percentages
    create_pie_chart(percentages, cities, "Rainfall by City", "rainfall_by_city.png")

# Process data and create pie charts for rainfall distribution by magnitude
def process_rain_sum_by_magnitude_and_create_pie_chart(json_data):
    magnitude_categories = {'Low Magnitude': 0, 'Medium Magnitude': 0, 'High Magnitude': 0}

    # Iterate over each record and classify the magnitude
    for entry in json_data:
        magnitude = entry.get('magnitude', 0)
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        magnitude_category = classify_magnitude(magnitude)

        if magnitude_category:
            magnitude_categories[magnitude_category] += rain_sum

    # Prepare data for pie chart
    data = list(magnitude_categories.values())
    labels = list(magnitude_categories.keys())

    # Create pie chart for rainfall by magnitude
    create_pie_chart(data, labels, "Rainfall by Magnitude", "rainfall_by_magnitude.png")

def process_city_data_and_create_pie_chart(json_data, city_name):
    rain_low = 0
    rain_medium = 0
    rain_high = 0

    # Loop through the JSON data and filter by city
    for entry in json_data:
    
        city = entry.get('city', "")
        
        # Skip entries where the city is None, empty, or a list
        if not city or isinstance(city, list):
            continue
        if city == city_name:
            rain_sum = entry['weather'].get('rain_sum', 0)
            rainfall_class = classify_rainfall(rain_sum)
            if rainfall_class == 'Low':
                rain_low += 1
            elif rainfall_class == 'Medium':
                rain_medium += 1
            elif rainfall_class == 'High':
                rain_high += 1

    # If there is valid data for the city
    if rain_low + rain_medium + rain_high > 0:
        data = [rain_low, rain_medium, rain_high]
        labels = ['Low Rainfall', 'Medium Rainfall', 'High Rainfall']
        title = f"Rainfall Distribution for {city_name}"
        filename = f"rainfall_distribution_{city_name}.png"

        # Create pie chart for the specific city
        create_pie_chart_analysis(data, labels, title, filename)
    else:
        print(f"No data available for {city_name}.")


# Example usage
if __name__ == "__main__":
    # Replace this with the path to your actual JSON file
    file_path = "merged_data.json"
    
    # Load the data
    json_data = load_json_data(file_path)

    # Create the first pie chart for rainfall distribution
    process_rainfall_data_and_create_pie_chart(json_data)

    # Create the second pie chart for rain_sum by time of day
    process_rain_sum_by_time_of_day_and_create_pie_chart(json_data)

    # Create the third pie chart for rain_sum by elevation
    process_rain_sum_by_elevation_and_create_pie_chart(json_data)

    # Create the fourth pie chart for rain_sum by city
    process_rain_sum_by_city_and_create_pie_chart(json_data)

    # Create the fifth pie chart for rain_sum by magnitude
    process_rain_sum_by_magnitude_and_create_pie_chart(json_data)

    city_name = input("Enter the city name: ")

    # Process the data for the specified city and create the pie chart
    process_city_data_and_create_pie_chart(json_data, city_name)





