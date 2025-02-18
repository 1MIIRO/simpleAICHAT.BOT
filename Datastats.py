import xml.etree.ElementTree as ET
import os
from collections import Counter
import re
import statistics
from datetime import datetime, timedelta

def parse_atom_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    entries = []
    places = []
    times = []
    months = []
    years = []
    elevations = []
    magnitudes = []
    timestamps = []  # Store timestamps to calculate time differences

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        updated = entry.find('{http://www.w3.org/2005/Atom}updated').text
        point = entry.find('{http://www.georss.org/georss}point').text
        
        # Safe handling of elevation data
        elev_text = entry.find('{http://www.georss.org/georss}elev').text
        elev = 0.0  # Default value if elevation is missing or None
        if elev_text is not None:
            try:
                elev = float(elev_text)
            except ValueError:
                elev = 0.0  # Default value if conversion fails
        
        place = title.split()[-1]
        time = updated.split('T')[1].split(':')[0]
        date = updated.split('T')[0]
        month = date.split('-')[1]
        year = date.split('-')[0]

        magnitude_match = re.search(r'M\s([\d\.]+)', title)
        if magnitude_match:
            magnitude = float(magnitude_match.group(1))
        else:
            magnitude = 0.0  # Default value if no magnitude found

        # Append data to respective lists
        entries.append(entry)
        places.append(place)
        times.append(time)
        months.append(month)
        years.append(year)
        elevations.append(elev)
        magnitudes.append(magnitude)
        timestamps.append(updated)  # Storing timestamp

    return entries, places, times, months, years, elevations, magnitudes, timestamps


def calculate_statistics(folder_path):
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
            file_entries, file_places, file_times, file_months, file_years, file_elevations, file_magnitudes, file_timestamps = parse_atom_file(file_path)
            entries.extend(file_entries)
            places.extend(file_places)
            times.extend(file_times)
            months.extend(file_months)
            years.extend(file_years)
            elevations.extend(file_elevations)
            magnitudes.extend(file_magnitudes)
            timestamps.extend(file_timestamps)

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
    highest_elevation_title = entries[highest_elevation_index].find('{http://www.w3.org/2005/Atom}title').text
    lowest_elevation_title = entries[lowest_elevation_index].find('{http://www.w3.org/2005/Atom}title').text

    # Percentage of negative and positive elevations
    negative_elevations = sum(1 for elev in elevations if elev < 0)
    positive_elevations = total_entries - negative_elevations
    percentage_negative_elevations = (negative_elevations / total_entries) * 100 if total_entries else 0
    percentage_positive_elevations = (positive_elevations / total_entries) * 100 if total_entries else 0

    # Average magnitude
    average_magnitude = sum(magnitudes) / total_entries if total_entries else 0

    # Magnitude >= 4 titles
    high_magnitude_titles = [entries[i].find('{http://www.w3.org/2005/Atom}title').text for i in range(total_entries) if magnitudes[i] >= 4]

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

    # Frequency by Hour
    hour_counts = Counter(times)

    # Frequency by Minute, Day, Week, Month, and Year
    earthquake_by_minute = Counter([datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M') for timestamp in timestamps])
    earthquake_by_day = Counter([datetime.fromisoformat(timestamp).strftime('%Y-%m-%d') for timestamp in timestamps])
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
        file.write(f"Frequency of Earthquakes by Hour\n{dict(hour_counts)}\n")
        file.write("----------------------------------------------------------------\n")
        file.write(f"Frequency by Minute\n{dict(earthquake_by_minute)}\n")
        file.write(f"Frequency by Day\n{dict(earthquake_by_day)}\n")
        file.write(f"Frequency by Week\n{dict(earthquake_by_week)}\n")
        file.write(f"Frequency by Month\n{dict(earthquake_by_month)}\n")
        file.write(f"Frequency by Year\n{dict(earthquake_by_year)}\n")
        file.write("----------------------------------------------------------------\n")

# Call the function
folder_path = "user.atomfiles"
calculate_statistics(folder_path)
