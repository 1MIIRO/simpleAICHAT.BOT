import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Set the output folder for saving pie charts
OUTPUT_FOLDER = "earthquake_piechats"

# Check if the directory exists, if it does, delete all files in it, otherwise create the folder
if os.path.exists(OUTPUT_FOLDER):
    for file in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, file))
else:
    os.makedirs(OUTPUT_FOLDER)
  
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

OUTPUT_FOLDER1 = "earthquake_piechats_analysis"

# Check if the directory exists, if it does, delete all files in it, otherwise create the folder
if os.path.exists(OUTPUT_FOLDER1):
    for file in os.listdir(OUTPUT_FOLDER1):
        os.remove(os.path.join(OUTPUT_FOLDER1, file))
else:
    os.makedirs(OUTPUT_FOLDER1)

def create_pie_chart1(data, labels, title, filename):
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
    plt.savefig(os.path.join(OUTPUT_FOLDER1, filename), bbox_inches='tight')
    plt.close()

OUTPUT_FOLDER2 = "rain_piechats"

if os.path.exists(OUTPUT_FOLDER2):
    for file in os.listdir(OUTPUT_FOLDER2):
        os.remove(os.path.join(OUTPUT_FOLDER2, file))
else:
    os.makedirs(OUTPUT_FOLDER2)

def create_pie_chart2(data, labels, title, filename):
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
    plt.savefig(os.path.join(OUTPUT_FOLDER2, filename), bbox_inches='tight')
    plt.close()


OUTPUT_FOLDER2 = "rain_piechats_analysis"

if os.path.exists(OUTPUT_FOLDER2):
    for file in os.listdir(OUTPUT_FOLDER2):
        os.remove(os.path.join(OUTPUT_FOLDER2, file))
else:
    os.makedirs(OUTPUT_FOLDER2)

def create_pie_chart3(data, labels, title, filename):
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
    plt.savefig(os.path.join(OUTPUT_FOLDER2, filename), bbox_inches='tight')
    plt.close()

# Function to classify rainfall data by magnitude
def classify_magnitude(magnitude):
    if magnitude <= 2:
        return 'Low_Magnitude'
    elif 3 <= magnitude <= 5:
        return 'Medium_Magnitude'
    elif magnitude >= 5:
        return 'High_Magnitude'
    return None  # If there's no valid data for magnitude

# Function to classify elevation
def classify_elevation(elevation):
    if elevation <= 10:
        return 'Below_Sea_Level'
    elif 11 <= elevation <= 30:
        return 'Sea_Level'
    elif 31 <= elevation <= 60:
        return 'Ground_Level'
    elif 61 <= elevation <= 90:
        return 'Ground_Level_Mid'
    elif elevation > 90:
        return 'Ground_Level_High'
    return None

# Function to classify rainfall categories
def classify_rainfall(rain_sum):
    if rain_sum <= 5:
        return 'Low_rainfall'
    elif 6 <= rain_sum <= 10:
        return 'Medium_rainfall'
    elif rain_sum >= 10:
        return 'High_rainfall'
    return None  # If there's no valid data for rainfall sum

# Function to categorize time of day
def categorize_time_of_day(time_str):
    # Split time_str by ':' and get the hour part
    hour = int(time_str.split(':')[0])  # Extract hour as an integer
    
    if 0 <= hour < 10:
        return 'Morning'
    elif 10 <= hour < 13:
        return 'Mid_Morning'
    elif 13 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 20:
        return 'Evening'
    elif 20 <= hour < 24:
        return 'Night'
    return None

def get_sunshine_duration(sunshine_seconds):
   
    sunshine_seconds = float(sunshine_seconds)
    return sunshine_seconds / 3600  

