import nltk
import string
from nltk.corpus import brown
from nltk.corpus import wordnet
from nltk.util import ngrams
from fuzzywuzzy import fuzz
import requests
import json

r_stop=requests.get('https://raw.githubusercontent.com/egovernments/egov-mdms-data/DEV/data/pb/Chatbot/stopwords.txt')
stopwords=r_stop.text.splitlines()

rem=stopwords
keep=['are','to','be','not']
from autocorrect import Speller
spell=Speller(lang='en')

keyWords= requests.get('https://raw.githubusercontent.com/egovernments/egov-mdms-data/DEV/data/pb/Chatbot/KeyWords.json')
result=json.loads(keyWords.text)

toBePaid=['to be paid', 'to be paid','not paid yet','not yet paid']

synonyms=result['KeyWords'][0]['synonyms']

antonyms=result['KeyWords'][0]['antonyms']

quitSynonyms=result['KeyWords'][0]['quits']

pastSynonyms=res['KeyWords'][0]['syn_past']

notPaid=res['KeyWords'][0]['bigrams'][0]['values']

for i in range(len(notPaid)):
    notPaid[i]=result['KeyWords'][0]['bigrams'][0]['prefix']+' '+notPaid[i]

notDue=res['KeyWords'][0]['bigrams'][1]['values']

for i in range(len(notDue)):
    notDue[i]=result['KeyWords'][0]['bigrams'][1]['prefix']+' '+notDue[i]

notToBePaid=result['KeyWords'][0]['bigrams'][2]['values']

for i in range(len(notToBePaid)):
    notToBePaid[i]=result['KeyWords'][0]['bigrams'][2]['prefix']+' '+notToBePaid[i]


keywordList=synonyms+antonyms+pastSynonyms+quitSynonyms+ ['to','be','hi','hello','water', 'sewerage', 'electricity', 'property','income','trade license','show','see','bills']
keywordList=list(set(keywordList))

def rectify(sentence):
    sentence=sentence.lower()
    if sentence=="hi" or sentence=="hello":
        return ("hello",0)
    
    sentence=sentence.replace('to see', 'show')
    sentence=sentence.replace('see','show')
    sentence=sentence.replace('to retrieve','show')
    sentence=sentence.replace('to retrieved','show')
    sentence=sentence.replace('to get', 'show')
    sentence=sentence.replace('get','')
    sentence=sentence.replace('take','')
    sentence=sentence.replace('look','')
    
    
    newSentence=""
    for i in sentence:
        if len(newSentence)<2:
            newSentence=newSentence+i
        elif (newSentence[len(newSentence)-1]!=i or newSentence[len(newSentence)-2]!=i):
            newSentence=newSentence+i

    newSentence=newSentence.replace("n't",' not')
    newSentence=newSentence.replace("'d"," would")
    
    for word in newSentence.split():
        if word in rem and word not in keep:
            newSentence=newSentence.replace(word,'')

   
    newSentence=newSentence.replace('wetar', 'water')
    newSentence=newSentence.replace (' want ', ' ')
    newSentence=newSentence.replace(' wants ', ' ')
    newSentence=newSentence.replace (' wanted ', ' ')
    
    finalSentence=''
    
    count=0
    for i in newSentence.split():
        maxRatio=0
        
        newWord=''
        for j in keywordList:
            if fuzz.ratio(i,j)>=70 and fuzz.ratio(i,j)>maxRatio:
                count+=1
                maxRatio=fuzz.ratio(i,j)
                newWord=j
                
        if maxRatio!=0:
            finalSentence+=newWord+' '
        else:
            finalSentence+= spell(i)+' '

    
    flag=0
    if 'show' in finalSentence or 'see' in finalSentence:
        flag=1
    wordList=finalSentence.split();
    answerSentence=' '.join([i for i in wordList if i not in ['see','show']])
    

    if count!=0:
        
        return (answerSentence,flag)
    else:
        return ("invalid",flag)
