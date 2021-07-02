from flask import Flask, jsonify, request
import requests
from city_extract import *
from flask_ngrok import run_with_ngrok
import json
import speech_recognition as sr
from pydub import AudioSegment

city_audio=Flask(__name__)
run_with_ngrok(city_audio)

cacheCities={}
cacheFinal={}
cacheLocalities={}
source={}

welcomeMessage= "Welcome to the *DIGIT* platform ! Please type in your city name.\n"

@city_audio.route('/',methods=['POST'])
def reply():
    destination="919619367055"
    payload='channel=whatsapp&source=917834811114&destination=919619367055&message=Please%20mention%20a%20category&src.name=LocalitySearch'
    url_2 = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
      'Cache-Control': 'no-cache',
      'Content-Type': 'application/x-www-form-urlencoded',
      'apikey': '443fbc250a744864c880cc6d373692cb',
      'cache-control': 'no-cache'
                      }
    
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

    

    inp=inp.lower()
    

    

    if(inp=="hi" or inp=="hello" or inp=="mseva"):
        cacheCities.clear()
        cacheFinal.clear()
        
        cacheLocalities.clear()
        k=payload.index("&message")
        payload=payload[0:k]+"&message="+welcomeMessage+ "&src.name=LocalitySearch"
        

    elif (inp>="1" and inp<="9" and int(inp)>=1 and int(inp)<=9):
        
        if (int(inp)>len(cacheCities) or int(inp)<1):
            k=payload.index("&message")
            payload=payload[0:k]+"&message="+"Please enter a valid selection\n"+"Type 'mseva' to return back to the main menu."+ "&src.name=LocalitySearch"

        else:
            
            
            if (len(cacheLocalities)!=0):
                
                
                locality=cacheLocalities[int(inp)]
                
                k=payload.index("&message")
                payload=payload[0:k]+"&message="+"Locality detected--> "+locality.upper()+ "&src.name=LocalitySearch"
                cacheCities.clear()
                cacheFinal.clear()
                cacheLocalities.clear()
                
                
            else:
                city= cacheCities[int(inp)]
                k=payload.index("&message")
                payload=payload[0:k]+"&message=*"+(city[0].upper()+city[1:].lower())+"* \n"+ "Type the name of your locality\n"+"Type 'mseva' to return back to the main menu."+"&src.name=LocalitySearch"
                cacheFinal["city"]=city
                
            

    else:
        if (len(cacheCities)==0):
            m={"input_city":inp,"input_lang":"hindi"}
            response=requests.post(url="http://127.0.0.1:8080/nlp-engine/fuzzy/city", data=json.dumps(m), headers={"Content-Type": "application/json"})
            cities=json.loads(response.text)["city_detected"]
            count=1
            cityList="Did you mean any one of the following cities ? Enter the number of your city."+'\n'
            
            for i in cities:
                cacheCities[count]=i[3:]
                cityList+=(str(count)+'.')
                cityList+=(i[3].upper()+i[4:].lower())+'\n'
                count+=1

            cityList+='\n'
            cityList+="Type 'mseva' to return back to the main menu."

            k=payload.index("&message")
            payload=payload[0:k]+"&message="+cityList+"&src.name=LocalitySearch"
            
       
        else:
            m={"city":cacheFinal["city"],"locality":inp}
            response=requests.post(url="http://127.0.0.1:8080/nlp-engine/fuzzy/locality", data=json.dumps(m), headers={"Content-Type": "application/json"})
            localities=json.loads(response.text)["predictions"]
            count=1
            localList="Did you mean any one of the following localities ? Enter the number of your locality.\n"

            for i in localities:
                cacheLocalities[count]=i["name"]
                localList+=(str(count)+'.'+i["code"]+' . '+i["name"]+'\n')
                count+=1

            k=payload.index("&message")
            payload=payload[0:k]+"&message="+localList+"&src.name=LocalitySearch"  
        
       

    payload=payload.encode('utf-8')
            
    response = requests.request("POST", url_2, headers=headers, data = payload)

    return ""

city_audio.run()