# Load your JSON data from the file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Process data and create a pie chart for rainfall categories
def process_earthquake_magnitude_data_and_create_pie_chart(json_data):
    
    earthquake_magnitude_categories = {'Low_Magnitude':0 ,'Medium_Magnitude':0,'High_Magnitude':0}
    
    # Iterate over each record and classify the rainfall
    for entry in json_data:
        magnitude =entry.get('magnitude')
       
        magnitude_category = classify_magnitude(magnitude)
        if magnitude_category:
            if magnitude_category == 'Low_Magnitude':
               earthquake_magnitude_categories['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                earthquake_magnitude_categories['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                earthquake_magnitude_categories['High_Magnitude'] += 1

    # Prepare data for pie chart
    data = list(earthquake_magnitude_categories.values())
    labels = list(earthquake_magnitude_categories.keys())

    # Create pie chart
    create_pie_chart(data, labels, "Magnitude_distribution", "magnitude_distribution.png")

def process_earthquake_magnitude_by_night(json_data):
    night_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        magnitude_category = classify_magnitude(magnitude)
        
        if time_str_category == 'Night':
            if magnitude_category == 'Low_Magnitude':
                night_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                night_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                night_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(night_magnitudes.values())
    labels = list(night_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_night", "magnitude_distribution _by_night.png")

def process_earthquake_magnitude_by_evening(json_data):
    evening_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        time_str = entry.get('time')
        
        time_str_category = categorize_time_of_day(time_str)
        magnitude_category = classify_magnitude(magnitude)
        
        if time_str_category == 'Evening':
            if magnitude_category == 'Low_Magnitude':
                evening_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                evening_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                evening_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(evening_magnitudes.values())
    labels = list(evening_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_evening", "magnitude_distribution _by_evening.png")

def process_earthquake_magnitude_by_afternoon(json_data):
    afternoon_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        magnitude_category = classify_magnitude(magnitude)
        
        if time_str_category == 'Afternoon':
            if magnitude_category == 'Low_Magnitude':
                afternoon_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                afternoon_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                afternoon_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(afternoon_magnitudes.values())
    labels = list(afternoon_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_afternoon", "magnitude_distribution _by_afternoon.png")

def process_earthquake_magnitude_by_mid_morning(json_data):
    MidMorning_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        magnitude_category = classify_magnitude(magnitude)
        
        if time_str_category == 'Mid_Morning':
            if magnitude_category == 'Low_Magnitude':
                 MidMorning_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                 MidMorning_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                 MidMorning_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list( MidMorning_magnitudes.values())
    labels = list( MidMorning_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_ MidMorning_magnitudes", "magnitude_distribution _by_ MidMorning_magnitudes.png")

def process_earthquake_magnitude_by_Morning(json_data):
    Morning_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        magnitude_category = classify_magnitude(magnitude)
        
        if time_str_category == 'Morning':
            if magnitude_category == 'Low_Magnitude':
                Morning_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Morning_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Morning_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Morning_magnitudes.values())
    labels = list(Morning_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Morning", "magnitude_distribution _by_Morning.png")

def process_earthquake_magnitude_by_elevation_Below_Sea_Level(json_data):
    belowsealevel_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        magnitude_category = classify_magnitude(magnitude)
        
        if elevation_category == 'Below_Sea_Level':
            if magnitude_category == 'Low_Magnitude':
                belowsealevel_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                belowsealevel_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                belowsealevel_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(belowsealevel_magnitudes.values())
    labels = list(belowsealevel_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Below_Sea_Level", "magnitude_distribution _by_Below_Sea_Level.png")

def process_earthquake_magnitude_by_elevation_Sea_Level(json_data):
    Sea_Level_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        magnitude_category = classify_magnitude(magnitude)
        
        if elevation_category == 'Sea_Level':
            if magnitude_category == 'Low_Magnitude':
                Sea_Level_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Sea_Level_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Sea_Level_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Sea_Level_magnitudes.values())
    labels = list(Sea_Level_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Sea_Level", "magnitude_distribution _by_Sea_Level.png")

def process_earthquake_magnitude_by_elevation_Ground_Level(json_data):
    Ground_Level_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        elevation = entry.get ('elevation')
        
        elevation_category = classify_elevation(elevation)
        magnitude_category = classify_magnitude(magnitude)
        
        if elevation_category == 'Ground_Level':
            if magnitude_category == 'Low_Magnitude':
               Ground_Level_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Ground_Level_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Ground_Level_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Ground_Level_magnitudes.values())
    labels = list(Ground_Level_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Ground_Level", "magnitude_distribution _by_Ground_Level.png")

def process_earthquake_magnitude_by_elevation_Ground_Level_Mid(json_data):
    Ground_Level_Mid_magnitude = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        elevation = entry.get ('elevation')
        
        elevation_category = classify_elevation(elevation)
        magnitude_category = classify_magnitude(magnitude)
        
        if elevation_category == 'Ground_Level_Mid':
            if magnitude_category == 'Low_Magnitude':
               Ground_Level_Mid_magnitude['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Ground_Level_Mid_magnitude['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Ground_Level_Mid_magnitude['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Ground_Level_Mid_magnitude.values())
    labels = list(Ground_Level_Mid_magnitude.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Ground_Level_Mid", "magnitude_distribution _by_Ground_Level_Mid.png")

def process_earthquake_magnitude_by_elevation_Ground_Level_High(json_data):
    Ground_Level_High_magnitude = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        elevation = entry["elevation"]
        
        elevation_category = categorize_time_of_day(elevation)
        magnitude_category = classify_magnitude(magnitude)
        
        if elevation_category == 'Ground_Level_High':
            if magnitude_category == 'Low_Magnitude':
               Ground_Level_High_magnitude['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Ground_Level_High_magnitude['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Ground_Level_High_magnitude['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Ground_Level_High_magnitude.values())
    labels = list(Ground_Level_High_magnitude.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Ground_Level_High", "magnitude_distribution _by_Ground_Level_High.png")

def process_earthquake_magnitude_by_elevation_Ground_Level_High(json_data):
    Ground_Level_High_magnitude = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        magnitude_category = classify_magnitude(magnitude)
        
        if elevation_category == 'Ground_Level_High':
            if magnitude_category == 'Low_Magnitude':
               Ground_Level_High_magnitude['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Ground_Level_High_magnitude['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Ground_Level_High_magnitude['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Ground_Level_High_magnitude.values())
    labels = list(Ground_Level_High_magnitude.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _by_Ground_Level_High", "magnitude_distribution _by_Ground_Level_High.png")

def process_earthquake_magnitude_by_Low_rainfall(json_data):
    Low_rainfall_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        
        rain_sum_category = classify_rainfall(rain_sum)
        magnitude_category = classify_magnitude(magnitude)
        
        if rain_sum_category == 'Low_rainfall':
            if magnitude_category == 'Low_Magnitude':
               Low_rainfall_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Low_rainfall_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Low_rainfall_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Low_rainfall_magnitudes.values())
    labels = list(Low_rainfall_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _recieved with low rainfall", "magnitude_distribution _by_Low_rainfall_magnitudes.png")

def process_earthquake_magnitude_by_Medium_rainfall(json_data):
    Medium_rainfall_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        
        rain_sum_category = classify_rainfall(rain_sum)
        magnitude_category = classify_magnitude(magnitude)
        
        if rain_sum_category == 'Medium_rainfall':
            if magnitude_category == 'Low_Magnitude':
               Medium_rainfall_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                Medium_rainfall_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                Medium_rainfall_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(Medium_rainfall_magnitudes.values())
    labels = list(Medium_rainfall_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _recieved with Medium_rainfall", "magnitude_distribution _by_Medium_rainfall_magnitudes.png")

def process_earthquake_magnitude_by_High_rainfall(json_data):
    High_rainfall_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        magnitude =entry.get('magnitude')
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        
        rain_sum_category = classify_rainfall(rain_sum)
        magnitude_category = classify_magnitude(magnitude)
        
        if rain_sum_category == 'High_rainfall':
            if magnitude_category == 'Low_Magnitude':
               High_rainfall_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                High_rainfall_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                High_rainfall_magnitudes['High_Magnitude'] += 1


    # Prepare data for pie chart
    data = list(High_rainfall_magnitudes.values())
    labels = list(High_rainfall_magnitudes.keys())

    # Create pie chart
    create_pie_chart(data, labels, "magnitude_distribution _recieved with High_rainfall", "magnitude_distribution _by_High_rainfall_magnitudes.png")


    year_month_set = set()

    for entry in json_data:
        date = entry.get('date')
        if date:
            year, month, _ = date.split("-")  # Extract year and month
            year_month_set.add(f"{year}-{month}")  # Add the unique year-month combination to the set

    return year_month_set

def process_city_data_magnitude_and_create_pie_chart(json_data, city_name,start_date_input,end_date_input):
    city_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Loop through the JSON data and filter by city
    for entry in json_data:
        city = entry.get('city', "")
        event_date = entry.get('date')
        if not city or isinstance(city, list):
            continue

        if city == city_name and start_date_input <= event_date <= end_date_input :
            magnitude =entry.get('magnitude')
            magnitude_category = classify_magnitude(magnitude)
            if magnitude_category == 'Low_Magnitude':
                city_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                    city_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                city_magnitudes['High_Magnitude'] += 1

    # If there is valid data for the city
   
        data = list( city_magnitudes.values())
        labels = list( city_magnitudes.keys())
        title = f"earthquake magnitude Distribution for {city_name} from for {start_date_input} to {end_date_input}"
        filename = f"earthquake_magnitude_distribution_{city_name}_for_{start_date_input}_to_{end_date_input} .png"

        # Create pie chart for the specific city
        create_pie_chart1(data, labels, title, filename)
    else:
        print(f"No data available for {city_name}.")

def process_date_range_by_magnitude_and_create_pie_chart(json_data,start_date_input,end_date_input):
    date_range_magnitudes = {'Low_Magnitude': 0, 'Medium_Magnitude': 0, 'High_Magnitude': 0}

    # Loop through the JSON data and filter by city
    for entry in json_data:
        
        event_date = entry.get('date')
        
        if start_date_input <= event_date <= end_date_input :
            magnitude =entry.get('magnitude')
            magnitude_category = classify_magnitude(magnitude)
            if magnitude_category == 'Low_Magnitude':
                date_range_magnitudes['Low_Magnitude'] += 1
            elif magnitude_category == 'Medium_Magnitude':
                    date_range_magnitudes['Medium_Magnitude'] += 1
            elif magnitude_category == 'High_Magnitude':
                date_range_magnitudes['High_Magnitude'] += 1

    # If there is valid data for the city
   
        data = list( date_range_magnitudes.values())
        labels = list( date_range_magnitudes.keys())
        title = f"earthquake distribution for {start_date_input} to {end_date_input}"
        filename = f"earthquake_distribution_for {start_date_input} to {end_date_input}.png"

        # Create pie chart for the specific city
        create_pie_chart1(data, labels, title, filename)
    else:
        print(f"No data available for for {start_date_input} to {end_date_input}.")

def process_rainfall_data_and_create_pie_chart(json_data):
    
    rainfall_categories = {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}
    
    # Iterate over each record and classify the rainfall
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
       
        rainfall_category = classify_rainfall(rain_sum)
        if rainfall_category:
            if rainfall_category == 'Low_rainfall':
                rainfall_categories['Low_rainfall'] += 1
            elif rainfall_category == 'Medium_rainfall':
                    rainfall_categories['Medium_rainfall'] += 1
            elif rainfall_category == 'High_rainfall':
                rainfall_categories['High_rainfall'] += 1

    # Prepare data for pie chart
    data = list(rainfall_categories.values())
    labels = list(rainfall_categories.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution", "rainfall_distribution.png")

def process_rainfall_by_night(json_data):
    rainfall_categories_by_night= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        rainfall_category = classify_rainfall(rain_sum)
        
        if time_str_category == 'Night':
            if rainfall_category == 'Low_rainfall':
                rainfall_categories_by_night['Low_rainfall'] += 1
            elif rainfall_category == 'Medium_rainfall':
                    rainfall_categories_by_night['Medium_rainfall'] += 1
            elif rainfall_category == 'High_rainfall':
                rainfall_categories_by_night['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list(rainfall_categories_by_night.values())
    labels = list(rainfall_categories_by_night.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_night", "rainfall_distribution _by_night.png")

def process_rainfall_by_evening(json_data):
    rainfall_categories_by_Evening= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        rainfall_category = classify_rainfall(rain_sum)
        
        if time_str_category == 'Evening':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_by_Evening['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_by_Evening['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_by_Evening['High_rainfall'] += 1

    # Prepare data for pie chart
    data = list(rainfall_categories_by_Evening.values())
    labels = list(rainfall_categories_by_Evening.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_night", "rainfall_distribution _by_night.png")

def process_rainfall_by_Afternoon(json_data):
    rainfall_categories_by_Afternoon= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        rainfall_category = classify_rainfall(rain_sum)
        
        if time_str_category == 'Afternoon':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_by_Afternoon['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_by_Afternoon['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_by_Afternoon['High_rainfall'] += 1



    # Prepare data for pie chart
    data = list(rainfall_categories_by_Afternoon.values())
    labels = list(rainfall_categories_by_Afternoon.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_Afternoon", "rainfall_distribution _by_Afternoon.png")

def process_rainfall_by_Mid_Morning(json_data):
    rainfall_categories_by_Mid_Morning= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        rainfall_category = classify_rainfall(rain_sum)
        
        if time_str_category == 'Mid_Morning':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_by_Mid_Morning['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_by_Mid_Morning['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_by_Mid_Morning['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_by_Mid_Morning.values())
    labels = list( rainfall_categories_by_Mid_Morning.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_by_Mid_Morning", "rainfall_distribution _by_ rainfall_categories_by_Mid_Morning.png")

def process_rainfall_by_Morning(json_data):
    rainfall_categories_by_Morning= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        time_str = entry.get('time', "")
        
        time_str_category = categorize_time_of_day(time_str)
        rainfall_category = classify_rainfall(rain_sum)
        
        if time_str_category == 'Morning':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_by_Morning['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_by_Morning['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_by_Morning['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_by_Morning.values())
    labels = list( rainfall_categories_by_Morning.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_by_Morning", "rainfall_distribution _by_ rainfall_categories_by_Morning.png")

def process_rainfall_at_Below_Sea_Level(json_data):
    rainfall_categories_at_Below_Sea_Level= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        rainfall_category = classify_rainfall(rain_sum)
        
        if elevation_category == 'Below_Sea_Level':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_at_Below_Sea_Level['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_at_Below_Sea_Level['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_at_Below_Sea_Level['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_at_Below_Sea_Level.values())
    labels = list( rainfall_categories_at_Below_Sea_Level.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_at_Below_Sea_Level", "rainfall_distribution _by_ rainfall_categories_at_Below_Sea_Level.png")

def process_rainfall_at_Sea_Level(json_data):
    rainfall_categories_at_Sea_Level= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        rainfall_category = classify_rainfall(rain_sum)
        
        if elevation_category == 'Sea_Level':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_at_Sea_Level['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_at_Sea_Level['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_at_Sea_Level['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_at_Sea_Level.values())
    labels = list( rainfall_categories_at_Sea_Level.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_at_Sea_Level", "rainfall_distribution _by_ rainfall_categories_at_Sea_Level.png")

def process_rainfall_at_Ground_Level(json_data):
    rainfall_categories_at_Ground_Level= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        rainfall_category = classify_rainfall(rain_sum)
        
        if elevation_category == 'Ground_Level':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_at_Ground_Level['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_at_Ground_Level['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_at_Ground_Level['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_at_Ground_Level.values())
    labels = list( rainfall_categories_at_Ground_Level.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_at_Ground_Level", "rainfall_distribution _by_ rainfall_categories_at_Ground_Level.png")

def process_rainfall_at_Ground_Level_Mid(json_data):
    rainfall_categories_at_Ground_Level_Mid= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        rainfall_category = classify_rainfall(rain_sum)
        
        if elevation_category == 'Ground_Level_Mid':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_at_Ground_Level_Mid['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_at_Ground_Level_Mid['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_at_Ground_Level_Mid['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_at_Ground_Level_Mid.values())
    labels = list( rainfall_categories_at_Ground_Level_Mid.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_at_Ground_Level_Mid", "rainfall_distribution _by_ rainfall_categories_at_Ground_Level_Mid.png")

def process_rainfall_at_Ground_Level_High(json_data):
    rainfall_categories_at_Ground_Level_High= {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Iterate over each record and classify the time of day
    for entry in json_data:
        rain_sum = entry.get('weather', {}).get('rain_sum', 0)
        elevation = entry["elevation"]
        
        elevation_category = classify_elevation(elevation)
        rainfall_category = classify_rainfall(rain_sum)
        
        if elevation_category == 'Ground_Level_High':
            if  rainfall_category == 'Low_rainfall':
                rainfall_categories_at_Ground_Level_High['Low_rainfall'] += 1
            elif  rainfall_category == 'Medium_rainfall':
                rainfall_categories_at_Ground_Level_High['Medium_rainfall'] += 1
            elif  rainfall_category == 'High_rainfall':
                rainfall_categories_at_Ground_Level_High['High_rainfall'] += 1


    # Prepare data for pie chart
    data = list( rainfall_categories_at_Ground_Level_High.values())
    labels = list( rainfall_categories_at_Ground_Level_High.keys())

    # Create pie chart
    create_pie_chart2(data, labels, "rainfall_distribution _by_ rainfall_categories_at_Ground_Level_High", "rainfall_distribution _by_ rainfall_categories_at_Ground_Level_High.png")

def process_city_data_rain_and_create_pie_chart(json_data, city_name,start_date_input,end_date_input):
    city_rainfall = {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Loop through the JSON data and filter by city
    for entry in json_data:
        city = entry.get('city', "")
        event_date = entry.get('date')
        if not city or isinstance(city, list):
            continue

        if city == city_name and start_date_input <= event_date <= end_date_input :
            rain_sum = entry.get('weather', {}).get('rain_sum', 0)
            rainfall_category = classify_rainfall(rain_sum)
            if rainfall_category == 'Low_rainfall':
                city_rainfall['Low_rainfall'] += 1
            elif rainfall_category == 'Medium_rainfall':
                    city_rainfall['Medium_rainfall'] += 1
            elif rainfall_category == 'High_rainfall':
                city_rainfall['High_rainfall'] += 1

    # If there is valid data for the city
   
        data = list( city_rainfall.values())
        labels = list( city_rainfall.keys())
        title = f"Rainfall Distribution for {city_name} from for {start_date_input} to {end_date_input}"
        filename = f"rainfall_distribution_{city_name}_for_{start_date_input}_to_{end_date_input} .png"

        # Create pie chart for the specific city
        create_pie_chart3(data, labels, title, filename)
    else:
        print(f"No data available for {city_name}.")

def process_date_range_by_rainfall_and_create_pie_chart(json_data,start_date_input,end_date_input):
    date_range_rainfall = {'Low_rainfall': 0, 'Medium_rainfall': 0, 'High_rainfall': 0}

    # Loop through the JSON data and filter by city
    for entry in json_data:
        
        event_date = entry.get('date')
        
        if start_date_input <= event_date <= end_date_input :
            rain_sum = entry.get('weather', {}).get('rain_sum', 0)
            rainfall_category = classify_rainfall(rain_sum)
            if rainfall_category == 'Low_rainfall':
                date_range_rainfall['Low_rainfall'] += 1
            elif rainfall_category == 'Medium_rainfall':
                    date_range_rainfall['Medium_rainfall'] += 1
            elif rainfall_category == 'High_rainfall':
                date_range_rainfall['High_rainfall'] += 1

    # If there is valid data for the city
   
        data = list( date_range_rainfall.values())
        labels = list( date_range_rainfall.keys())
        title = f"Rainfall Distribution for {start_date_input} to {end_date_input}"
        filename = f"rainfall_distribution_for {start_date_input} to {end_date_input}.png"

        # Create pie chart for the specific city
        create_pie_chart3(data, labels, title, filename)
    else:
        print(f"No data available for for {start_date_input} to {end_date_input}.")


if __name__ == "__main__":
    # Replace this with the path to your actual JSON file
    file_path = "merged_data.json"
    
    # Load the data
    json_data = load_json_data(file_path)

    # Create the first pie chart for magntude  distribution
    process_earthquake_magnitude_data_and_create_pie_chart(json_data)
    process_earthquake_magnitude_by_night(json_data)
    process_earthquake_magnitude_by_evening(json_data)
    process_earthquake_magnitude_by_afternoon(json_data)
    process_earthquake_magnitude_by_mid_morning(json_data)
    process_earthquake_magnitude_by_Morning(json_data)
    process_earthquake_magnitude_by_elevation_Below_Sea_Level(json_data)
    process_earthquake_magnitude_by_elevation_Sea_Level(json_data)
    process_earthquake_magnitude_by_elevation_Ground_Level(json_data)
    process_earthquake_magnitude_by_elevation_Ground_Level_Mid(json_data)
    process_earthquake_magnitude_by_elevation_Ground_Level_High(json_data)

    
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    if start_date_input and end_date_input:
        process_date_range_by_magnitude_and_create_pie_chart(json_data,start_date_input,end_date_input)


    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    if start_date_input and end_date_input:
          city_name = input("Enter the city name: ")
    if city_name:
    # Process the data for the specified city and create the pie chart
        process_city_data_magnitude_and_create_pie_chart(json_data, city_name,start_date_input,end_date_input)
       

    process_rainfall_data_and_create_pie_chart(json_data)
    process_rainfall_by_night(json_data)
    process_rainfall_by_evening(json_data)
    process_rainfall_by_Afternoon(json_data)
    process_rainfall_by_Mid_Morning(json_data)
    process_rainfall_by_Morning(json_data)
    process_rainfall_at_Below_Sea_Level(json_data)
    process_rainfall_at_Sea_Level(json_data)
    process_rainfall_at_Ground_Level(json_data)
    process_rainfall_at_Ground_Level_Mid(json_data)
    process_rainfall_at_Ground_Level_High(json_data)

    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    if start_date_input and end_date_input:
        process_date_range_by_rainfall_and_create_pie_chart(json_data,start_date_input,end_date_input)


    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")
    if start_date_input and end_date_input:
          city_name = input("Enter the city name: ")
    if city_name:
    # Process the data for the specified city and create the pie chart
        process_city_data_rain_and_create_pie_chart(json_data, city_name,start_date_input,end_date_input)
       








