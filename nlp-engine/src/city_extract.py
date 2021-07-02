import string
import nltk
from fuzzywuzzy import fuzz
from googletrans import Translator
from nltk.util import ngrams
import requests
import json

translator= Translator()

punctuations= string.punctuation

cityNames= requests.get('https://raw.githubusercontent.com/egovernments/egov-mdms-data/DEV/data/pb/Chatbot/CityNames.json')
cityLocale= requests.get('https://raw.githubusercontent.com/egovernments/egov-mdms-data/DEV/data/pb/Chatbot/CityLocaleMasterData.json')
resultName= json.loads(cityNames.text)
resultLocale= json.loads(cityLocale.text)

cities=resultName["CityNames"][0]["cities"]
citiesHindi=resultName["CityNames"][1]["cities"]
cityPunjabi=resultName["CityNames"][2]["cities"]

master= resultLocale["CityLocaleMasterData"]

for i in range(0,len(cities)):
    cities[i]= cities[i].lower()


cities=cities+citiesHindi+cityPunjabi

def find_city(city):
    city= [i for i in city if i not in punctuations]
    city= ''.join(city)
    city=city.lower()

    maxRatio=0
    cityResult=[[0,"Please try again"]]
    
    
    for j in master:

        if (city == j["cityName"].lower()[0:len(city)]):
            cityResult.append([100,j["tenantId"]])
            
        elif fuzz.ratio(city,j["cityName"].lower())>=50 :
            maxRatio=max(maxRatio,fuzz.ratio(city,j["cityName"].lower()))
            cityResult.append([fuzz.ratio(city,j["cityName"].lower()),j["tenantId"]])
            
                
                
    exactMatch='false'
    if maxRatio==100:
        exactMatch='true'
    k= sorted(cityResult)
   

    
    finalAnswer=list()
    for i in range(min(5,len(k))):
        finalAnswer.append(k[len(k)-1-i][1])
    
    return (finalAnswer,maxRatio,exactMatch)
    
