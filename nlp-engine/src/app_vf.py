from main3 import *
from flask import Flask, jsonify, request, send_file
from entity_recognition import *
import requests
from googletrans import Translator
from fuzzywuzzy import fuzz

from city_extract import find_city
import time

import speech_recognition as sr
from os import path
from pydub import AudioSegment

translator= Translator()
languages={
    'english':'en',
    'hindi':'hi',
    'marathi': 'mr', 'gujarati':'gu', 'punjabi':'pa',  'kannada':'kn', 'tamil':'ta', 'malayalam': 'ml', 'telugu':'te', 'bengali': 'bn', 'bangla': 'bn'

    }
def close_to(entry):
    entry=entry.lower()
    for i in languages.keys():
        if fuzz.ratio(i,entry)>=75:
            return i
    return 'english'

    

app_vf = Flask(__name__)

@app_vf.route('/', methods=['POST'])
def reply():
    requestData=request.get_json()
    inp=""

    if requestData["payload"]["type"]=="audio" :
        audioUrl=requestData["payload"]["payload"]["url"]
        getAudioFile=requests.get(audioUrl, allow_redirects=True)
        open('voice_message.ogg', 'wb').write(getAudioFile.content)
        sound=AudioSegment.from_ogg("voice_message.ogg")
        
        sound.export("voice_message.wav", format="wav")

        AUDIO_FILE = "voice_message.wav"
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)
            inp=r.recognize_google(audio)
    else:
        inp=requestData["payload"]["payload"]["text"]

    destination=requestData["payload"]["source"]

    default = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=Please%20mention%20a%20category&src.name=chatbotpayment'

    payload= default
    
    inp=inp.lower()
    

    url = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
      'Cache-Control': 'no-cache',
      'Content-Type': 'application/x-www-form-urlencoded',
      'apikey': '37cef3c8bf164df7cdc0a36eae94beec',
      'cache-control': 'no-cache'
                      }

    if len(inp.split())==1 and inp!="hi" and inp!="hello":
        answer=find_city(inp)[0].upper()
        answer=answer[0]+answer[1:].lower()

        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate("We have detected *"+answer+"* as your city.",dest='en').text+ "&src.name=chatbotpayment"
        response = requests.request("POST", url, headers=headers, data = payload)

        payload=payload[0:k]+"&message="+translator.translate("If your city is detected correctly, you can continue with your bill/receipt queries.\n Else, kindly type your city name again.\n ",dest='en').text+ "&src.name=chatbotpayment"
        response = requests.request("POST", url, headers=headers, data = payload)
        return ""
        

    inp=translator.translate(inp,dest='en')
    sourceLanguage=inp.src
    inp=inp.text
    result= process(inp)
    
    resultArray=result.split()

    if resultArray[0]=="Welcome" :
        
        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate(result,dest=sourceLanguage).text+ "&src.name=chatbotpayment"
        response = requests.request("POST", url, headers=headers, data = payload)
        
        
        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate("Please enter your city name\n",dest=sourceLanguage).text+ "&src.name=chatbotpayment"
  
    elif c[0]=='Showing':
        if 'water' in resultArray:
            payload = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=%7B%22type%22%3A%22file%22%2C%22url%22%3A%22https%3A//www.buildquickbots.com/whatsapp/media/sample/pdf/sample01.pdf%22%2C%22caption%22%3A%22%22%2C%22filename%22%3A%22Water_Sewerage_receipts.pdf%22%7D&src.name=chatbotpayment'

        elif 'trade' in resultArray:
            payload = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=%7B%22type%22%3A%22file%22%2C%22url%22%3A%22https%3A//www.buildquickbots.com/whatsapp/media/sample/pdf/sample01.pdf%22%2C%22caption%22%3A%22%22%2C%22filename%22%3A%22Trade_license_receipts.pdf%22%7D&src.name=chatbotpayment'

        elif 'property' in resultArray:
            payload = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=%7B%22type%22%3A%22file%22%2C%22url%22%3A%22https%3A//www.buildquickbots.com/whatsapp/media/sample/pdf/sample01.pdf%22%2C%22caption%22%3A%22%22%2C%22filename%22%3A%22Property_Tax_receipts.pdf%22%7D&src.name=chatbotpayment'

        else:
            
            k=payload.index("&message")
            payload=payload[0:k]+"&message="+translator.translate(result,dest=sourceLanguage).text+ "&src.name=chatbotpayment" 

    elif resultArray[0]=='Visit':
        
        
        
        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate(result,dest=sourceLanguage).text+ "&src.name=chatbotpayment"

    elif resultArray[0]=='You':

        if 'water' in resultArray:
            payload = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=%7B%22type%22%3A%22file%22%2C%22url%22%3A%22https%3A//www.buildquickbots.com/whatsapp/media/sample/pdf/sample01.pdf%22%2C%22caption%22%3A%22%22%2C%22filename%22%3A%22Water_Sewerage_bills.pdf%22%7D&src.name=chatbotpayment'

        elif 'trade' in resultArray:
            payload = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=%7B%22type%22%3A%22file%22%2C%22url%22%3A%22https%3A//www.buildquickbots.com/whatsapp/media/sample/pdf/sample01.pdf%22%2C%22caption%22%3A%22%22%2C%22filename%22%3A%22Trade_license_bills.pdf%22%7D&src.name=chatbotpayment'

        elif 'property' in resultArray:
            payload = 'channel=whatsapp&source=917834811114&destination='+destination+'&message=%7B%22type%22%3A%22file%22%2C%22url%22%3A%22https%3A//www.buildquickbots.com/whatsapp/media/sample/pdf/sample01.pdf%22%2C%22caption%22%3A%22%22%2C%22filename%22%3A%22Property_Tax_bills.pdf%22%7D&src.name=chatbotpayment'

       
        response = requests.request("POST", url, headers=headers, data = payload)

        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate(result,dest=sourceLanguage).text+ "&src.name=chatbotpayment"

    else:
     
        k=payload.index("&message")
        payload=payload[0:k]+"&message="+translator.translate(result,dest=sourceLanguage).text+ "&src.name=chatbotpayment"
    
         
    
    if resultArray[0]!="Showing":
        payload=payload.encode('utf-8')

    response = requests.request("POST", url, headers=headers, data = payload)

    return ""

app_vf.run()
