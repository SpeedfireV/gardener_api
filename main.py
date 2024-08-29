import os
import uuid

import dotenv
import firebase_admin
from dotenv import load_dotenv
from openai import OpenAI
import requests
import json

from firebase_admin import credentials, firestore

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

response = requests.get("https://world-crops.com/tomato/").content
start = str(response).find(".entry-content")
end = str(response).find(".entry-content .clear")
print(str(response)[start:end])

cred = credentials.Certificate('gardener-ca78c-firebase-adminsdk-2hjca-4407dfeffe.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()

messages = [{"role": "system", "content": "You are an intelligent gardening assistant."},
             {
                 "role": "system", "content": "You are supposed to answer ONLY with json filed structurized as following with your custom values:\n"
                                              "{"
                                              "'airHumidity': { max[float]: 100, min[float]: 100 }, // Define perfect min and max air humidity (float representing percent) for a plant"
                                              "'countries': {'pl'[bool]: true, 'US'[bool]: true, ...}, // List at least few big nations including Poland in which the plant can and can't be planted"
                                              "'description'[string]: 'That plant is a delicious cabbage...,' // Describe plant, maybe give some fun facts etc."
                                              "'growingDifficulty'[int]: 4, // Give number from 1 to 6 defining how hard it is to grow that plant"
                                              "'growingTime': { max[float]: 7, min[float]: 5 } // Define the time (in weeks) how long the plant grows. If the plant is grown in less time than a week define for example 0.2 for a day (0.2*7=1.4 => floor(1.4) = 1)"
                                              "'howToPlant'[string]: 'Plant seeds ¼-½ inch deep, 2-3 weeks before the last frost in the spring. Thin seedlings...', // Describe how to plant, grow and harvest the plant."
                                              "'latin'[string]: 'Brassica oleracea', // Latin name of a plant"
                                              "'name'[string]: 'Cabbage', // English name of a plant"
                                              "'neededLight'[int]: 3, // Number on scale 1-6 how much light the plant needs where 1 is nearly no at all and 6 is a lot of light."
                                              "'neededWater'[int]: 5, // Number on scale 1-6 how much water the plant needs where 1 is nearly no at all and 6 is a lot of water."
                                              "'optimalTemp': { max[int]: 35, min[int]: 26 }, //  Define perfect min and max temp (int representing a temperature in celsius scale) for a plant"
                                              "'seasons'[list]: ['planting', 'resting', 'growing', 'harvesting'... (totally 24 records)] // Define list of exactly 24 string each string represents half of a month so first record is the first half o january, second is second half, third is a first half of february etc. You have to fill the list with 24 strings each string can be of following type: 'planting' for the moment in which plant should be planted, 'growing': for the time the plant is growing, 'harvesting': for the time in which plant is harvested, 'resting': for the time that the plant shouldn't be planted, harvested or grown."
                                              "'soilDetails'[string]: 'Cabbage may be grown on a variety of soils but it does best on a well- drained, loam soil well supplied with organic matter...' // Define soil details for a plant growth."
                                              "'type'[string]: 'fruit' // Define type of a plant. It can be either 'vegetable', 'fruit', 'herb' or 'all' for others."
                                              "}",
             },
             {
                 "role": "user", "content": "Give me a json of strawberry."
             }
             ]
doc_ref = db.collection("plants").document(str(uuid.uuid4()))
chat = client.chat.completions.create(
    model='gpt-4o-mini', messages=messages
)
content = chat.choices[0].message.content
content = content[content.find("{"):content.rfind("}")+1]
print(content)
print(chat.choices[0].message.content)
doc_ref.set(json.loads(content))
