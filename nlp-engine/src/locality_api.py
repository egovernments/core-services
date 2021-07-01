from flask import Flask, jsonify, request, send_file
import json
import requests
from fuzzywuzzy import fuzz
from city_extract import *
import string

punct= string.punctuation

locality_api = Flask(__name__)

#locality_api.config['APPLICATION_ROOT']='/nlp-engine'
@locality_api.route('/nlp-engine/fuzzy/city', methods=['POST'])
def reply():
    request_data=request.get_json()
    inp= request_data['input_city']
    lang=request_data['input_lang']

    k= find_city(inp)
    response=dict()
    response['city_detected']= k[0]
    response['match']= k[1]

    return jsonify(response)


@locality_api.route('/nlp-engine/fuzzy/locality',methods=['POST'])
def reply_2():
    request_data=request.get_json()
    city=request_data['city']
    locality=request_data['locality']
    

    payload="{\r\n\r\n   \"apiId\": \"asset-services\",\r\n   \"ver\": null,\r\n   \"ts\": null,\r\n   \"action\": null,\r\n   \"did\": null,\r\n   \"key\": null,\r\n   \"msgId\": \"search with from and to values\",\r\n   \"authToken\": \"{{qaAuth}}}\",\r\n   \"correlationId\": null,\r\n   \"userInfo\": {\r\n     \"id\": \"1\",\r\n     \"userName\": null,\r\n     \"name\": null,\r\n     \"type\": null,\r\n     \"mobileNumber\": null,\r\n     \"emailId\": null,\r\n     \"roles\": null\r\n   }\r\n \r\n}"

    url="https://qa.digit.org/egov-location/location/v11/boundarys/_search?tenantId="+str(city.lower())

    response=requests.request("POST",url, data=payload, headers={"Content-Type": "application/json"})

    
    localities=list()
    tenant_boundaries=json.loads(response.text)["TenantBoundary"] 

    for tenant in tenant_boundaries:
        for entry in tenant["boundary"]:
            for sub_entry in entry["children"]:
                for grand_entry in sub_entry["children"]:
                    for final in grand_entry["children"]:
                        
                        k=final["name"]
                        k=k.lower()
                        median=""
                        for character in k:
                            if character!=' ':
                                median+=character
                        k=median

                        median=""
                        locality= [i for i in locality if i not in punct]
                        locality= ''.join(locality)
                        locality=locality.lower()
                        
                        for character in locality:
                            if character!=' ':
                                median+=character
                        locality=median
                        locality=locality.lower()

                        if locality==k[0:len(locality)]:
                            a=list()
                            a.append(100)
                            b=dict()
                            b["code"]=final["code"]
                            b["name"]=final["name"]
                            checker=list()
                            for i in localities:
                                checker.append(i[1]["name"])
                            a.append(b)
                            if b["name"] not in checker:
                                localities.append(a)
                            
                        
                        if fuzz.ratio(locality.lower(),k)>=50:
                            a=list()
                            a.append(fuzz.ratio(locality,k))
                            b=dict()
                            b["code"]=final["code"]
                            b["name"]=final["name"]
                            checker=list()
                            for i in localities:
                                checker.append(i[1]["name"])
                            a.append(b)
                            if b["name"] not in checker:
                                localities.append(a)
    
    
    localities.sort(key=lambda x:x[0] ,reverse=False)
    predictions=list()

    for i in range(min(5,len(localities))):
        predictions.append(localities[len(localities)-1-i][1])
    
    
    
    g={"predictions":predictions}
    return g
    
    

locality_api.run(host='0.0.0.0',port=8080)