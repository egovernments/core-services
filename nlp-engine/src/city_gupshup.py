from flask import Flask, jsonify,request
import requests
from  city_extract import *
from flask_ngrok import run_with_ngrok
import json
from googletrans import Translator

translator= Translator()


city_gupshup=Flask(__name__)
run_with_ngrok(city_gupshup)

cacheCities={}

cacheFinal={}
source={}


welcomeMessage= "Welcome to the *DIGIT* platform ! Please type in your city name.\n"


@city_gupshup.route('/',methods=['POST'])
def reply():
    requestData=request.get_json()
    inp=requestData["payload"]["payload"]["text"]

    destination=requestData["payload"]["source"]

    default = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=Please%20mention%20a%20category&src.name=LocalitySearch'

    payload=default
    inp=inp.lower()
    inp_2=inp

    if (inp=="hi" or inp=="hello" or inp=="नमस्ते" or inp=="नमस्कार" or inp=="ਹਾਇ" or inp=="ਸਤ ਸ੍ਰੀ ਅਕਾਲ"):
        inp=translator.translate(inp,dest='en')
        src=inp.src
        inp=inp.text
        inp=inp.lower()
        source["src"]=src

    if (inp!="hi" and inp!="hello"):
        inp=inp_2

    url_2 = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
      'Cache-Control': 'no-cache',
      'Content-Type': 'application/x-www-form-urlencoded',
      'apikey': '443fbc250a744864c880cc6d373692cb',
      'cache-control': 'no-cache'
                      }
    if(inp=="hi" or inp=="hello" or inp=="mseva"):
        cacheCities.clear()
        cacheFinal.clear()
        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate(welcomeMessage,dest=source["src"]).text+ "&src.name=LocalitySearch"
        

    elif (inp>="1" and inp<="9" and int(inp)>=1 and int(inp)<=9):
        if (int(inp)>len(cacheCities) or int(inp)<1):
            
            k=payload.index("&message")
            payload=payload[0:k]+"&message="+translator.translate("Please enter a valid selection",dest=source["src"]).text+translator.translate("Type 'mseva' to return back to the main menu.",dest=source["src"]).text+ "&src.name=LocalitySearch"

        else:
           
            city= cacheCities[int(inp)]
            k=payload.index("&message")
            payload=payload[0:k]+"&message=*"+translator.translate((city[0].upper()+city[1:].lower()),dest=source["src"]).text+"* \n"+ translator.translate("Type 'mseva' to return back to the main menu.",dest=source["src"]).text+"&src.name=LocalitySearch"
            
            cacheCities.clear()
            

    else:
        if (len(cacheCities)==0):
            m={"input_city":inp,"input_lang":"hindi"}
            response=requests.post(url="http://127.0.0.1:8080/nlp-engine/fuzzy/city", data=json.dumps(m), headers={"Content-Type": "application/json"})
            cities=json.loads(response.text)["city_detected"]
            count=1
            cityList=translator.translate("Did you mean any one of the following cities ? Enter the number of your city.",dest=source["src"]).text+'\n'
            
            for i in cities:
                cacheCities[count]=i[3:]
                cityList+=(str(count)+'.')
                cityList+=translator.translate((i[3].upper()+i[4:].lower()), dest=source["src"]).text+'\n'
                count+=1

            cityList+='\n'
            cityList+=translator.translate("Type 'mseva' to return back to the main menu.",dest=source["src"]).text

            k=payload.index("&message")
            payload=payload[0:k]+"&message="+cityList+"&src.name=LocalitySearch"

       

    payload=payload.encode('utf-8')
            
    response = requests.request("POST", url_2, headers=headers, data = payload)

    return ""

city_gupshup.run()
