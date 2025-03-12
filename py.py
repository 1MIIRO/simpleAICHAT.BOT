import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

# Load JSON data
def load_data(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

# Ensure "pie_charts" folder exists
OUTPUT_FOLDER = "pie_charts"
if os.path.exists(OUTPUT_FOLDER):
    for file in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, file))
else:
    os.makedirs(OUTPUT_FOLDER)

# Function to create and save pie charts
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

# Process earthquake data
def process_data(data):
    # Initialize counters for time of day and elevation categories
    low_mag_time_of_day = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
    medium_mag_time_of_day = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
    high_mag_time_of_day = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}

    low_mag_elevation = {"below sea-level": 0, "sea-level": 0, "ground_level": 0, "ground_level_mid": 0, "ground_level_high": 0}
    medium_mag_elevation = {"below sea-level": 0, "sea-level": 0, "ground_level": 0, "ground_level_mid": 0, "ground_level_high": 0}
    high_mag_elevation = {"below sea-level": 0, "sea-level": 0, "ground_level": 0, "ground_level_mid": 0, "ground_level_high": 0}

    low_mag_rain = {"low": 0, "mid": 0, "high": 0}
    medium_mag_rain = {"low": 0, "mid": 0, "high": 0}
    high_mag_rain = {"low": 0, "mid": 0, "high": 0}

    total_entries = len(data)  # Total number of entries for percentage calculations

    for entry in data:
        magnitude = entry["magnitude"]
        time = entry["time"]
        elevation = entry["elevation"]
        rain_sum = entry["weather"]["rain_sum"]
        
        # Determine rain category
        if rain_sum <= 5:
            rain_category = "low"
        elif 6 <= rain_sum <= 10:
            rain_category = "mid"
        else:
            rain_category = "high"

        # Determine time of day
        hour = int(time.split(":")[0])
        if 0 <= hour < 12:
            time_of_day = "Morning"
        elif 12 <= hour < 15:
            time_of_day = "Afternoon"
        elif 15 <= hour < 19:
            time_of_day = "Evening"
        else:
            time_of_day = "Night"

        # Categorize by time of day, magnitude, and rain
        if magnitude <= 2.0:
            low_mag_time_of_day[time_of_day] += 1
            low_mag_rain[rain_category] += 1
            # Elevation categorization for low magnitude
            if elevation < 0:
                low_mag_elevation["below sea-level"] += 1
            elif elevation == 0:
                low_mag_elevation["sea-level"] += 1
            elif 0 < elevation <= 100:
                low_mag_elevation["ground_level"] += 1
            elif 100 < elevation <= 200:
                low_mag_elevation["ground_level_mid"] += 1
            else:
                low_mag_elevation["ground_level_high"] += 1
        elif 2.1 <= magnitude <= 3.0:
            medium_mag_time_of_day[time_of_day] += 1
            medium_mag_rain[rain_category] += 1
            # Elevation categorization for medium magnitude
            if elevation < 0:
                medium_mag_elevation["below sea-level"] += 1
            elif elevation == 0:
                medium_mag_elevation["sea-level"] += 1
            elif 0 < elevation <= 100:
                medium_mag_elevation["ground_level"] += 1
            elif 100 < elevation <= 200:
                medium_mag_elevation["ground_level_mid"] += 1
            else:
                medium_mag_elevation["ground_level_high"] += 1
        elif magnitude > 3.0:
            high_mag_time_of_day[time_of_day] += 1
            high_mag_rain[rain_category] += 1
            # Elevation categorization for high magnitude
            if elevation < 0:
                high_mag_elevation["below sea-level"] += 1
            elif elevation == 0:
                high_mag_elevation["sea-level"] += 1
            elif 0 < elevation <= 100:
                high_mag_elevation["ground_level"] += 1
            elif 100 < elevation <= 200:
                high_mag_elevation["ground_level_mid"] += 1
            else:
                high_mag_elevation["ground_level_high"] += 1

    return (low_mag_time_of_day, medium_mag_time_of_day, high_mag_time_of_day,
            low_mag_elevation, medium_mag_elevation, high_mag_elevation,
            low_mag_rain, medium_mag_rain, high_mag_rain)

# Generate pie charts for Low Magnitude Time of Day
def generate_low_mag_time_pie_charts(time_of_day_data):
    total_entries = sum(time_of_day_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in time_of_day_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "Low Magnitude Earthquakes by Time of Day", "low_mag_time_of_day.png")

# Generate pie charts for Medium Magnitude Time of Day
def generate_medium_mag_time_pie_charts(time_of_day_data):
    total_entries = sum(time_of_day_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in time_of_day_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "Medium Magnitude Earthquakes by Time of Day", "medium_mag_time_of_day.png")

# Generate pie charts for High Magnitude Time of Day
def generate_high_mag_time_pie_charts(time_of_day_data):
    total_entries = sum(time_of_day_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in time_of_day_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "High Magnitude Earthquakes by Time of Day", "high_mag_time_of_day.png")

# Generate pie charts for Low Magnitude Elevation
def generate_low_mag_elevation_pie_charts(elevation_data):
    total_entries = sum(elevation_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in elevation_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "Low Magnitude Earthquakes by Elevation", "low_mag_elevation.png")

# Generate pie charts for Medium Magnitude Elevation
def generate_medium_mag_elevation_pie_charts(elevation_data):
    total_entries = sum(elevation_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in elevation_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "Medium Magnitude Earthquakes by Elevation", "medium_mag_elevation.png")

# Generate pie charts for High Magnitude Elevation
def generate_high_mag_elevation_pie_charts(elevation_data):
    total_entries = sum(elevation_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in elevation_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "High Magnitude Earthquakes by Elevation", "high_mag_elevation.png")

# Generate pie charts for Low Magnitude Rain Categories
def generate_low_mag_rain_pie_charts(rain_data):
    total_entries = sum(rain_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in rain_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "Low Magnitude Earthquakes by Rain Categories", "low_mag_rain.png")

# Generate pie charts for Medium Magnitude Rain Categories
def generate_medium_mag_rain_pie_charts(rain_data):
    total_entries = sum(rain_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in rain_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "Medium Magnitude Earthquakes by Rain Categories", "medium_mag_rain.png")

# Generate pie charts for High Magnitude Rain Categories
def generate_high_mag_rain_pie_charts(rain_data):
    total_entries = sum(rain_data.values())
    percentages = {k: (v / total_entries) * 100 if total_entries > 0 else 0 for k, v in rain_data.items()}
    create_pie_chart(list(percentages.values()), list(percentages.keys()), 
                     "High Magnitude Earthquakes by Rain Categories", "high_mag_rain.png")

# Main Execution
json_file = "merged_data.json"
data = load_data(json_file)
low_mag_time_of_day, medium_mag_time_of_day, high_mag_time_of_day, low_mag_elevation, medium_mag_elevation, high_mag_elevation, low_mag_rain, medium_mag_rain, high_mag_rain = process_data(data)

# Generate each pie chart independently
generate_low_mag_time_pie_charts(low_mag_time_of_day)
generate_medium_mag_time_pie_charts(medium_mag_time_of_day)
generate_high_mag_time_pie_charts(high_mag_time_of_day)

generate_low_mag_elevation_pie_charts(low_mag_elevation)
generate_medium_mag_elevation_pie_charts(medium_mag_elevation)
generate_high_mag_elevation_pie_charts(high_mag_elevation)

generate_low_mag_rain_pie_charts(low_mag_rain)
generate_medium_mag_rain_pie_charts(medium_mag_rain)
generate_high_mag_rain_pie_charts(high_mag_rain)
