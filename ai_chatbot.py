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

# Load pre-trained DialoGPT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

model.eval()

conversation_history = []

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

state_abbreviations = {
    'AK': 'Alaska', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 
    'CO': 'Colorado', 'HI': 'Hawaii', 'NC': 'North Carolina', 'NJ': 'New Jersey', 
    'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OK': 'Oklahoma', 
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'KS': 'Kansas', 'WA': 'Washington', 
    'WY': 'Wyoming', 'TX': 'Texas', 'TN': 'Tennessee'
} 

view_mapofearthquakes_triggers = [
        # English
        "I would like to see earthquake data on the map","Im interested in seeing earthquake data on the map.","Could I see earthquake data on the map?", 
        "Id like to visualize earthquake data on the map.","Can I view the earthquake data on the map?","Id love to explore earthquake data on the map.",
        "Id like to display earthquake data on the map.","I want to see the earthquake data shown on the map.","Can you show earthquake data on the map?"

        # French
        "J'aimerais voir les données sismiques sur la carte.","Je suis intéressé à voir les données sismiques sur la carte.","Puis-je voir les données sismiques sur la carte ?",
        "J'aimerais visualiser les données sismiques sur la carte.","Puis-je voir les données sismiques sur la carte ?","J'adorerais explorer les données sismiques sur la carte.",
        "J'aimerais afficher les données sismiques sur la carte.","Je veux voir les données sismiques affichées sur la carte.","Peux-tu montrer les données sismiques sur la carte ?"

        # Spanish
        "Me gustaría ver los datos sísmicos en el mapa.","Estoy interesado en ver los datos sísmicos en el mapa.","¿Podría ver los datos sísmicos en el mapa?",
        "Me gustaría visualizar los datos sísmicos en el mapa.","¿Puedo ver los datos sísmicos en el mapa?","Me encantaría explorar los datos sísmicos en el mapa.",
        "Me gustaría mostrar los datos sísmicos en el mapa.","Quiero ver los datos sísmicos mostrados en el mapa.","¿Puedes mostrar los datos sísmicos en el mapa?"

        # Swahili
        "Ningependa kuona data za tetemeko la ardhi kwenye ramani.","Nina hamu ya kuona data za tetemeko la ardhi kwenye ramani.", "Naweza kuona data za tetemeko la ardhi kwenye ramani?",
        "Ningependa kuonyesha data za tetemeko la ardhi kwenye ramani.", "Naweza kuona data za tetemeko la ardhi kwenye ramani?","Ningependa kuchunguza data za tetemeko la ardhi kwenye ramani."
        "Ningependa kuonyesha data za tetemeko la ardhi kwenye ramani.","Nataka kuona data za tetemeko la ardhi zikionyeshwa kwenye ramani.","Unaweza kuonyesha data za tetemeko la ardhi kwenye ramani?"
    ]

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

