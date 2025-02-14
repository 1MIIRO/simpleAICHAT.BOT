import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict

namespace = {'atom': "http://www.w3.org/2005/Atom", 'georss': "http://www.georss.org/georss"}

class AtomFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = None
        self.root = None
        self.namespace = namespace
        self.open_file()

    def open_file(self):
        try:
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
            print(f"Atom file '{self.file_path}' opened and parsed successfully.\n")
        except FileNotFoundError:
            print(f"Error: The Atom file '{self.file_path}' was not found.")
        except ET.ParseError:
            print(f"Error: Unable to parse the Atom file '{self.file_path}'. The file may be corrupted.")
        except Exception as e:
            print(f"An unexpected error occurred while opening the Atom file: {e}")

    def close_file(self):
        if self.tree:
            print("Atom file closed.")
        else:
            print("Error: Atom file is not open.")

    def write_atom_info(self, file_path):
        if self.root is None:
            print("Error: Atom file not opened or parsed.")
            return

        feed_title = self.root.find('atom:title', self.namespace).text
        updated = self.root.find('atom:updated', self.namespace).text
        author_name = self.root.find('atom:author/atom:name', self.namespace).text
        author_uri = self.root.find('atom:author/atom:uri', self.namespace).text
        link_href = self.root.find('atom:link[@rel="self"]', self.namespace).get('href')
        icon = self.root.find('atom:icon', self.namespace).text

        with open('displayfiles\\display_atom.txt', 'w', encoding='utf-8') as file:
            file.write("\n")
            file.write(f"Feed Title: {feed_title}\n")
            file.write(f"Updated: {updated}\n")
            file.write(f"Author: {author_name}, {author_uri}\n")
            file.write(f"Identification: {link_href}\n")
            file.write(f"Icon: {icon}\n")
            file.write("\n")

            for entry in self.root.findall('atom:entry', self.namespace):
                title = entry.find('atom:title', self.namespace).text
                link = entry.find('atom:link', self.namespace).get('href')
                published = entry.find('atom:updated', self.namespace).text
                coordinates = entry.find('georss:point', self.namespace).text
                elevation = entry.find('georss:elev', self.namespace).text

                age = None
                for category in entry.findall('atom:category', self.namespace):
                    if category.get('label') == 'Age':
                        age = category.get('term')

                magnitude = None
                for category in entry.findall('atom:category', self.namespace):
                    if category.get('label') == 'Magnitude':
                        magnitude = category.get('term')

                file.write(f"Title: {title}\n")
                file.write(f"ID: {link}\n")
                file.write(f"Published: {published}\n")
                file.write(f"Coordinates: {coordinates}\n")
                file.write(f"Elevation/Depth: {elevation}\n")
                file.write(f"Occurred: {age}\n")
                file.write(f"Magnitude: {magnitude}\n")
                file.write("-" * 120 + "\n")

        print("The output has been written to the display atom file.")

    def process_and_separate_events(self, filepath):
        if self.root is None:
            print("Error: Atom file not opened or parsed.")
            return

        earthquakes = []
        other_events = {
            'Quarry Blasts': [],
            'Explosions': [],
            'Snow Avalanches': []
        }

        # Extract feed metadata
        feed_title = self.root.find('atom:title', self.namespace).text
        feed_updated = self.root.find('atom:updated', self.namespace).text
        feed_author = self.root.find('atom:author/atom:name', self.namespace).text
        feed_author_uri = self.root.find('atom:author/atom:uri', self.namespace).text
        feed_id = self.root.find('atom:id', self.namespace).text
        feed_icon = self.root.find('atom:icon', self.namespace).text

        metadata_content = f"Feed Title: {feed_title}\nUpdated: {feed_updated}\nAuthor: {feed_author}, {feed_author_uri}\nIdentification: {feed_id}\nIcon: {feed_icon}\n\n"

        def process_entry(entry):
            title = entry.find('atom:title', self.namespace).text
            entry_id = entry.find('atom:id', self.namespace).text
            updated = entry.find('atom:updated', self.namespace).text
            coordinates = entry.find('georss:point', self.namespace).text
            elevation = entry.find('georss:elev', self.namespace).text

            age = None
            magnitude = None
            for category in entry.findall('atom:category', self.namespace):
                if category.get('label') == 'Age':
                    age = category.get('term')
                elif category.get('label') == 'Magnitude':
                    magnitude = category.get('term')

            event_data = f"Title: {title}\nID: {entry_id}\nPublished: {updated}\nCoordinates: {coordinates}\nElevation/Depth: {elevation}\nOccurred: {age if age else 'N/A'}\nMagnitude: {magnitude if magnitude else 'N/A'}\n{'-'*120}"

            if title.startswith('M') and 'Quarry Blast' not in title and 'Explosion' not in title and 'Snow Avalanche' not in title:
                earthquakes.append(event_data)
            elif 'Quarry Blast' in title:
                other_events['Quarry Blasts'].append(event_data)
            elif 'Explosion' in title:
                other_events['Explosions'].append(event_data)
            elif 'Snow Avalanche' in title:
                other_events['Snow Avalanches'].append(event_data)

        for entry in self.root.findall('atom:entry', self.namespace):
            process_entry(entry)

        earthquake_file_content = metadata_content + "All Earthquake Events:\n" + "\n".join(earthquakes)

        other_event_content = metadata_content
        for category, events in other_events.items():
            other_event_content += f"\n{category} Events:\n" + "\n".join(events)

        with open('displayfiles\\displayearthquakeonly.txt', 'w', encoding='utf-8') as earthquake_file:
            earthquake_file.write(earthquake_file_content)

        with open('displayfiles\\displaynonearthquakeonly.txt', 'w', encoding='utf-8') as other_event_file:
            other_event_file.write(other_event_content)

        print("Events have been separated and written to respective files.")

    def group_events_by_location(self, file_path):
        if self.root is None:
            print("Error: Atom file not opened or parsed.")
            return

        places = defaultdict(list)

        # Extract feed metadata
        feed_title = self.root.find('atom:title', self.namespace).text
        feed_updated = self.root.find('atom:updated', self.namespace).text
        feed_author = self.root.find('atom:author/atom:name', self.namespace).text
        feed_author_uri = self.root.find('atom:author/atom:uri', self.namespace).text
        feed_id = self.root.find('atom:id', self.namespace).text
        feed_icon = self.root.find('atom:icon', self.namespace).text

        metadata_content = f"Feed Title: {feed_title}\nUpdated: {feed_updated}\nAuthor: {feed_author}, {feed_author_uri}\nIdentification: {feed_id}\nIcon: {feed_icon}\n\n"

        def process_entry(entry):
            title = entry.find('atom:title', self.namespace).text
            entry_id = entry.find('atom:id', self.namespace).text
            updated = entry.find('atom:updated', self.namespace).text
            coordinates = entry.find('georss:point', self.namespace).text
            elevation = entry.find('georss:elev', self.namespace).text

            age = None
            magnitude = None
            for category in entry.findall('atom:category', self.namespace):
                if category.get('label') == 'Age':
                    age = category.get('term')
                elif category.get('label') == 'Magnitude':
                    magnitude = category.get('term')

            event_data = f"Title: {title}\nID: {entry_id}\nPublished: {updated}\nCoordinates: {coordinates}\nElevation/Depth: {elevation}\nOccurred: {age if age else 'N/A'}\nMagnitude: {magnitude if magnitude else 'N/A'}\n{'-'*120}"

            title_parts = title.split(" - ")
            if len(title_parts) > 1:
                location = title_parts[1].strip()

                try:
                    city, place = location.rsplit(',', 1)
                    city = city.strip()
                    place = place.strip()
                except ValueError:
                    city = location
                    place = "Unknown"

                places[place].append(event_data)

        for entry in self.root.findall('atom:entry', self.namespace):
            process_entry(entry)

        output_content = metadata_content
        for place, events in places.items():
            output_content += f"\n{place}\n"
            output_content += "=" * 60 + "\n"
            output_content += "\n".join(events) + "\n"

        with open('displayfiles\\siesmicactivitylocation.txt', 'w', encoding='utf-8') as file:
            file.write(output_content)

        print(f"Events have been grouped by location and written to siesmicactivitylocation.txt")
