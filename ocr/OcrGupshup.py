from flask import Flask, jsonify, request
import requests
from flask_ngrok import run_with_ngrok
from SkewTest import *
import json
from Config import *

OcrGupshup= Flask(__name__)
run_with_ngrok(OcrGupshup)

@OcrGupshup.route('/', methods=['POST'])
def reply():
    requestData=request.get_json()

    welcomeMessage= WELCOME_MESSAGE

    destination=requestData["payload"]["source"]

    default = PREFIX+destination+CATEGORY+SRC_NAME

    payload=default

    url_2 = GUPSHUP_URL
    headers = {
      'Cache-Control': 'no-cache',
      'Content-Type': 'application/x-www-form-urlencoded',
      'apikey': '443fbc250a744864c880cc6d373692cb',
      'cache-control': 'no-cache'
      }

    if requestData["payload"]["type"]=="image":
        imageUrl= requestData["payload"]["payload"]["url"]
        imageFile=requests.get(imageUrl, allow_redirects=True)
        open('gupshup_test.jpg', 'wb').write(imageFile.content)
        k=payload.index(MESSAGE_TOKEN)
        payload=payload[0:k]+MESSAGE_TOKEN+ocr("gupshup_test.jpg")+ SRC_NAME
        response = requests.request("POST", url_2, headers=headers, data = payload)
        k=payload.index(MESSAGE_TOKEN)
        payload=payload[0:k]+MESSAGE_TOKEN+MSEVA+ SRC_NAME
        response = requests.request("POST", url_2, headers=headers, data = payload)

    else:
        k=payload.index(MESSAGE_TOKEN)
        payload=payload[0:k]+MESSAGE_TOKEN+welcomeMessage+ SRC_NAME
        response = requests.request("POST", url_2, headers=headers, data = payload)
        


    

    return ""

OcrGupshup.run()
        
        
