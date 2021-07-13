import cv2
import numpy as np
import pytesseract
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import re
from fuzzywuzzy import fuzz
import imutils
from Config import *



#function for displaying image on pyplot
def display(img, cmap='gray'):
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)
    ax.imshow(img,cmap='gray')

    
# function to check whether a given string qualifies as a valid name
def is_name(s):
    counter=0
    for i in s:
        if ((i>='a' and i<='z') or (i>='A' and i<='Z')):
            counter+=1
    if counter>(len(s)/2):
        return True
    return False


def ocr(img):
    img = cv2.imread(img)
    
    #non-local means denoising on the colored image
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15)

    #conversion to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #Thresholding --> Otsu's binarization
    th, threshed = cv2.threshold(gray,0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU )

    #find rotation angle using projection profile method
    coords = np.column_stack(np.where(threshed > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -1*(90 + angle)
    # otherwise, just take the inverse of the angle to make
    # it positive
    else:
        angle = -1*angle
        
    #rotate the image in opposite direction
    threshed= imutils.rotate(threshed,angle)
    
    #information extraction from the cleaned image
    text2 = pytesseract.image_to_string(threshed, lang="eng")
    result=list()

    for i in text2.split('\n'):
        if i!='' and i!=' ':
            result.append(i)

    
    name=""
    category=""
    id_no=""
    dob=""

    flag=0
    dob_flag=0

    gender_ratio=0
    gender=""

    doi=""
    sdw= ""
    father=""

    for i in result:
        
        #Regex for id number [Aadhar]
        if bool(re.search(AADHAR_FORMAT, i))==True:
            category=AADHAR
            id_no = re.search(AADHAR_FORMAT, i)[0]
            
        #Regex for id number [PAN]
        elif bool(re.search(PAN_FORMAT, i))==True:
            category=PAN
            id_no=re.search(PAN_FORMAT, i)[0]

        #Regex for id number [Driving license]
        elif NUMBER in i.lower():
            number_start=i.lower().find(NUMBER)
            id_no = i[number_start+6:len(i)]
            category= DRIVING_LICENSE
            
        #Regex for date of birth
        if DOB in i.lower():
            dob_start=i.lower().find(DOB)
            if dob_flag==0:
                dob_flag=1
                dob=i[dob_start+3:len(i)]

        elif bool(re.search(DOB_FORMAT,i))==True and dob_flag==0:
            dob=re.search(DOB_FINAL,i)[0]
            
            
        #Regex for name [PAN]
        if ((i.upper() ==i) and (GOVT not in i) and  (INCOME not in i) and (TAX not in i) and (DEPARTMENT not in i) and (GOVERNMENT not in i) and (INDIA not in i) and (DEPT not in i)):
            if flag==0 and is_name(i):
                temp= i
                for j in temp:
                    if ((j>='A' and j<='Z') or j==' '):
                        name+=j
                flag=1
            elif flag==1 and is_name(i):
                temp= i
                for j in temp:
                    if ((j>='A' and j<='Z') or j==' '):
                        father+=j
                flag=2
                
        #Regex for name [Driving license]
        elif NAME in i.lower():
            name_start=i.lower().find(NAME)
            name=i[name_start+4:len(i)]
            if is_name(name):
                flag=1
                
        #Regex for name [Aadhar]
        else:
            temp_2=i.split()
            for j in range(len(temp_2)):
                t=temp_2[j]
                t=t[0].upper()+t[1:].lower()
                temp_2[j]=t
            temp_2=" ".join(temp_2)
            if i==temp_2 and is_name(i) and flag==0 :
                name=i
                flag=1
            
        #Regex for date of issue
        if ISSUE_DATE in i.lower():
            doi_start=i.lower().find(ISSUE_DATE)
            doi=i[doi_start+10 :len(i)]
            
        #Regex for s/d/w
        if SDW in i.lower():
            sdw_start=i.lower().find(SDW)
            sdw=i[sdw_start+9:len(i)]
            
        #Regex for gender
        for j in i.split():
            if fuzz.ratio(j.lower(),MALE)>=60 and fuzz.ratio(j.lower(),MALE)>gender_ratio:
                gender_ratio=fuzz.ratio(j.lower(),MALE)
                gender=MALE
            if fuzz.ratio(j.lower(),FEMALE)>=60 and fuzz.ratio(j.lower(),FEMALE)>gender_ratio:
                gender_ratio=fuzz.ratio(j.lower(),FEMALE)
                gender=FEMALE

    #getting rid of non-ascii characters
    dob=[i for i in dob if i>='0' and i<='9' or i=='/'  or i=='-']
    dob="".join(dob)
    name=[i for i in name if (i>='A' and i<='Z') or (i>='a' and i<='z') or i==' ']
    name="".join(name)

    output_string= HEADER
    output_string+= CATEGORY_HEAD
    output_string+=category
    output_string+=NAME_HEAD
    output_string+=name
    output_string+=ID_HEAD
    output_string+=id_no
    output_string+=DOB_HEAD
    output_string+=dob

    if doi!="":
        output_string+=DOI_HEAD
        output_string+=doi
    if sdw!="":
        output_string+=SDW_HEAD
        output_string+=sdw

    if father!="" and category==PAN:
        output_string+=FATHER_NAME
        output_string+=father

    if gender!="" and category==AADHAR:
        output_string+=GENDER_HEAD
        output_string+=gender

    

    return output_string
    
############