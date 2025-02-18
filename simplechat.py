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

# Function to extract unique locations from .atom files
def extract_all_locations(folder_path):
    """Extracts unique locations (places) from all .atom files in the folder."""
    global unique_locations
    unique_locations = set()
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.atom'):
            file_path = os.path.join(folder_path, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                for entry in root.findall('atom:entry', namespace):
                    title = entry.find('atom:title', namespace).text
                    location_parts = title.split(' - ')

                    if len(location_parts) > 1:
                        city_place = location_parts[-1].split(', ')
                        if len(city_place) == 2:
                            unique_locations.add(city_place[1].strip())

            except ET.ParseError:
                print(f"Error parsing file: {file_path}")    

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
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss'}
    matching_entries = []
    result_file_path = 'displayfiles/display_search_results.txt'

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
    coordinates = entry.find('georss:point', namespace).text
    elevation = entry.find('georss:elev', namespace).text

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

    magnitude = None
    match = re.search(r'M\s*([\d.]+)', title)
    if match:
        magnitude = float(match.group(1))  

    age = None
    for category in entry.findall('atom:category', namespace):
        if category.get('label') == 'Age':
            age = category.get('term')
    event_data = {
        'title': title,
        'link': link,
        'published': published,
        'coordinates': coordinates,
        'elevation': elevation,
        'age': age,
        'magnitude': magnitude,
        'city': city,
        'place': place
    }

    return event_data


    
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
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss'}
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
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss'}
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



# Function to generate a response based on the input
def generate_response(input_text):

    # Check if the sentence ends with "Translate" and translate
    if input_text.lower().endswith(" translate"):
        text_to_translate = input_text[:-9].strip()  # Remove the word "Translate"
        return translate_text(text_to_translate)  # Call translate_text function to handle translation
    
    # Check if the input asks for the date or time in English, French, Spanish, or Swahili
    if any(phrase in input_text.lower() for phrase in ["date", "jour", "día", "date", "muda", "siku"]):
        return get_current_date()

    if any(phrase in input_text.lower() for phrase in ["time", "heure", "hora", "wakati"]):
        return get_current_time()
    
    # Check if the input is in the predefined responses dictionary (case insensitive)
    user_input_lower = input_text.lower()  # Convert input to lowercase
    
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
        if unique_locations:
            locations_list = "\n".join(sorted(unique_locations))
            print(f"\nBIBA: Here are the locations found in the records:\n{locations_list}\n")
        else:
            print("\nBIBA: No locations found in the dataset.\n")

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

# Function to handle earthquake data


# Function to translate the input text into Spanish, French, and Swahili using deep-translator
def translate_text_deep_translator(text):
    translations = {}
    translations['Spanish'] = GoogleTranslator(source='en', target='es').translate(text)
    translations['French'] = GoogleTranslator(source='en', target='fr').translate(text)
    translations['Swahili'] = GoogleTranslator(source='en', target='sw').translate(text)
    
    # Format the translations
    result = f"Spanish: {translations['Spanish']}\nFrench: {translations['French']}\nSwahili: {translations['Swahili']}"
    return result

# Function to translate the input text into Spanish, French, and Swahili using googletrans
def translate_text_googletrans(text):
    translator = GoogleTranslatorV2()
    translations = {}
    translations['Spanish'] = translator.translate(text, src='en', dest='es').text
    translations['French'] = translator.translate(text, src='en', dest='fr').text
    translations['Swahili'] = translator.translate(text, src='en', dest='sw').text

    # Format the translations
    result = f"Spanish: {translations['Spanish']}\nFrench: {translations['French']}\nSwahili: {translations['Swahili']}"
    return result

# Function to switch between translators (deep-translator or googletrans)
def translate_text(text):
    # Randomly choose whether to use deep-translator or googletrans
    import random
    if random.choice([True, False]):
        return translate_text_googletrans(text)
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