search_keywords = [
    # English
    "search earthquake data", "find events in", "lookup location",  "seismic activity in", 
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

view_seismic_triggers = [
        "i would like to view seismic activity over a period range",
        "je voudrais voir l'activité sismique sur une période de temps",  # French
        "quisiera ver la actividad sísmica en un rango de tiempo",  # Spanish
        "ningependa kuona shughuli za mitetemeko ya ardhi kwa muda fulani"  # Swahili
    ]

view_mapofearthquakesandweather_triggers = [
        # English
        "I would like to see earthquake with the weather data on the map","Id like to view earthquake data along with weather data on the map.","I want to see earthquake data combined with weather information on the map.", 
        "I'd like to visualize earthquake data together with weather data on the map.","Could I see both earthquake and weather data on the map?","I'm interested in viewing earthquake data alongside weather data on the map."
        
        # French
        "J'aimerais voir les données des tremblements de terre avec les données météorologiques sur la carte.",
        "J'aimerais voir les données des tremblements de terre ainsi que les données météorologiques sur la carte.",
        "Je veux voir les données des tremblements de terre combinées avec les informations météorologiques sur la carte.",
        "J'aimerais visualiser les données des tremblements de terre avec les données météorologiques sur la carte.",
        "Puis-je voir à la fois les données des tremblements de terre et les données météorologiques sur la carte ?",
        "Je suis intéressé à voir les données des tremblements de terre accompagnées des données météorologiques sur la carte."

        # Spanish
        "Me gustaría ver los datos de los terremotos con los datos meteorológicos en el mapa.",
        "Me gustaría ver los datos de los terremotos junto con los datos meteorológicos en el mapa.",
        "Quiero ver los datos de los terremotos combinados con la información meteorológica en el mapa.",
        "Me gustaría visualizar los datos de los terremotos junto con los datos meteorológicos en el mapa.",
        "¿Podría ver tanto los datos de los terremotos como los datos meteorológicos en el mapa?",
        "Estoy interesado en ver los datos de los terremotos junto con los datos meteorológicos en el mapa."

        # Swahili
        "Ningependa kuona data za tetemeko la ardhi pamoja na data za hali ya hewa kwenye ramani."
        "Ningependa kuona data za tetemeko la ardhi pamoja na data za hali ya hewa kwenye ramani."
        "Nataka kuona data za tetemeko la ardhi pamoja na taarifa za hali ya hewa kwenye ramani."
        "Ningependa kuona data za tetemeko la ardhi pamoja na data za hali ya hewa kwenye ramani."
        "Naweza kuona data za tetemeko la ardhi na hali ya hewa kwenye ramani?"
        "Nina nia ya kuona data za tetemeko la ardhi pamoja na data za hali ya hewa kwenye ramani."

    ]

view_magnitude_by_size=[
  "I would like to view earth-quake magnitudes by size",
  "I'd like to see earthquake magnitudes sorted by size.",
  "I want to view earthquake magnitudes in order of size.",
  "Can I see earthquake magnitudes categorized by size?",
  "I'd like to view earthquake magnitudes arranged by size.",
  "I want to view earthquake sizes based on their magnitudes.",
  "Could I see earthquake magnitudes organized by their size?",
  "I would like to explore earthquake magnitudes classified by size.",
  "Can I view earthquake magnitudes ranked by size?",
  "I'd like to examine earthquake magnitudes by their size.",
  "I want to view earthquake magnitudes according to their size."

#french
   "J'aimerais voir les magnitudes des tremblements de terre par taille.",
   "J'aimerais voir les magnitudes des tremblements de terre triées par taille.",
   "Je veux voir les magnitudes des tremblements de terre par ordre de taille.",
   "Puis-je voir les magnitudes des tremblements de terre classées par taille ?",
   "J'aimerais voir les magnitudes des tremblements de terre disposées par taille.",
   "Je veux voir les tailles des tremblements de terre en fonction de leurs magnitudes.",
   "Puis-je voir les magnitudes des tremblements de terre organisées par taille ?",
   "J'aimerais explorer les magnitudes des tremblements de terre classées par taille.",
   "Puis-je voir les magnitudes des tremblements de terre classées par taille ?",
   "J'aimerais examiner les magnitudes des tremblements de terre par leur taille.",
   "Je veux voir les magnitudes des tremblements de terre en fonction de leur taille.",
#spanish 
    "Me gustaría ver las magnitudes de los terremotos por tamaño.",
    "Me gustaría ver las magnitudes de los terremotos ordenadas por tamaño.",
    "Quiero ver las magnitudes de los terremotos en orden de tamaño.",
    "¿Puedo ver las magnitudes de los terremotos categorizadas por tamaño?",
    "Me gustaría ver las magnitudes de los terremotos organizadas por tamaño.",
    "Quiero ver los tamaños de los terremotos según sus magnitudes.",
    "¿Puedo ver las magnitudes de los terremotos organizadas por su tamaño?",
    "Me gustaría explorar las magnitudes de los terremotos clasificadas por tamaño.",
    "¿Puedo ver las magnitudes de los terremotos clasificadas por tamaño?",
    "Me gustaría examinar las magnitudes de los terremotos por su tamaño.",
    "Quiero ver las magnitudes de los terremotos según su tamaño."
#Swahili
     "Ningependa kuona magnitudes za matetemeko ya ardhi kulingana na ukubwa."
    "Ningependa kuona magnitudes za matetemeko ya ardhi zilizopangwa kulingana na ukubwa."
    "Nataka kuona magnitudes za matetemeko ya ardhi kwa mpangilio wa ukubwa."
    "Naweza kuona magnitudes za matetemeko ya ardhi zilizokategorizwa kulingana na ukubwa?"
    "Ningependa kuona magnitudes za matetemeko ya ardhi zilizopangwa kulingana na ukubwa."
    "Nataka kuona ukubwa wa matetemeko ya ardhi kulingana na magnitudes zao."
    "Naweza kuona magnitudes za matetemeko ya ardhi zilizopangwa kulingana na ukubwa wao?"
    "Ningependa kuchunguza magnitudes za matetemeko ya ardhi zilizokasimu kulingana na ukubwa."
    "Naweza kuona magnitudes za matetemeko ya ardhi zilizoainishwa kulingana na ukubwa?"
    "Ningependa kuchunguza magnitudes za matetemeko ya ardhi kulingana na ukubwa wao."
    "Nataka kuona magnitudes za matetemeko ya ardhi kulingana na ukubwa wao."

]

view_magnitude_by_sizeplace=[
   "show me magnitude of a spec area of a certian magnitude"
]

view_all_earthquakes_report=[
 "I want a general report on all earth_quake data in the world",
  "Je veux un rapport général sur toutes les données des tremblements de terre dans le monde.",
  "Quiero un informe general sobre todos los datos de terremotos en el mundo."
]

view_a_report_of_earth_quakes_and_weather_of_a_specific_place_and_time=[
 "I would like to view a report on earthquakes and weather of a specific place and time",
 "I would like to view a report on earthquakes and weather for a specific place and time.",
 "I want to see a report on earthquakes and weather for a specific location and time.",
 "Could I get a report on earthquakes and weather at a specific place and time?",
 "Id like to see a report that includes earthquakes and weather for a particular place and time.",
 "Id like to view a detailed report on earthquakes and weather for a given place and time.",
 "Can I view a report on the earthquakes and weather for a specific place and time?",
 "I would like a report on earthquakes and weather data for a specific place and time.",
 "Could I have a report on earthquakes and weather from a certain location and time?",
 "I want to see earthquake and weather data for a specific place and time.",
 "Im interested in viewing a report on earthquakes and weather for a particular place and time."
#french
  "Je voudrais voir un rapport sur les tremblements de terre et la météo pour un endroit et une période spécifiques.",
  "Je veux voir un rapport sur les tremblements de terre et la météo d'un lieu et d'un moment précis.",
 "Puis-je obtenir un rapport sur les tremblements de terre et la météo pour un endroit et un moment spécifiques?",
 "J'aimerais voir un rapport incluant les tremblements de terre et la météo pour un lieu et un moment particuliers.",
 "Je voudrais voir un rapport détaillé sur les tremblements de terre et la météo pour un endroit et un moment donnés.",
 "Puis-je voir un rapport sur les tremblements de terre et la météo d'un lieu et d'un moment spécifiques?",
 "Je voudrais un rapport sur les tremblements de terre et les données météorologiques pour un endroit et un moment spécifiques.",
 "Puis-je avoir un rapport sur les tremblements de terre et la météo d'un lieu et d'un moment donnés?",
 "Je veux voir les données des tremblements de terre et la météo pour un endroit et un moment spécifiques.",
 "Je suis intéressé par un rapport sur les tremblements de terre et la météo pour un lieu et un moment spécifiques."
#spanish
  "Me gustaría ver un informe sobre los terremotos y el clima de un lugar y tiempo específicos."
 "Quiero ver un informe sobre los terremotos y el clima de una ubicación y momento específicos."
 "¿Podría obtener un informe sobre los terremotos y el clima de un lugar y un tiempo específicos?"
 "Me gustaría ver un informe que incluya los terremotos y el clima de un lugar y tiempo determinados."
 "Me gustaría ver un informe detallado sobre los terremotos y el clima de un lugar y tiempo específicos."
 "¿Puedo ver un informe sobre los terremotos y el clima de un lugar y un tiempo específicos?"
 "Quiero un informe sobre los terremotos y los datos climáticos de un lugar y un momento determinados."
 "¿Puedo obtener un informe sobre los terremotos y el clima de un lugar y tiempo específicos?"
 "Quiero ver los datos sobre los terremotos y el clima de un lugar y un tiempo específicos."
 "Estoy interesado en ver un informe sobre los terremotos y el clima de un lugar y tiempo específicos."
#swahili
  "Ningependa kuona ripoti kuhusu matetemeko ya ardhi na hali ya hewa kwa mahali na wakati maalum.",
  "Nataka kuona ripoti kuhusu matetemeko ya ardhi na hali ya hewa kwa eneo na muda maalum.",
 "Naweza kupata ripoti kuhusu matetemeko ya ardhi na hali ya hewa kwa mahali na wakati maalum?",
 "Ningependa kuona ripoti inayojumuisha matetemeko ya ardhi na hali ya hewa kwa mahali na wakati fulani.",
 "Ningependa kuona ripoti ya kina kuhusu matetemeko ya ardhi na hali ya hewa kwa mahali na wakati fulani.",
 "Naweza kuona ripoti kuhusu matetemeko ya ardhi na hali ya hewa kwa mahali na wakati maalum?",
 "Ningependa ripoti kuhusu matetemeko ya ardhi na data za hali ya hewa kwa mahali na wakati maalum.",
 "Naweza kupata ripoti kuhusu matetemeko ya ardhi na hali ya hewa kutoka kwa mahali na wakati fulani?",
 "Nataka kuona data za matetemeko ya ardhi na hali ya hewa kwa mahali na wakati maalum.",
 "Nina nia ya kuona ripoti kuhusu matetemeko ya ardhi na hali ya hewa kwa mahali na wakati maalum."

]

view_weather_report=[
 "give me a weather report",
 "Can you give me a weather report?",
 "Could I have a weather report?",
 "I'd like a weather report.",
 "Please give me a weather report.",
 "Can I get a weather report?",
 "I would like a weather report.",
 "Could you provide a weather report?",
 "Can you show me the weather report?",
 "I need a weather report.",
 "Please show me the weather report."
#french
  "Pouvez-vous me donner un rapport météo ?",
"Puis-je avoir un rapport météo ?",
"J'aimerais un rapport météo.",
"S'il vous plaît, donnez-moi un rapport météo.",
"Puis-je obtenir un rapport météo ?",
"Je voudrais un rapport météo.",
"Pourriez-vous fournir un rapport météo ?",
"Pouvez-vous me montrer le rapport météo ?",
"J'ai besoin d'un rapport météo.",
"S'il vous plaît, montrez-moi le rapport météo."
#Spanish:
"¿Puedes darme un informe del tiempo?",
"¿Puedo tener un informe del tiempo?",
"Me gustaría un informe del tiempo.",
"Por favor, dame un informe del tiempo.",
"¿Puedo obtener un informe del tiempo?",
"Quisiera un informe del tiempo.",
"¿Podrías proporcionar un informe del tiempo?",
"¿Puedes mostrarme el informe del tiempo?",
"Necesito un informe del tiempo.",
"Por favor, muéstrame el informe del tiempo."
#swahili
"Je, unaweza kunipa ripoti ya hali ya hewa?",
"Naweza kupata ripoti ya hali ya hewa?",
"Ningependa ripoti ya hali ya hewa.",
"Tafadhali, nipatie ripoti ya hali ya hewa.",
"Naweza kupata ripoti ya hali ya hewa?",
"Ningependa kupata ripoti ya hali ya hewa.",
"Unaweza kutoa ripoti ya hali ya hewa?",
"Je, unaweza kunionyesha ripoti ya hali ya hewa?",
"Nahitaji ripoti ya hali ya hewa.",
"Tafadhali, nionyeshe ripoti ya hali ya hewa."

]

view_earthquake_report_of_place=[
        "I would like an earthquake report of a specific place in a given period of time " 
        "Can I get an earthquake report for a specific place within a certain period?"
        "I would like an earthquake report for a particular location during a specific time frame."
        "Could you provide an earthquake report for a given place and time?"
        "I'd like to see an earthquake report for a specific location over a certain time period."
        "Can you give me an earthquake report for a particular place and time span?"
        "I need an earthquake report for a specific place and a certain period of time."
        "Could I have an earthquake report for a given location in a specific timeframe?"
        "I would like to see earthquake data for a specific location during a certain period."
        "Could you show me an earthquake report for a particular place within a given time?"
        "I want an earthquake report for a specific place over a certain time period."
        #French:
        "Puis-je obtenir un rapport sur les tremblements de terre pour un lieu spécifique pendant une période donnée ?"
        "J'aimerais un rapport sur les tremblements de terre pour un endroit particulier sur une période précise."
        "Pourriez-vous fournir un rapport sur les tremblements de terre pour un lieu et une période spécifiques ?"
        "Je voudrais voir un rapport sur les tremblements de terre pour un emplacement spécifique pendant une période déterminée."
        "Pouvez-vous me donner un rapport sur les tremblements de terre pour un lieu et une période donnée ?"
        "J'ai besoin d'un rapport sur les tremblements de terre pour un lieu spécifique sur une période donnée."
        "Puis-je avoir un rapport sur les tremblements de terre pour un endroit spécifique et un laps de temps précis ?"
        "Je voudrais voir des données sur les tremblements de terre pour un lieu spécifique pendant une période déterminée."
        "Pouvez-vous me montrer un rapport sur les tremblements de terre pour un lieu donné et une période spécifique ?"
        "Je veux un rapport sur les tremblements de terre pour un lieu précis pendant une période donnée."
        #Spanish:
        "¿Puedo obtener un informe de terremotos para un lugar específico durante un periodo determinado?"
        "Me gustaría un informe de terremotos para un lugar particular en un tiempo específico."
        "¿Podrías proporcionar un informe de terremotos para un lugar y tiempo específicos?"
        "Me gustaría ver un informe de terremotos para un lugar específico durante un periodo determinado."
        "¿Puedes darme un informe de terremotos para un lugar y un período de tiempo determinado?"
        "Necesito un informe de terremotos para un lugar específico y un periodo de tiempo determinado."
        "¿Puedo tener un informe de terremotos para un lugar específico dentro de un marco temporal dado?"
        "Me gustaría ver los datos de terremotos para un lugar específico durante un periodo determinado."
        "¿Puedes mostrarme un informe de terremotos para un lugar específico dentro de un tiempo determinado?"
        "Quiero un informe de terremotos para un lugar específico durante un tiempo determinado."
        #Swahili:
        "Je, naweza kupata ripoti ya tetemeko la ardhi kwa mahali maalum katika kipindi kilichotolewa?"
        "Ningependa ripoti ya tetemeko la ardhi kwa eneo fulani katika kipindi maalum."
        "Unaweza kutoa ripoti ya tetemeko la ardhi kwa mahali na kipindi maalum?"
        "Ningependa kuona ripoti ya tetemeko la ardhi kwa mahali maalum kwa muda fulani."
        "Je, unaweza kunipa ripoti ya tetemeko la ardhi kwa mahali na muda maalum?"
        "Nahitaji ripoti ya tetemeko la ardhi kwa mahali fulani katika kipindi fulani."
        "Naweza kupata ripoti ya tetemeko la ardhi kwa mahali maalum katika kipindi fulani?"
        "Ningependa kuona data za tetemeko la ardhi kwa mahali fulani katika kipindi kilichotolewa."
        "Je, unaweza kuonyesha ripoti ya tetemeko la ardhi kwa mahali fulani ndani ya kipindi maalum?"
        "Nataka ripoti ya tetemeko la ardhi kwa mahali fulani katika kipindi kilichotolewa."

]

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

def extract_all_locations(folder_path, output_file):
    """Extracts unique locations (places) from all .atom files in the folder and outputs them to a text file."""
    unique_locations = set()
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss', 'ns0':"http://www.georss.org/georss"}

    # Process each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.atom'):
            file_path = os.path.join(folder_path, filename)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                for entry in root.findall('atom:entry', namespace):
                    event_data = get_event_data(entry, namespace)
                    title = event_data['title']
                    event_place = event_data['place']
                    city = extract_location_from_title1(title)

                    # If event_place exists, add it (with or without city)
                    if event_place:
                        if city:
                            unique_locations.add(f"{event_place}, {city}")  # Add place and city as a single string
                        else:
                            unique_locations.add(f"{event_place}")  # Add only place as a string

            except ET.ParseError:
                print(f"Error parsing file: {file_path}")

    # Write the locations to a text file
    with open(output_file,'w',encoding='utf-8') as f:
        # Sort locations and write to the output file
        for location in sorted(unique_locations):
            f.write(f"{location}\n")

    print(f"Locations have been written to {output_file}")

def parse_atom_file(file_path):

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing file {file_path}: {e}")
        return None

def search_seismic_activityofplacebydate(folder_path, date_range_start, date_range_end,place):
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
                        event_date = event_data['published_date']
                        event_place = event_data['place']
                        event_mag = event_data['magnitude']
                        updated =event_data['published']
                        elevation =event_data['elevation']
                        title =event_data['title']
                        coordinates =event_data['Coordinates']
                        
                        if event_place and event_place.lower() == place.lower() and date_range_start <= event_date <= date_range_end:

                            matching_entries.append({
                                'title': title,
                                'published': updated,
                                'coordinates': coordinates,
                                'elevation': elevation,
                                'magnitude': event_mag
                            })

        if matching_entries:
            for entry in matching_entries:
                result_file.write(f"Title: {entry['title']}\n")
                result_file.write(f"Published: {entry['published']}\n")
                result_file.write(f"Coordinates: {entry['coordinates']}\n")
                result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                result_file.write(f"Magnitude: {entry['magnitude']}\n")
                result_file.write("-" * 120 + "\n")

    return result_file_path, len(matching_entries)

def search_seismic_activityofplacebytime(folder_path, time_range_start, time_range_end,place):
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
                        event_time = event_data['Published_time']
                        event_place = event_data['place']
                        event_mag = event_data['magnitude']
                        updated =event_data['published']
                        elevation =event_data['elevation']
                        title =event_data['title']
                        coordinates =event_data['Coordinates']
                        
                        if event_place and event_place.lower() == place.lower() and time_range_start <= event_time <= time_range_end:

                            matching_entries.append({
                                'title': title,
                                'published': updated,
                                'coordinates': coordinates,
                                'elevation': elevation,
                                'magnitude': event_mag
                            })

        if matching_entries:
            for entry in matching_entries:
                result_file.write(f"Title: {entry['title']}\n")
                result_file.write(f"Published: {entry['published']}\n")
                result_file.write(f"Coordinates: {entry['coordinates']}\n")
                result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                result_file.write(f"Magnitude: {entry['magnitude']}\n")
                result_file.write("-" * 120 + "\n")

    return result_file_path, len(matching_entries)

def search_seismic_activityofplacebytimeanddate(folder_path, date_range_start, date_range_end,place,time_rangest,timerangeed):
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
                        event_date = event_data['published_date']
                        event_time = event_data['Published_time']
                        event_place = event_data['place']
                        event_mag = event_data['magnitude']
                        updated =event_data['published']
                        elevation =event_data['elevation']
                        title =event_data['title']
                        coordinates =event_data['Coordinates']
                        
                        if event_place and event_place.lower() == place.lower() and date_range_start <= event_date <= date_range_end and time_rangest <= event_time <= timerangeed   :

                            matching_entries.append({
                                'title': title,
                                'published': updated,
                                'coordinates': coordinates,
                                'elevation': elevation,
                                'magnitude': event_mag
                            })

        if matching_entries:
            for entry in matching_entries:
                result_file.write(f"Title: {entry['title']}\n")
                result_file.write(f"Published: {entry['published']}\n")
                result_file.write(f"Coordinates: {entry['coordinates']}\n")
                result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
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

def get_weather_icon_url(icon_code):
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

def get_sunshine_duration(sunshine_seconds):
    return sunshine_seconds / 3600 

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
                event_date = event_data['published_date']
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

def calculate_statisticsofplace(folder_path ,startdate,enddate,place):
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
                event_place =event_data('place')
                event_date =event_data('published_date')
                if event_place and event_place.lower() == place.lower() and startdate <= event_date <= enddate:
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

def load_data_from_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def calculate_average(values):
    return sum(values) / len(values) if values else 0

def get_full_state_name(state_abbreviation):
    return state_abbreviations.get(state_abbreviation, state_abbreviation)

def analyze_data(entries):
    # Initialize variables for max/min values and best location data
    max_temp = -float('inf')
    min_temp = float('inf')
    max_mean_temp = -float('inf')
    max_sunshine_hours = -float('inf')
    min_sunshine_hours = float('inf')
    max_rainfall = -float('inf')
    min_rainfall = float('inf')
    max_snowfall = -float('inf')
    min_snowfall = float('inf')
    max_wind_speed = -float('inf')
    min_wind_speed = float('inf')

    # Initialize dictionary to store date-wise statistics
    date_stats = defaultdict(lambda: {
        'rainfall': [], 'snowfall': [], 'sunshine_hours': [], 'temperature_mean': [] 
    })

    # Initialize data storage for best locations
    best_locations = {
        'max_temp': None, 'min_temp': None, 'max_mean_temp': None,
        'max_sunshine': None, 'min_sunshine': None, 'max_rainfall': None,
        'min_rainfall': None, 'max_snowfall': None, 'min_snowfall': None,
        'max_wind_speed': None, 'min_wind_speed': None
    }

    # Iterate over entries to compute required values
    for entry in entries:
        # Extract weather data
        temperature_max = entry['weather']['temperature_max']
        temperature_min = entry['weather']['temperature_min']
        temperature_mean = entry['weather']['temperature_mean']
        sunshine_hours = entry['weather']['sunshine_hours']
        rainfall = entry['weather']['rain_sum']
        snowfall = entry['weather']['snowfall_sum']
        wind_speed_max = entry['weather']['wind_speed_max']
        place_full_name = get_full_state_name(entry['place'])  # Convert place abbreviation to full name
        time=entry['time']
        date=entry['date']
        city=entry['city']
        # Track max/min values and corresponding locations
        if temperature_max > max_temp:
            max_temp = temperature_max
            best_locations['max_temp'] = (place_full_name, time ,date,city)

        if temperature_min < min_temp:
            min_temp = temperature_min
            best_locations['min_temp'] = (place_full_name, time ,date,city)

        if temperature_mean > max_mean_temp:
            max_mean_temp = temperature_mean
            best_locations['max_mean_temp'] = (place_full_name, time ,date,city)

        if sunshine_hours > max_sunshine_hours:
            max_sunshine_hours = sunshine_hours
            best_locations['max_sunshine'] = (place_full_name, time ,date,city)

        if sunshine_hours < min_sunshine_hours:
            min_sunshine_hours = sunshine_hours
            best_locations['min_sunshine'] = (place_full_name, time ,date,city)

        if rainfall > max_rainfall:
            max_rainfall = rainfall
            best_locations['max_rainfall'] = (place_full_name, time ,date,city)

        if rainfall < min_rainfall:
            min_rainfall = rainfall
            best_locations['min_rainfall'] = (place_full_name, time ,date,city)

        if snowfall > max_snowfall:
            max_snowfall = snowfall
            best_locations['max_snowfall'] = (place_full_name, time ,date,city)

        if snowfall < min_snowfall:
            min_snowfall = snowfall
            best_locations['min_snowfall'] = (place_full_name, time ,date,city)

        if wind_speed_max > max_wind_speed:
            max_wind_speed = wind_speed_max
            best_locations['max_wind_speed'] = (place_full_name, time ,date,city)
        if wind_speed_max < min_wind_speed:
            min_wind_speed = wind_speed_max
            best_locations['min_wind_speed'] = (place_full_name, time ,date,city)

        # Accumulate data for averages by date
        date_stats[entry['date']]['rainfall'].append(rainfall)
        date_stats[entry['date']]['snowfall'].append(snowfall)
        date_stats[entry['date']]['sunshine_hours'].append(sunshine_hours)
        date_stats[entry['date']]['temperature_mean'].append(temperature_mean)

    # Compute average values for each date
    averages_by_date = {}
    for date, stats in date_stats.items():
        averages_by_date[date] = {
            'rainfall': calculate_average(stats['rainfall']),
            'snowfall': calculate_average(stats['snowfall']),
            'sunshine_hours': calculate_average(stats['sunshine_hours']),
            'temperature_mean': calculate_average(stats['temperature_mean'])
        }
    
    # Return a dictionary with all necessary statistics
    return {
        'best_locations': best_locations,
        'averages_by_date': averages_by_date,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'max_mean_temp': max_mean_temp,
        'max_sunshine_hours': max_sunshine_hours,
        'min_sunshine_hours': min_sunshine_hours,
        'max_rainfall': max_rainfall,
        'min_rainfall': min_rainfall,
        'max_snowfall': max_snowfall,
        'min_snowfall': min_snowfall,
        'max_wind_speed': max_wind_speed,
        'min_wind_speed': min_wind_speed
        
    }

def write_stats_to_file(stats):
    max_sunshine_hours_str = stats.get('max_sunshine_hours', '0')  # Default to '0' if not found
    min_sunshine_hours_str = stats.get('min_sunshine_hours', '0')  # Default to '0' if not found
    
# Convert to float before passing to the function
    max_sunshine_in_hours = get_sunshine_duration(float(max_sunshine_hours_str))
    min_sunshine_in_hours = get_sunshine_duration(float(min_sunshine_hours_str))
    
    
    with open('weatherstat.txt', 'w') as f:
        f.write("="*78 + "\n")
        f.write("Weather Report\n")
        f.write("="*78 + "\n")
        f.write(f"Max Temperature Recorded (temperature_max): \n{stats['max_temp']:.2f}\n")
        f.write("-"*78 + "\n")
        f.write(f"Location from where Max Temperature Recorded (temperature_max): \nArea:{stats['best_locations']['max_temp'][0]} \nCity: {stats['best_locations']['max_temp'][3]} \nTime: {stats['best_locations']['max_temp'][1]} \nDate: {stats['best_locations']['max_temp'][2]} \n")
        f.write("-"*78 + "\n")
        f.write(f"Min Temperature Recorded (temperature_min):\n{stats['min_temp']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from where Min Temperature Recorded (temperature_min): \nArea:{stats['best_locations']['min_temp'][0]}\nCity: {stats['best_locations']['min_temp'][3]} \nTime: {stats['best_locations']['min_temp'][1]}\nDate: {stats['best_locations']['min_temp'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Highest Mean Temperature (temperature_mean): \n{stats['max_mean_temp']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from where Mean Temperature Recorded (temperature_mean): \nArea:{stats['best_locations']['max_mean_temp'][0]} \nCity: {stats['best_locations']['max_mean_temp'][3]} \nTime: {stats['best_locations']['max_mean_temp'][1]}\nDate: {stats['best_locations']['max_mean_temp'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Max Sunshine Hours (sunshine_hours): \n{max_sunshine_in_hours:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Max Sunshine Hours (sunshine_hours):  \nArea:{stats['best_locations']['max_sunshine'][0]}\nCity: {stats['best_locations']['max_sunshine'][3]} \nTime: {stats['best_locations']['max_sunshine'][1]}\nDate: {stats['best_locations']['max_sunshine'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Max Sunshine Hours (sunshine_hours): \n{min_sunshine_in_hours:.2f}\n")
        f.write(f"Location from which Min Sunshine Hours (sunshine_hours):  \nArea:{stats['best_locations']['min_sunshine'][0]}\nCity: {stats['best_locations']['min_sunshine'][3]} \nTime: {stats['best_locations']['min_sunshine'][1]}\nDate: {stats['best_locations']['min_sunshine'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Max Rainfall (rain_sum): \n{stats['max_rainfall']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Max Rainfall (rain_sum):  \nArea:{stats['best_locations']['max_rainfall'][0]}\nCity: {stats['best_locations']['max_rainfall'][3]} \nTime: {stats['best_locations']['max_rainfall'][1]}\nDate: {stats['best_locations']['max_rainfall'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Min Rainfall (rain_sum): \n{stats['min_rainfall']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Min Rainfall (rain_sum):\nArea:{stats['best_locations']['min_rainfall'][0]}\nCity: {stats['best_locations']['min_rainfall'][3]} \nTime: {stats['best_locations']['min_rainfall'][1]}\nDate: {stats['best_locations']['min_rainfall'][2]}\n ")
        f.write("-"*78 + "\n")
        f.write(f"Max Snowfall (snowfall_sum): \n{stats['max_snowfall']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Max Snowfall (snowfall_sum): \nArea:{stats['best_locations']['max_snowfall'][0]}\nCity: {stats['best_locations']['max_snowfall'][3]} \nTime: {stats['best_locations']['max_snowfall'][1]}\nDate: {stats['best_locations']['max_snowfall'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Min Snowfall (snowfall_sum): \n{stats['min_snowfall']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Min Snowfall (snowfall_sum):\nArea:{stats['best_locations']['min_snowfall'][0]}\nCity: {stats['best_locations']['min_snowfall'][3]} \nTime: {stats['best_locations']['min_snowfall'][1]}\nDate: {stats['best_locations']['min_snowfall'][2]}\n\n")
        f.write("-"*78 + "\n")
        f.write(f"Max Wind Speed (wind_speed_max): \n{stats['max_wind_speed']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Max Wind Speed (wind_speed_max): \nArea:{stats['best_locations']['max_wind_speed'][0]}\nCity: {stats['best_locations']['max_wind_speed'][3]} \nTime: {stats['best_locations']['max_wind_speed'][1]}\nDate: {stats['best_locations']['max_wind_speed'][2]}\n")
        f.write("-"*78 + "\n")
        f.write(f"Min Wind Speed (wind_speed_max): \n{stats['min_wind_speed']:.2f}\n")
        f.write("\n"+"-"*78 + "\n")
        f.write(f"Location from which Min Wind Speed (wind_speed_max): \nArea:{stats['best_locations']['min_wind_speed'][0]}\nCity: {stats['best_locations']['min_wind_speed'][3]} \nTime: {stats['best_locations']['min_wind_speed'][1]}\nDate: {stats['best_locations']['min_wind_speed'][2]}\n")
        f.write("-"*78 + "\n")
        f.write("\n")
        f.write("="*78 + "\n")
        f.write("Average Statistics by Date\n")
        f.write("="*78 + "\n")
        for date, averages in stats['averages_by_date'].items():
            f.write(f"Average Rainfall on {date}: {averages['rainfall']:.2f}\n")
            f.write(f"Average Snowfall on {date}: {averages['snowfall']:.2f}\n")
            f.write(f"Average Sunshine Hours on {date}: {averages['sunshine_hours']:.2f}\n")
            f.write(f"Average Temperature on {date}: {averages['temperature_mean']:.2f}\n")
            f.write("="*78 + "\n")

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
                            result_file.write(f"Coordinates: {entry['Coordinates']}\n")
                            result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                            result_file.write(f"Magnitude: {entry['magnitude']}\n")
                            result_file.write("-" * 120 + "\n")

    return result_file_path, len(matching_entries)  

def search_magnitudeplace(folder_path, search_type,place,startdate,enddate):
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
                        event_place= event_data('place')
                        event_date=event_data('Published_date')
                        if event_place and event_place.lower() == place.lower() and startdate <= event_date <= enddate:
                            if event_data['magnitude'] is not None and check_magnitude(event_data['magnitude'], search_type):

                                matching_entries.append(event_data)

                    if matching_entries:
                        for entry in matching_entries:
                            result_file.write(f"Title: {entry['title']}\n")
                            result_file.write(f"Published: {entry['published']}\n")
                            result_file.write(f"Coordinates: {entry['Coordinates']}\n")
                            result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
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
                            result_file.write(f"Coordinates: {entry['Coordinates']}\n")
                            result_file.write(f"Elevation/Depth: {entry['elevation']}\n")
                            result_file.write(f"Magnitude: {entry['magnitude']}\n")
                            result_file.write("-" * 120 + "\n")

    # Ensure the function always returns a tuple
    return result_file_path, len(matching_entries)

def generate_report(json_file):
    # Load the data from the given JSON file
    with open(json_file) as file:
        data = json.load(file)
    
    # Helper function to calculate mean
    def mean(values):
        return sum(values) / len(values) if values else 0

    # Helper function to calculate standard deviation
    def std_dev(values):
        return statistics.stdev(values) if len(values) > 1 else 0

    # Extract relevant fields for easier calculations
    magnitudes = [entry["magnitude"] for entry in data]
    elevations = [entry["elevation"] for entry in data]
    temperature_means = [entry["weather"]["temperature_mean"] for entry in data]
    rainfalls = [entry["weather"]["rain_sum"] for entry in data]
    snowfalls = [entry["weather"]["snowfall_sum"] for entry in data]
    cities = [entry["city"] for entry in data]
    
    # 1. Number of records
    num_records = len(data)

    # 2. Highest magnitude recorded
    highest_magnitude = max(magnitudes)
    highest_magnitude_entry = data[magnitudes.index(highest_magnitude)]

    # 3. Lowest magnitude recorded
    lowest_magnitude = min(magnitudes)
    lowest_magnitude_entry = data[magnitudes.index(lowest_magnitude)]

    # 4. Average magnitude
    average_magnitude = mean(magnitudes)

    # 5. Percentage of occurrences with high magnitude (>3)
    high_magnitude_count = sum(1 for mag in magnitudes if mag > 3)
    high_magnitude_percentage = (high_magnitude_count / num_records) * 100

    # 6. Percentage of occurrences with low magnitude (<=3)
    low_magnitude_count = num_records - high_magnitude_count
    low_magnitude_percentage = (low_magnitude_count / num_records) * 100

    # 7. Median magnitude
    median_magnitude = statistics.median(magnitudes)

    # 8. Magnitude standard deviation
    magnitude_std_dev = std_dev(magnitudes)

    # 9. Highest elevation recorded
    highest_elevation = max(elevations)
    highest_elevation_entry = data[elevations.index(highest_elevation)]

    # 10. Lowest elevation recorded
    lowest_elevation = min(elevations)
    lowest_elevation_entry = data[elevations.index(lowest_elevation)]

    # 11. Average elevation
    average_elevation = mean(elevations)

    # 12. Max temperature
    max_temperature = max(temperature_means)
    max_temperature_entry = data[temperature_means.index(max_temperature)]

    # 13. Min temperature
    min_temperature = min(temperature_means)
    min_temperature_entry = data[temperature_means.index(min_temperature)]

    # 14. Temperature range
    temperature_range = max_temperature - min_temperature

    # 15. Temperature standard deviation
    temperature_std_dev = std_dev(temperature_means)

    # 16. City with most earthquakes
    cities = [str(entry["city"]) for entry in data]  # Convert city to string to avoid unhashable types
    city_count = Counter(cities)
    most_earthquakes_city = city_count.most_common(1)[0]

    # 17. City with least earthquakes
    least_earthquakes_city = city_count.most_common()[-1]

    # 18. Total rainfall
    total_rainfall = sum(rainfalls)

    # 19. Average rainfall
    average_rainfall = mean(rainfalls)

    # 20. Rainfall range
    rainfall_range = max(rainfalls) - min(rainfalls)

    # 21. Highest rainfall recorded
    highest_rainfall = max(rainfalls)
    highest_rainfall_entry = data[rainfalls.index(highest_rainfall)]

    # 22. Lowest rainfall recorded
    lowest_rainfall = min(rainfalls)
    lowest_rainfall_entry = data[rainfalls.index(lowest_rainfall)]

    # 23. Total snowfall
    total_snowfall = sum(snowfalls)

    # 24. Average snowfall
    average_snowfall = mean(snowfalls)

    # 25. Percentage of areas which received snow
    snowy_areas_percentage = (sum(1 for snow in snowfalls if snow > 0) / num_records) * 100


     # Relational processing for rainfall, temperature, elevation, etc.
    # Rainfall and Magnitude Data
    rain_and_magnitude = {
        "High rainfall and high magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r > 0 and mag > 3),
        "High rainfall and low magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r > 0 and mag <= 3),
        "low rain and high magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r == 0 and mag > 3),
        "low rain and low magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r == 0 and mag <= 3),
    }

    rain_and_magnitude_percentage = {key: (count / num_records) * 100 for key, count in rain_and_magnitude.items()}

    # Temperature and Magnitude Data
    temp_and_magnitude = {
        "high tempreture and high magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t > 10 and mag > 3),
        "high tempreture and low magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t > 10 and mag <= 3),
        "low tempreture and high magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t < 10 and mag > 3),
        "low tempreture and low magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t < 10 and mag <= 3),
    }

    temp_and_magnitude_percentage = {key: (count / num_records) * 100 for key, count in temp_and_magnitude.items()}

    # Snowfall and Magnitude Data
    snow_and_magnitude = {
        "High snowfall and high magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s > 0 and mag > 3),
        "High snowfall and low magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s > 0 and mag <= 3),
        "low snowfall and high magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s == 0 and mag > 3),
        "low snowfall and low magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s == 0 and mag <= 3),
    }

    snow_and_magnitude_percentage = {key: (count / num_records) * 100 for key, count in snow_and_magnitude.items()}

    # Elevation and Magnitude Data
    elevation_and_magnitude = {
        "slightly above sea level": sum(1 for e, mag in zip(elevations, magnitudes) if 0 <= e <= 20 and mag > 3),
        "1000m above sea level": sum(1 for e, mag in zip(elevations, magnitudes) if 20 < e <= 50 and mag > 3),
        "2000m and more above sea level": sum(1 for e, mag in zip(elevations, magnitudes) if e > 50 and mag > 3),
        "below sea level": sum(1 for e, mag in zip(elevations, magnitudes) if e < 0 and mag > 3),
    }

    elevation_and_magnitude_percentage = {key: (count / num_records) * 100 for key, count in elevation_and_magnitude.items()}
    
    # Filter the data to include only the entries from the city with the most occurrences
    filtered_data = [entry for entry in data if entry["city"] == most_earthquakes_city]
    num_filtered_records = len(filtered_data)
    if num_filtered_records > 0:
    # Extract relevant fields for the filtered city entries
        magnitudes = [entry["magnitude"] for entry in filtered_data]
        elevations = [entry["elevation"] for entry in filtered_data]
        temperature_means = [entry["weather"]["temperature_mean"] for entry in filtered_data]
        rainfalls = [entry["weather"]["rain_sum"] for entry in filtered_data]
        snowfalls = [entry["weather"]["snowfall_sum"] for entry in filtered_data]

        # Rainfall and Magnitude Data for the filtered city
        rain_and_magnitude = {
            "High rainfall and high magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r > 0 and mag > 3),
            "High rainfall and low magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r > 0 and mag <= 3),
            "low rain and high magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r == 0 and mag > 3),
            "low rain and low magnitude": sum(1 for r, mag in zip(rainfalls, magnitudes) if r == 0 and mag <= 3),
        }

        rain_and_magnitude_percentage = {key: (count / num_filtered_records) * 100 for key, count in rain_and_magnitude.items()}

        # Temperature and Magnitude Data for the filtered city
        temp_and_magnitude = {
            "high tempreture and high magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t > 10 and mag > 3),
            "high tempreture and low magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t > 10 and mag <= 3),
            "low tempreture and high magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t < 10 and mag > 3),
            "low tempreture and low magnitude": sum(1 for t, mag in zip(temperature_means, magnitudes) if t < 10 and mag <= 3),
        }

        temp_and_magnitude_percentage = {key: (count / num_filtered_records) * 100 for key, count in temp_and_magnitude.items()}

        # Snowfall and Magnitude Data for the filtered city
        snow_and_magnitude = {
            "High snowfall and high magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s > 0 and mag > 3),
            "High snowfall and low magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s > 0 and mag <= 3),
            "low snowfall and high magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s == 0 and mag > 3),
            "low snowfall and low magnitude": sum(1 for s, mag in zip(snowfalls, magnitudes) if s == 0 and mag <= 3),
        }

        snow_and_magnitude_percentage = {key: (count / num_filtered_records) * 100 for key, count in snow_and_magnitude.items()}

        # Elevation and Magnitude Data for the filtered city
        elevation_and_magnitude = {
            "slightly above sea level": sum(1 for e, mag in zip(elevations, magnitudes) if 0 <= e <= 20 and mag > 3),
            "1000m above sea level": sum(1 for e, mag in zip(elevations, magnitudes) if 20 < e <= 50 and mag > 3),
            "2000m and more above sea level": sum(1 for e, mag in zip(elevations, magnitudes) if e > 50 and mag > 3),
            "below sea level": sum(1 for e, mag in zip(elevations, magnitudes) if e < 0 and mag > 3),
        }

    # Accumulate all report data in a single string
    report_content = "=" * 80 + "\n"
    report_content += "Statistics Report\n"
    report_content += "=" * 80 + "\n"
    report_content += f"Number of recorded records from place: \n{num_records}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Highest magnitude recorded:\n{highest_magnitude}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Location from which highest magnitude was recorded: \n{highest_magnitude_entry['city']} \n"
    report_content += f"Time: {highest_magnitude_entry['time']} \n"
    report_content += f"Date: {highest_magnitude_entry['date']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Lowest magnitude recorded: \n{lowest_magnitude}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Location from which lowest magnitude was recorded: \n{lowest_magnitude_entry['city']} \n"
    report_content += f"Time: {lowest_magnitude_entry['time']} \n"
    report_content += f"Date: {lowest_magnitude_entry['date']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Average magnitude of all seismic activity: \n{average_magnitude}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Percentage of occurrences with high magnitude: \n{high_magnitude_percentage:.2f}%\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Percentage of occurrences with low magnitude: \n{low_magnitude_percentage:.2f}%\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Median magnitude: \n{median_magnitude}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Magnitude Standard Deviation: \n{magnitude_std_dev}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Highest elevation recorded: \n{highest_elevation}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Location from which highest elevation was recorded: \n{highest_elevation_entry['city']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Lowest elevation recorded: \n{lowest_elevation}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Location from which lowest elevation was recorded: \n{lowest_elevation_entry['city']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Average elevation of all seismic activity: \n{average_elevation}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Maximum temperature recorded: {max_temperature}\n"
    report_content += f"Location from which Maximum temperature was recorded: \n{max_temperature_entry['city']} \n"
    report_content += f"Date: {max_temperature_entry['date']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Min temperature: {min_temperature}\n"
    report_content += f"Location from which lowest temperature was recorded: \n{min_temperature_entry['city']} \n"
    report_content += f"Date: {min_temperature_entry['date']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Temperature range: \n{temperature_range}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Temperature Standard Deviation: \n{temperature_std_dev}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"City with the most earthquakes: \n{most_earthquakes_city[0]}\n"
    report_content += f"Number of occurencies:\n{most_earthquakes_city[1]}\n"     
    report_content += "-" * 80 + "\n"                    
    report_content += f"City with the least earthquakes: \n{least_earthquakes_city[0]}\n"
    report_content += f"Number of occurencies:\n{least_earthquakes_city[1]}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Total rainfall: \n{total_rainfall}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Average rainfall: \n{average_rainfall}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Rainfall range: \n{rainfall_range}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Location from which highest rainfall was recorded: \n{highest_rainfall_entry['city']} \n"
    report_content += f"Date: {highest_rainfall_entry['date']} \n"
    report_content += f"Time: {highest_rainfall_entry['time']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Location from which lowest rainfall was recorded: \n{lowest_rainfall_entry['city']} \n"
    report_content += f"Date: {lowest_rainfall_entry['date']} \n"
    report_content += f"Time: {lowest_rainfall_entry['time']} \n"
    report_content += "-" * 80 + "\n"
    report_content += f"Total snowfall: \n{total_snowfall}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Average snowfall:\n{average_snowfall}\n"
    report_content += "-" * 80 + "\n"
    report_content += f"Percentage of areas which received snow: \n{snowy_areas_percentage:.2f}%\n"
    report_content += "-" * 80 + "\n"
    report_content += "City data\n"
    report_content += "=" * 80 + "\n"
    
    # Iterate over unique cities
    for city in set(cities):
        # Filter entries for the current city
        city_entries = [entry for entry in data if entry["city"] == city]
        
        if city_entries:  # Only process the city if it has entries
            # Extract magnitudes for the city
            city_magnitudes = [entry["magnitude"] for entry in city_entries]
            
            # Highest magnitude experienced in the city
            city_highest_magnitude = max(city_magnitudes)
            city_highest_magnitude_entry = city_entries[city_magnitudes.index(city_highest_magnitude)]
            
            # Lowest magnitude experienced in the city
            city_lowest_magnitude = min(city_magnitudes)
            city_lowest_magnitude_entry = city_entries[city_magnitudes.index(city_lowest_magnitude)]
            
            # Max temperature (mean) for the city
            city_temperature_means = [entry["weather"]["temperature_mean"] for entry in city_entries]
            city_max_temperature = max(city_temperature_means)
            city_min_temperature = min(city_temperature_means)

            # Total snowfall and rainfall received by the city
            city_snowfall = sum([entry["weather"]["snowfall_sum"] for entry in city_entries])
            city_rainfall = sum([entry["weather"]["rain_sum"] for entry in city_entries])

            # Average wind speed for the city
            city_wind_speeds = [entry["weather"]["wind_speed_max"] for entry in city_entries]
            city_average_wind_speed = sum(city_wind_speeds) / len(city_wind_speeds) if city_wind_speeds else 0

            # Most common time of occurrence for the city
            times = [entry["time"] for entry in city_entries]
            city_most_common_time = max(set(times), key=times.count) if times else None

            # Append city-specific data to the report
            report_content += f"City name: {city}\n"
            report_content += f"Number of occurrences: {len(city_entries)}\n"
            
            report_content += f"Highest magnitude experienced: \n{city_highest_magnitude} \nDate: {city_highest_magnitude_entry['date']} \n Time: {city_highest_magnitude_entry['time']}\n"
            report_content += f"Lowest magnitude experienced: \n{city_lowest_magnitude} \nDte: {city_lowest_magnitude_entry['date']}\n Time: {city_lowest_magnitude_entry['time']}\n"
            report_content += f"Max temperature experienced: \n{city_max_temperature} \nDate {city_entries[city_temperature_means.index(city_max_temperature)]['date']}\n"
            report_content += f"Min temperature experienced: \n{city_min_temperature} \nDate {city_entries[city_temperature_means.index(city_min_temperature)]['date']}\n"
            report_content += f"Total snowfall received: \n{city_snowfall}\n"
            report_content += f"Total rainfall received: \n{city_rainfall}\n"
            report_content += f"Average wind speed: \n{city_average_wind_speed}\n"
            report_content += f"Most common time occurrence: \n{city_most_common_time}\n"
            report_content += "-" * 80 + "\n"

    report_content += "=" * 80 + "\n"
    report_content += "Relational Processing Data\n"
    report_content += "=" * 80 + "\n"

    report_content += "Rainfall and Magnitude Breakdown:\n"
    for key, value in rain_and_magnitude_percentage.items():
                    report_content += f"{key}: {value:.2f}%\n"
    report_content += "-" * 80 + "\n"
                
    report_content += "Temperature and Magnitude Breakdown:\n"
    for key, value in temp_and_magnitude_percentage.items():
                    report_content += f"{key}: {value:.2f}%\n"
    report_content += "-" * 80 + "\n"
                
    report_content += "Snowfall and Magnitude Breakdown:\n"
    for key, value in snow_and_magnitude_percentage.items():
                    report_content += f"{key}: {value:.2f}%\n"
    report_content += "-" * 80 + "\n"
                
    report_content += "Elevation and Magnitude Breakdown:\n"
    for key, value in elevation_and_magnitude_percentage.items():
                    report_content += f"{key}: {value:.2f}%\n"
    report_content += "-" * 80 + "\n"
    report_content += "Percentages from the city that had the most occurencies\n"
    report_content += "-" * 80 + "\n"
    report_content += "Rainfall and Magnitude Breakdown (City with Most Entries):\n"
    for key, value in rain_and_magnitude_percentage.items():
      report_content += f"{key}: \n{value:.2f}%\n"

# Temperature and Magnitude Breakdown (City with Most Entries)
    report_content += "\nTemperature and Magnitude Breakdown (City with Most Entries):\n"
    for key, value in temp_and_magnitude_percentage.items():
       report_content += f"{key}: \n{value:.2f}%\n"

# Snowfall and Magnitude Breakdown (City with Most Entries)
    report_content += "\nSnowfall and Magnitude Breakdown (City with Most Entries):\n"
    for key, value in snow_and_magnitude_percentage.items():
       report_content += f"{key}: \n{value:.2f}%\n"

# Elevation and Magnitude Breakdown (City with Most Entries)
    report_content += "\nElevation and Magnitude Breakdown (City with Most Entries):\n"
    for key, value in elevation_and_magnitude_percentage.items():
       report_content += f"{key}: \n{value:.2f}%\n"
    report_content += "-" * 80 + "\n"
    report_content += "=" * 80 + "\n"
    report_content += "=" * 80 + "\n"

    

    # Write all content to the file at once
    with open("displayfiles\\weather_earthquake_stat.txt", "w") as file:
        file.write(report_content)

def parse_atom_files_by_place_and_date(folder_path, start_date, end_date, place):
    namespace = {'atom': 'http://www.w3.org/2005/Atom', 'georss': 'http://www.georss.org/georss', 'ns0': "http://www.georss.org/georss"}
    entries = []

    # Loop through all atom files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".atom"):
            file_path = os.path.join(folder_path, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Iterate through all entries in the Atom file
            for entry in root.findall('atom:entry', namespace):
                # Use get_event_data to extract event data
                event_data = get_event_data(entry, namespace)

                # Extract the date from the event data and convert it to a datetime object
                event_date = datetime.strptime(event_data['formatted_date'], '%Y-%m-%d')
                event_place = event_data['place']

                # Only include entries that match the place and date range
                if event_place and event_place.lower() == place.lower() and start_date <= event_date <= end_date:
                    # Collect only magnitude and coordinates
                    magnitude = event_data.get('magnitude', 0.0)  # Use default if no magnitude is found
                    lat = event_data['lat']
                    lon = event_data['lon']

                    # Add relevant data to the entries list
                    entries.append((event_date, lat, lon, magnitude))

    return entries

def plot_on_map(json_file, output_map="displayfiles\\earthquake.view.html"):
    with open(json_file, "r") as file:
        data = json.load(file)

    if not data:
        print("No data found for mapping.")
        return
    
    # Center map at the first entry
    

    # Create map
    m = folium.Map( zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)

    for entry in data:
        date= entry["date"]
        latitude = float(entry["latitude"])  # Convert latitude to float
        longitude = float(entry["longitude"])  # Convert longitude to float
        magnitude = entry["magnitude"]
        
        
        
        folium.Marker(
            location=[latitude, longitude],
            popup=f"{date}<br>Magnitude: {magnitude}<br>Latitude: {latitude}, Longitude: {longitude}",
            icon=folium.Icon(color=get_marker_color(magnitude))
        ).add_to(marker_cluster)
    
    # Save map to HTML file
    m.save(output_map)
    print(f"Map has been saved to {output_map}")
 
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

def getatomdata(folder_path,start_date,end_date,json_filename):
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
                event_date = event_data['published_date']
                title=event_data['title']
                event_place = event_data['place']
                event_time =event_data['Published_time']
                city_fr =extract_location_from_title1(title)
                if not city_fr or not event_place:
                    continue
                # Filter entries by date range and location
                if start_date <= event_date <= end_date:
                    # Collect only magnitude and coordinates
                    magnitude = event_data.get('magnitude', 0.0)  # Default to 0.0 if missing
                    lat = event_data['lat']
                    lon = event_data['lon']

                    # Add relevant data to the entries list
                    earthquake_data.append({
                        "place":event_place,
                        "city":city_fr,
                        "time":event_time,
                        "date": event_date,
                        "latitude": lat,
                        "longitude": lon,
                        "magnitude": magnitude
                    })

    # Save data to JSON file
    with open(json_filename, 'w') as f:
        json.dump(earthquake_data, f, indent=4)

    # Print confirmation message after writing
    print(f"Data has been written to '{json_filename}'.")
    return json_filename

def visualize_earthquake_weather_on_map(json_file, output_map="displayfiles\\weather_earthquakes_on_map.html"):
    """Generate an interactive map with earthquake and weather data."""
    
    with open(json_file, "r") as file:
        data = json.load(file)

    if not data:
        print("No data found for mapping.")
        return
    
    # Center map at the first entry
    

    # Create map
    m = folium.Map( zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)

    for entry in data:
        lat = float(entry["latitude"])  # Convert latitude to float
        lon = float(entry["longitude"])  # Convert longitude to float
        magnitude = entry["magnitude"]
        weather = entry["weather"]
        color = get_marker_color(magnitude)
        sunshine = get_sunshine_duration(float(weather.get("sunshine_hours", "N/A")))
        

        # Create a popup table
        popup_html = f"""
        <table border="1" cellpadding="5" cellspacing="0">
        <tr><td>Date</td><td>{entry["date"]}</td></tr>
        <tr><td>Magnitude</td><td>{entry["magnitude"]}</td></tr>
        <tr><td colspan="2"><strong>Weather Data</strong></td></tr>
        <tr>
            <td>Rainfall Sum</td>
            <td><img src="{get_weather_icon_url('10d')}" alt="rain icon" width="40" height="40">
                {weather.get("rain_sum", "N/A")} mm</td>
        </tr>
        <tr>
            <td>Wind Speed</td>
            <td><img src="{get_weather_icon_url('50d')}" alt="wind icon" width="40" height="40">
                {weather.get("wind_speed_max", "N/A")} km/h</td>
        </tr>
        <tr>
            <td>Snowfall</td>
            <td><img src="{get_weather_icon_url('13d')}" alt="snow icon" width="40" height="40">
                {weather.get("snowfall_sum", "N/A")} mm</td>
        </tr>
        <tr>
            <td>Sunshine Duration</td>
            <td><img src="https://img.icons8.com/ios-filled/50/000000/sun.png" alt="Sunshine" width="40" height="40">
                {sunshine} hours</td>
        </tr>
        <tr>
            <td>Max Temperature</td>
            <td><img src="https://img.icons8.com/ios-filled/50/000000/temperature.png" alt="Temperature" width="40" height="40">
                {weather.get("temperature_max", "N/A")}°C</td>
        </tr>
        <tr>
            <td>Min Temperature</td>
            <td><img src="https://img.icons8.com/ios-filled/50/000000/temperature.png" alt="Temperature" width="40" height="40">
                {weather.get("temperature_min", "N/A")}°C</td>
        </tr>
        <tr>
            <td>Avg Temperature</td>
            <td><img src="https://img.icons8.com/ios-filled/50/000000/temperature.png" alt="Temperature" width="40" height="40">
                {weather.get("temperature_mean", "N/A")}°C</td>
        </tr>
       </table>
         """
        
        popup = folium.Popup(folium.IFrame(popup_html, width=280, height=200), max_width=400)
        
        folium.Marker(
            location=[lat, lon],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=popup,
            icon=folium.Icon(color=get_marker_color(magnitude))
        ).add_to(marker_cluster)
    
    # Save map to HTML file
    m.save(output_map)
    print(f"Map has been saved to {output_map}")

def split_and_filter_by_date(folder_path, start_date, end_date, place, json_filename):
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
                event_date = event_data['published_date']
                event_place = event_data['place']
                event_time =event_data['Published_time']
                # Filter entries by date range and location
                if event_place and event_place.lower() == place.lower() and start_date <= event_date <= end_date:
                    # Collect only magnitude and coordinates
                    magnitude = event_data.get('magnitude', 0.0)  # Default to 0.0 if missing
                    lat = event_data['lat']
                    lon = event_data['lon']

                    # Add relevant data to the entries list
                    earthquake_data.append({
                        "place":place,
                        "time":event_time,
                        "date": event_date,
                        "latitude": lat,
                        "longitude": lon,
                        "magnitude": magnitude
                    })

    # Save data to JSON file
    with open(json_filename, 'w') as json_file:
        json.dump(earthquake_data, json_file, indent=4)

    # Print confirmation message after writing
    print(f"Data has been written to '{json_filename}'.")
    return json_filename

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

def show_help():
   
    # Language selection
    language_options = """
    Please choose your language:
    1. English
    2. Français (French)
    3. Español (Spanish)
    4. Kiswahili (Swahili)
    
    Enter the number of your choice (e.g., '1' for English, '2' for French, etc.):
    """
    print(language_options)
    
    # Get language choice from the user
    language_choice = input("Your choice: ").strip()
    
    # Set the language for the help text based on the user's choice
    if language_choice == '1' or language_choice.lower() == 'english':
        help_text = get_help_text('english')
    elif language_choice == '2' or language_choice.lower() == 'french':
        help_text = get_help_text('french')
    elif language_choice == '3' or language_choice.lower() == 'spanish':
        help_text = get_help_text('spanish')
    elif language_choice == '4' or language_choice.lower() == 'swahili':
        help_text = get_help_text('swahili')
    else:
        print("Invalid choice. Please try again.")
        return
    
    # Show the selected language's help instructions
    print(help_text)

def get_help_text(language):
    # Define help text in different languages
    if language == 'english':
        return """
        Please select one of the following options for detailed help:
        
        1 'translate' 
        2. 'date' 
        3. 'time' 
        4. 'view available locations'
        5. 'search by magnitude'
        6. 'search magnitude of a specific location ina given period of time'
        7. 'search by period of occurance' 
        8. 'get report showing statistics on all earthquakes' 
        9. 'get report showing statistics on earthquakes of a specific place and time' 
        10. 'get report showing statistics on weather occurencies'
        11. 'get report showing statistics on earthquakes and weather occurencies of a specific place and time'
        12. 'view earthquake data on a map'
        13. 'view earthquake and weather data on a map'
        
        Enter the number or keyword of your choice (e.g., '1', 'date', etc.):
        """
    
    elif language == 'french':
        return """
        Veuillez sélectionner l'une des options suivantes pour obtenir de l'aide détaillée :
       1. 'traduire' 
       2. 'date' 
       3. 'heure' 
       4. 'voir les lieux disponibles'
       5. 'chercher par magnitude'
       6. 'chercher par période d'occurrence' 
       7. 'obtenir un rapport montrant les statistiques sur tous les tremblements de terre' 
       8. 'obtenir un rapport montrant les statistiques sur les tremblements de terre d'un lieu et d'un moment spécifiques' 
       9. 'obtenir un rapport montrant les statistiques sur les occurrences météorologiques'
       10. 'obtenir un rapport montrant les statistiques sur les tremblements de terre et les occurrences météorologiques d'un lieu et d'un moment spécifiques'
        
        Entrez le numéro ou le mot-clé de votre choix (par exemple, '1', 'date', etc.) :
        """
    
    elif language == 'spanish':
        return """
        Spanish: Por favor, seleccione una de las siguientes opciones para obtener ayuda detallada:
          Spanish: Por favor, seleccione una de las siguientes opciones para obtener ayuda detallada:

            1. 'traducir'
            2. 'fecha'
            3. 'hora'
            4. 'ver ubicaciones disponibles'
            5. 'buscar por magnitud'
            6. 'buscar por período de ocurrencia'
            7. 'obtener un informe con estadísticas sobre todos los terremotos'
            8. 'obtener un informe con estadísticas sobre terremotos de un lugar y tiempo específicos'
            9. 'obtener un informe con estadísticas sobre ocurrencias meteorológicas'
            10. 'obtener un informe con estadísticas sobre terremotos y ocurrencias meteorológicas de un lugar y tiempo específicos'

            Ingrese el número o la palabra clave de su elección (por ejemplo, '1', 'fecha', etc.):
            
   """ 
    elif language == 'swahili':
        return """
        Tafadhali chagua moja ya chaguzi zifuatazo kwa msaada wa kina:
        tafsiri'
         1. 'tarehe'
         2. 'muda'
         3. 'angalia maeneo yanayopatikana'
         4. 'tafuta kwa ukubwa'
         5. 'tafuta kwa kipindi cha tukio'
         6. 'pata ripoti inayonyesha takwimu za matetemeko ya ardhi yote'
         7. 'pata ripoti inayonyesha takwimu za matetemeko ya ardhi ya mahali na muda maalum'
         8. 'pata ripoti inayonyesha takwimu za matukio ya hali ya hewa'
         9. 'pata ripoti inayonyesha takwimu za matetemeko ya ardhi na matukio ya hali ya hewa ya mahali na muda maalum'
        10. Ingiza namba au neno muhimu la chaguo lako (kwa mfano, '1', 'tarehe', nk.):
                    
        Ingiza nambari au neno la ufunguo la chaguo lako (kwa mfano, '1', 'date', n.k.):
        """
    
    user_choice =input("choose ,choisir ,elegir,chagua:: ")

    if user_choice in ['1', 'translate'] and language == "english":
        detailed_help = """
        You have access to the translate function get any phrase you want in Spanish, French, and Swahili.
        Type in any phrase you want to understand with the keyword translate at the end 
        "choice word"translate
        """
        print(detailed_help)

    if user_choice in ['1', 'translate'] and language == "english":
        detailed_help = """
        You have access to the translate function, get any phrase you want in Spanish, French, and Swahili.
        Type in any phrase you want to understand with the keyword translate at the end.
        "choice word"translate
        """
        print(detailed_help)

    elif user_choice in ['2', 'date'] and language == "english":
        detailed_help = """
        Any phrase you input with the word date, I am programmed to automatically return the current date.
        """
        print(detailed_help)

    elif user_choice in ['3', 'time'] and language == "english":
        detailed_help = """
        Any phrase you input with the word date, I am programmed to automatically return the current time.
        """
        print(detailed_help)

    elif user_choice in ['4', 'view available locations'] and language == "english":
        detailed_help = """
        This can allow you to view all the locations we have information on. This information includes earthquake and weather data.
        You can ask me in any way to show you all the available locations.
        Use sample phrases:
        1. Where did events occur?
        2. List places.
        """
        print(detailed_help)

    elif user_choice in ['5', 'search by magnitude'] and language == "english":
        detailed_help = """
        Search for earthquakes of a specific magnitude in all our data.
        Bring back all the necessary info on those earthquakes.
        All you have to do is make a request in order to view that information.
        """
        print(detailed_help)

    elif user_choice in ['6', 'search magnitude of a specific location in a given period of time']:
        detailed_help = """
        Search for earthquakes of a specific magnitude that occurred in a given location.
        """
        print(detailed_help)

    elif user_choice in ['7', 'search by period of occurrence'] and language == "english":
        detailed_help = """
        Search for earthquakes that have occurred in a given period of time. This is a broad search to show earthquakes that happened in a given date, time, or datetime in the entire data-set.
        """
        print(detailed_help)

    elif user_choice in ['8', 'get report showing statistics on all earthquakes'] and language == "english":
        detailed_help = """
        This will allow you to view statistics of all the data that is present in our data.
        These are broad overall statistics from 2005-2025.
        """
        print(detailed_help)

    elif user_choice in ['9', 'get report showing statistics on earthquakes of a specific place and time'] and language == "english":
        detailed_help = """
        This will provide statistics of earthquakes that have occurred over a given period of time of a specific place. This is a more detailed search.
        """
        print(detailed_help)

    elif user_choice in ['10', 'get report showing statistics on weather occurrences'] and language == "english":
        detailed_help = """
        This will give you weather data statistics of all the data over a specified period of time.
        """
        print(detailed_help)

    elif user_choice in ['11', 'get report showing statistics on earthquakes and weather occurrences of a specific place and time']:
        detailed_help = """
        This will give you weather and earthquake statistics over a chosen period of time for a specific place.
        """
        print(detailed_help)

    elif user_choice in ['12', 'view earthquake data on a map'] and language == "english":
        detailed_help = """
        View earthquake data on a map on your browser for a place over a given period of time.
        """
        print(detailed_help)

    elif user_choice in ['13', 'view earthquake and weather data on a map'] and language == "english":
        detailed_help = """
        View earthquake and weather data of a given period of time and place of a specific location.
        """
        print(detailed_help)

    if user_choice in ['1', 'translate'] and language == "french":
        detailed_help = """
        Vous avez accès à la fonction de traduction. Obtenez toute phrase que vous souhaitez en espagnol, français et swahili.
        Tapez toute phrase que vous souhaitez comprendre avec le mot-clé 'translate' à la fin.
        "choisissez un mot"translate
        """
        print(detailed_help)

    elif user_choice in ['2', 'date'] and language == "french":
        detailed_help = """
        Toute phrase que vous entrez avec le mot 'date', je suis programmé pour retourner automatiquement la date actuelle.
        """
        print(detailed_help)

    elif user_choice in ['3', 'time'] and language == "french":
        detailed_help = """
        Toute phrase que vous entrez avec le mot 'date', je suis programmé pour retourner automatiquement l'heure actuelle.
        """
        print(detailed_help)

    elif user_choice in ['4', 'view available locations'] and language == "french":
        detailed_help = """
        Cela vous permet de voir toutes les localisations pour lesquelles nous avons des informations. Ces informations incluent les données sur les tremblements de terre et la météo.
        Vous pouvez me demander de vous montrer toutes les localisations disponibles de plusieurs façons.
        Utilisez des phrases types :
        1. Où les événements se sont-ils produits ?
        2. Listez les lieux.
        """
        print(detailed_help)

    elif user_choice in ['5', 'search by magnitude'] and language == "french":
        detailed_help = """
        Recherchez des tremblements de terre d'une magnitude spécifique dans toutes nos données.
        Apportez toutes les informations nécessaires sur ces tremblements de terre.
        Vous n'avez qu'à faire une demande pour voir ces informations.
        """
        print(detailed_help)

    elif user_choice in ['6', 'search magnitude of a specific location in a given period of time']:
        detailed_help = """
        Recherchez des tremblements de terre d'une magnitude spécifique qui se sont produits dans une localisation donnée.
        """
        print(detailed_help)

    elif user_choice in ['7', 'search by period of occurrence'] and language == "french":
        detailed_help = """
        Recherchez des tremblements de terre qui se sont produits sur une période donnée. Il s'agit d'une recherche large pour montrer les tremblements de terre qui ont eu lieu à une date, heure ou date/heure donnée dans l'ensemble des données.
        """
        print(detailed_help)

    elif user_choice in ['8', 'get report showing statistics on all earthquakes'] and language == "french":
        detailed_help = """
        Cela vous permettra de voir les statistiques de toutes les données présentes dans nos données.
        Ce sont des statistiques globales de 2005 à 2025.
        """
        print(detailed_help)

    elif user_choice in ['9', 'get report showing statistics on earthquakes of a specific place and time'] and language == "french":
        detailed_help = """
        Cela fournira des statistiques sur les tremblements de terre qui se sont produits sur une période donnée dans un endroit spécifique. Il s'agit d'une recherche plus détaillée.
        """
        print(detailed_help)

    elif user_choice in ['10', 'get report showing statistics on weather occurrences'] and language == "french":
        detailed_help = """
        Cela vous donnera des statistiques sur les données météorologiques de toutes les données sur une période donnée.
        """
        print(detailed_help)

    elif user_choice in ['11', 'get report showing statistics on earthquakes and weather occurrences of a specific place and time'] and language == "french":
        detailed_help = """
        Cela vous donnera des statistiques météorologiques et des tremblements de terre pendant une période choisie pour un endroit spécifique.
        """
        print(detailed_help)

    elif user_choice in ['12', 'view earthquake data on a map'] and language == "french":
        detailed_help = """
        Voir les données des tremblements de terre sur une carte dans votre navigateur pour un lieu pendant une période donnée.
        """
        print(detailed_help)

    elif user_choice in ['13', 'view earthquake and weather data on a map'] and language == "french":
        detailed_help = """
        Voir les données des tremblements de terre et de la météo pendant une période donnée et à un endroit spécifique.
        """
        print(detailed_help)

    if user_choice in ['1', 'translate'] and language == "spanish":
        detailed_help = """
        Tienes acceso a la función de traducción, obtén cualquier frase que quieras en español, francés y swahili.
        Escribe cualquier frase que quieras entender con la palabra clave 'translate' al final.
        "elige una palabra"translate
        """
        print(detailed_help)

    elif user_choice in ['2', 'date'] and language == "spanish":
        detailed_help = """
        Cualquier frase que ingreses con la palabra 'fecha', estoy programado para devolver automáticamente la fecha actual.
        """
        print(detailed_help)

    elif user_choice in ['3', 'time'] and language == "spanish":
        detailed_help = """
        Cualquier frase que ingreses con la palabra 'fecha', estoy programado para devolver automáticamente la hora actual.
        """
        print(detailed_help)

    elif user_choice in ['4', 'view available locations'] and language == "spanish":
        detailed_help = """
        Esto te permite ver todas las ubicaciones sobre las que tenemos información. Esta información incluye datos de terremotos y clima.
        Puedes pedirme que te muestre todas las ubicaciones disponibles de cualquier manera.
        Usa frases de ejemplo:
        1. ¿Dónde ocurrieron los eventos?
        2. Listar lugares.
        """
        print(detailed_help)

    elif user_choice in ['5', 'search by magnitude'] and language == "spanish":
        detailed_help = """
        Busca terremotos de una magnitud específica en todos nuestros datos.
        Devuelve toda la información necesaria sobre esos terremotos.
        Solo tienes que hacer una solicitud para ver esa información.
        """
        print(detailed_help)

    elif user_choice in ['6', 'search magnitude of a specific location in a given period of time']:
        detailed_help = """
        Busca terremotos de una magnitud específica que ocurrieron en una ubicación dada.
        """
        print(detailed_help)

    elif user_choice in ['7', 'search by period of occurrence'] and language == "spanish":
        detailed_help = """
        Busca terremotos que hayan ocurrido en un periodo de tiempo dado. Esta es una búsqueda amplia para mostrar los terremotos que ocurrieron en una fecha, hora o fecha y hora dadas en todo el conjunto de datos.
        """
        print(detailed_help)

    elif user_choice in ['8', 'get report showing statistics on all earthquakes'] and language == "spanish":
        detailed_help = """
        Esto te permitirá ver las estadísticas de todos los datos presentes en nuestros datos.
        Estas son estadísticas generales de 2005 a 2025.
        """
        print(detailed_help)

    elif user_choice in ['9', 'get report showing statistics on earthquakes of a specific place and time'] and language == "spanish":
        detailed_help = """
        Esto proporcionará estadísticas de terremotos que han ocurrido en un periodo de tiempo dado en un lugar específico. Esta es una búsqueda más detallada.
        """
        print(detailed_help)

    elif user_choice in ['10', 'get report showing statistics on weather occurrences'] and language == "spanish":
        detailed_help = """
        Esto te dará estadísticas sobre los datos meteorológicos de todos los datos en un periodo de tiempo determinado.
        """
        print(detailed_help)

    elif user_choice in ['11', 'get report showing statistics on earthquakes and weather occurrences of a specific place and time'] and language == "spanish":
        detailed_help = """
        Esto te dará estadísticas meteorológicas y de terremotos durante un periodo de tiempo elegido para un lugar específico.
        """
        print(detailed_help)

    elif user_choice in ['12', 'view earthquake data on a map'] and language == "spanish":
        detailed_help = """
        Ver datos de terremotos en un mapa en tu navegador de un lugar durante un periodo de tiempo dado.
        """
        print(detailed_help)

    elif user_choice in ['13', 'view earthquake and weather data on a map'] and language == "spanish":
        detailed_help = """
        Ver datos de terremotos y clima de un periodo de tiempo y lugar específico.
        """
        print(detailed_help)

    if user_choice in ['1', 'translate'] and language == "swahili":
        detailed_help = """
        Unaweza kutumia kipengele cha tafsiri, pata sentensi yoyote unayotaka kwa Kihispania, Kifaransa na Kiswahili.
        Andika sentensi yoyote unayotaka kuelewa na neno kuu 'translate' mwishoni.
        "chagua neno"translate
        """
        print(detailed_help)

    elif user_choice in ['2', 'date'] and language == "swahili":
        detailed_help = """
        Sentensi yoyote unayoingiza na neno 'tarehe', nimeprogramu kuonyesha tarehe ya sasa kiotomati.
        """
        print(detailed_help)

    elif user_choice in ['3', 'time'] and language == "swahili":
        detailed_help = """
        Sentensi yoyote unayoingiza na neno 'tarehe', nimeprogramu kuonyesha muda wa sasa kiotomati.
        """
        print(detailed_help)

    elif user_choice in ['4', 'view available locations'] and language == "swahili":
        detailed_help = """
        Hii inakuwezesha kuona maeneo yote ambayo tuna taarifa zake. Taarifa hizi zinajumuisha takwimu za matetemeko ya ardhi na hali ya hewa.
        Unaweza kuniuliza kwa njia yoyote kuonyesha maeneo yote yanayopatikana.
        Tumia mifano ya sentensi:
        1. Mahali gani matukio yalitokea?
        2. Orodhesha maeneo.
        """
        print(detailed_help)

    elif user_choice in ['5', 'search by magnitude'] and language == "swahili":
        detailed_help = """
        Tafuta matetemeko ya ardhi ya ukubwa maalum katika data yetu yote.
        Rudisha taarifa zote muhimu kuhusu matetemeko haya.
        Unachohitaji kufanya ni kuuliza ili kuona taarifa hizo.
        """
        print(detailed_help)

    elif user_choice in ['6', 'search magnitude of a specific location in a given period of time'] and language == "swahili":
        detailed_help = """
        Tafuta matetemeko ya ardhi ya ukubwa maalum yaliyotokea katika eneo fulani.
        """
        print(detailed_help)

    elif user_choice in ['7', 'search by period of occurrence'] and language == "swahili":
        detailed_help = """
        Tafuta matetemeko ya ardhi yaliyotokea katika kipindi fulani. Hii ni utafutaji mpana wa kuonyesha matetemeko yaliyotokea kwa tarehe, muda au tarehe na muda maalum kwenye seti ya data yote.
        """
        print(detailed_help)

    elif user_choice in ['8', 'get report showing statistics on all earthquakes'] and language == "swahili":
        detailed_help = """
        Hii itakuwezesha kuona takwimu za data zote zilizopo kwenye seti yetu.
        Takwimu hizi ni za jumla kutoka 2005 hadi 2025.
        """
        print(detailed_help)

    elif user_choice in ['9', 'get report showing statistics on earthquakes of a specific place and time'] and language == "swahili":
        detailed_help = """
        Hii itatoa takwimu za matetemeko ya ardhi yaliyotokea kwa kipindi maalum katika eneo fulani. Huu ni utafutaji wa kina zaidi.
        """
        print(detailed_help)

    elif user_choice in ['10', 'get report showing statistics on weather occurrences'] and language == "swahili":
        detailed_help = """
        Hii itakupa takwimu za hali ya hewa za data zote kwa kipindi fulani.
        """
        print(detailed_help)

    elif user_choice in ['11', 'get report showing statistics on earthquakes and weather occurrences of a specific place and time']:
        detailed_help = """
        Hii itakupa takwimu za matetemeko ya ardhi na hali ya hewa kwa kipindi kilichochaguliwa kwa eneo fulani.
        """
        print(detailed_help)

    elif user_choice in ['12', 'view earthquake data on a map'] and language == "swahili":
        detailed_help = """
        Tazama data za matetemeko ya ardhi kwenye ramani kwenye kivinjari chako kwa eneo kwa kipindi fulani.
        """
        print(detailed_help)

    elif user_choice in ['13', 'view earthquake and weather data on a map'] and language == "swahili":
        detailed_help = """
        Tazama data za matetemeko ya ardhi na hali ya hewa kwa kipindi fulani na eneo maalum.
        """
        print(detailed_help)

def generate_response(input_text):
    
    user_input_lower = input_text.lower()

    if input_text.lower() == "help":
        return show_help()
    
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
    
    if input_text.lower().strip() in view_weather_report:
        start_date_input = input("Enter the start date (YYYY-MM-DD): ")
        end_date_input = input("Enter the end date (YYYY-MM-DD): ")

        if start_date_input and end_date_input:
               
                entries = getatomdata("user.atomfiles",start_date_input,end_date_input,"displayfiles\\earthquake_data.json")
        if entries:
               
                weather = display_weather_by_date_range("weather_userdata", start_date_input, end_date_input, "displayfiles\\filtered_weather.json")
        if weather:
            
                display = merge_json_files(entries, weather, "displayfiles\\merged_data.json")
        if display:
                json_ffile ="displayfiles\\merged_data.json"   
                data = load_data_from_file(json_ffile)  # Replace with your actual file path
                stats = analyze_data(data)
                write_stats_to_file(stats)
        return "Activity displayed to text file"
    
    if input_text.lower().strip() in view_a_report_of_earth_quakes_and_weather_of_a_specific_place_and_time:
        start_date_input = input("Enter the start date (YYYY-MM-DD): ")
        end_date_input = input("Enter the end date (YYYY-MM-DD): ")
        if start_date_input and end_date_input:
               user_place = input("Enter the place (e.g., California): ")
        if user_place:        
                entries = singleplaceatom("user.atomfiles",start_date_input,end_date_input,user_place,"displayfiles\\earthquake_data.json")
        if entries:
                weather = display_weather_by_date_range("weather_userdata", start_date_input, end_date_input, "displayfiles\\filtered_weather.json")
        if weather:
                display = merge_json_files(entries, weather, "displayfiles\\merged_data.json")
        if display:
                json_ffile ="displayfiles\\merged_data.json"   
                data = generate_report(json_ffile)  # Replace with your actual file path
        return "Activity displayed to text file"

    if input_text.lower().strip() in view_all_earthquakes_report:
        # Assuming you need to get the namespace from the XML or relevant data
        calculate_statistics('user.atomfiles')  # Pass the folder path and namespace to calculate_statistics
        return "Earthquake statistics report has been generated. Check the 'displayfiles/user_view_screen.txt' file for details."
    
    if input_text.lower().strip() in view_earthquake_report_of_place:
        start_date_input = input("Enter the start date (YYYY-MM-DD): ")
        end_date_input = input("Enter the end date (YYYY-MM-DD): ")
        if start_date_input and end_date_input:
               user_place = input("Enter the place (e.g., California): ")
        if user_place:    
            calculate_statisticsofplace('user.atomfiles',start_date_input,end_date_input,user_place)  # Pass the folder path and namespace to calculate_statistics
        return "Earthquake statistics report has been generated. Check the 'displayfiles/user_view_screen.txt' file for details."

    if user_input_lower in predefined_responses:
        return predefined_responses[user_input_lower]
    
    if any(trigger in input_text.lower() for trigger in view_seismic_triggers):
        print("You can choose from the following options:")
        print("1. Search by Date Range")
        print("2. Search by Time Range")
        print("3. Search by Both Date and Time Range")
        search_type = input("Enter your choice (1/2/3): ").strip()

        folder_path = 'user.atomfiles'
        date_range_start, date_range_end, time_range_start, time_range_end = None, None, None, None

        if search_type == '1':
            date_range_start = (input("Enter start date (YYYY-MM-DD): "))
            date_range_end =(input("Enter end date (YYYY-MM-DD): "))
            place = input("Enter the place (e.g., California): ")
            search_seismic_activityofplacebydate(folder_path, date_range_start, date_range_end,place)
            file_path, count = search_seismic_activityofplacebydate(folder_path, date_range_start, date_range_end,place)
        elif search_type == '2':
            time_range_start =(input("Enter start time (HH:MM): "))
            time_range_end = (input("Enter end time (HH:MM): "))
            place = input("Enter the place (e.g., California): ")
            search_seismic_activityofplacebytime(folder_path, time_range_start, time_range_end,place)
            file_path, count = search_seismic_activityofplacebytime(folder_path, time_range_start, time_range_end,place)
        elif search_type == '3':
            date_range_start = (input("Enter start date (YYYY-MM-DD): "))
            date_range_end = (input("Enter end date (YYYY-MM-DD): "))
            time_rangest = (input("Enter start time (HH:MM): "))
            timerangeed = (input("Enter end time (HH:MM): "))
            place = input("Enter the place (e.g., California): ")
            search_seismic_activityofplacebytimeanddate(folder_path, date_range_start, date_range_end,place,time_rangest,timerangeed)
            file_path, count = search_seismic_activityofplacebytimeanddate(folder_path, date_range_start, date_range_end,place,time_rangest,timerangeed)
        else:
            return "Invalid choice. Please enter 1, 2, or 3."

        return f"Search completed. {count} matching entries found. Results saved in: {file_path}"
    
    if input_text.lower().strip() in view_magnitude_by_size:
        search_type = input("Enter the magnitude size or range (e.g., 1.5, >2, <=3.0): ").strip()
        file_path, count = search_magnitude('user.atomfiles', search_type)
        print(f"Magnitude search results saved to {file_path}")
        return f"Magnitude search completed. Data saved in: {file_path}"
    
    if input_text.lower().strip() in view_magnitude_by_sizeplace:
        statdateinput = input("Enter the start date (YYYY-MM-DD): ")
        enddateinput = input("Enter the end date (YYYY-MM-DD): ")
        if start_date_input and end_date_input:
               user_place1 = input("Enter the place (e.g., California): ")
        if user_place:  
            search_type = input("Enter the magnitude size or range (e.g., 1.5, >2, <=3.0): ").strip()
        file_path, count = search_magnitudeplace('user.atomfiles', search_type,user_place1,statdateinput,enddateinput)
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
   
    if input_text.lower().strip() in location_triggers:
    # Use the show_locations function to get the formatted list of locations
            locations_display = extract_all_locations("user.atomfiles", "displayfiles\\view_all_locaations.txt")
            print(f"\nBIBA: {locations_display}\n")

    if any(keyword in input_text.lower() for keyword in search_keywords):
        search_place = input("Enter the place (city) to search for: ").strip()
        file_path, count = search_atom_files('user.atomfiles', search_place)
        return f"Search results saved to {file_path}. Number of matching entries: {count}"
    

    if any(trigger in input_text.lower() for trigger in view_mapofearthquakesandweather_triggers):
        start_date_input = input("Enter the start date (YYYY-MM-DD): ")
        end_date_input = input("Enter the end date (YYYY-MM-DD): ")

        if start_date_input and end_date_input:
            user_place = input("Enter the place (e.g., California): ")
            if user_place:
                entries = split_and_filter_by_date("user.atomfiles", start_date_input, end_date_input, user_place, "displayfiles\\earthquake_data.json")
            if entries:
                weather = display_weather_by_date_range("weather_userdata", start_date_input, end_date_input, "displayfiles\\filtered_weather.json")
            if weather:
                display = merge_json_files(entries, weather, "displayfiles\\merged_data.json")
                
            if display:
                # Save merged data to a file
                merged_data_file = "displayfiles\\merged_data.json"
                # Now, pass the path to the merged data file
                map_obj = visualize_earthquake_weather_on_map(merged_data_file, output_map="displayfiles\\weather_earthquakes_on_map.html")
                map_file = "weather_map_with_icons.html"
                return f"Map has been saved. Open the following link to view it: file://{os.path.abspath(map_file)}"
            else:
                return f"No entries found for '{user_place}' within {start_date_input} to {end_date_input}."
        else:
            return "Invalid date range input."


    if input_text.lower().strip() in view_mapofearthquakes_triggers:
        start_date_input = input("Enter the start date (YYYY-MM-DD): ")
        end_date_input = input("Enter the end date (YYYY-MM-DD): ")

        if start_date_input and end_date_input:
        
        
            user_place = input("Enter the place (e.g., California): ")
            if user_place:
                entries = split_and_filter_by_date("user.atomfiles", start_date_input, end_date_input, user_place, "displayfiles//earthquake_data.json")

            if entries:
                data_file ="displayfiles//earthquake_data.json"
                map_obj = plot_on_map(data_file, output_map="displayfiles\\earthquake.view.html")
                map_file = "displayfiles\\earthquake.view.html"
                return f"Map has been saved. Open the following link to view it: file://{os.path.abspath(map_file)}"
            else:
                return f"No entries found for '{user_place}' within {start_date_input} to {end_date_input}."
        else:
            return "Invalid date range input."
   

    # Generate a response with the following parameters:
    outputs = model.generate(
        inputs, 
        attention_mask=attention_mask, 
        max_length=10000,  # Increase the response length to allow more details
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

def translate_text_deep_translator(text):
    translations = {}
    translations['Spanish'] = GoogleTranslator(source='en', target='es').translate(text)
    translations['French'] = GoogleTranslator(source='en', target='fr').translate(text)
    translations['Swahili'] = GoogleTranslator(source='en', target='sw').translate(text)
    
    # Format the translations
    result = f"Spanish: {translations['Spanish']}\nFrench: {translations['French']}\nSwahili: {translations['Swahili']}"
    return result

def translate_text(text):
    # Randomly choose whether to use deep-translator or googletrans
    import random
    if random.choice([True, False]):
        return translate_text_deep_translator(text)
    else:
        return translate_text_deep_translator(text)

def get_current_date():
    current_date = datetime.now()
    return f"Today's date is {current_date.strftime('%A, %B %d, %Y')}."

def get_current_time():
    current_time = datetime.now()
    return f"The current time is {current_time.strftime('%I:%M %p')}."

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