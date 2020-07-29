import json
import math
import re
from tkinter import *;
from nltk.stem import WordNetLemmatizer
import numpy
from numpy import array
import os
lemmatizer=WordNetLemmatizer()
if( not (os.path.isfile('./vectorSpace.txt'))):

    file = open("Stopword-List.txt","r");
    stopList = file.read().split();
    vectorSpace = dict()
    numberOfWord = 0
    for i in range(0,55):
        file = open("speech_"+str(i)+".txt","r")
        docWords = file.read()
        #-------------------------------------------------------------------- Preprocessing-------------------------------------------------#

        docWords  = re.sub('-', '', docWords )
        docWords  = re.sub("'", '', docWords )
        docWords  = re.sub("\.", '', docWords )
        docWords  = re.sub("’", '', docWords )
        docWords  = re.sub("`", '', docWords )
        docWords  = re.sub("‘", '', docWords )
        docWords = re.sub("'", '', docWords)
        docWords = re.sub("$", '', docWords)
        docWords = re.sub(":", '', docWords)
        docWords = re.sub(";", '', docWords)
        docWords = re.sub("`", '', docWords)
        docWords = re.sub("—", ' ', docWords)
        docWords .strip()
        
        
        docWords  = re.sub("\W", ' ', docWords )
        
        docWords = docWords.casefold()
        docWords = docWords.split()
        
       # print(docWords)
#-------------------------------------------------------------------- Lemmatization--------------------------------------------------#

        for j in range(len(docWords)):
            docWords[j]=lemmatizer.lemmatize(docWords[j])

        #docWords = list(dict.fromkeys(docWords))
        for term in docWords:
            if(term != "" and term not in stopList):
                if (term not in vectorSpace ):
                    temp = {term:{"list": [0],"df": 1}}
                    for z in range(0,55):
                        temp[term]["list"].append(0)
                    vectorSpace.update(temp)
                    vectorSpace[term]["list"][i-1] += 1
                    numberOfWord += 1
                   

                else:
                    vectorSpace[term]["list"][i-1] += 1
                    if(vectorSpace[term]["list"][i-1] == 1):
                        vectorSpace[term]["df"] += 1
        
    normList = [0] * 55
    for key in vectorSpace.keys():
        vectorSpace[key]["df"] =  math.log10(55/vectorSpace[key]["df"])
        for i in range(0,55):
            if (vectorSpace[key]["list"][i] != 0):
                vectorSpace[key]["list"][i] = 1 + math.log10(vectorSpace[key]["list"][i])
                vectorSpace[key]["list"][i] *= vectorSpace[key]["df"]
                normList[i] += math.pow(vectorSpace[key]["list"][i],2)
    for i in range (0,55):
        normList[i] = math.sqrt(normList[i])
    vectorSpace.update({"-norm": normList})
    del normList

    with open("vectorSpace.txt",'w+') as file:
        file.write(json.dumps(vectorSpace))
    del vectorSpace

#-------------------------------------------------------------------- Query processing--------------------------------------------------#
def vectorSpace():
    # results = Text(top, width=70, bg="white")
    # results.pack(side=TOP, fill=X)
    results.delete('1.0', END)
#----------------------------------------------------------------------Reading Stopwords------------------------------------------------#
    file = open("Stopword-List.txt", "r");
    stopList = file.read().split();
#----------------------------------------------------------------------Formation of Index------------------------------------------------#

    with open("vectorSpace.txt",'r') as file:
        temp = file.read()
    vectorSpace = json.loads(temp)
    vectorSpace = dict(sorted(vectorSpace.items(), key = lambda t: t[0]))
    querey = quereyBox.get()
    if(querey != ""):
        querey  = re.sub('-', '', querey )
        querey  = re.sub("'", '', querey )
        querey  = re.sub("\.", '', querey )
        querey  = re.sub("’", '', querey )
        querey  = re.sub("`", '', querey )
        querey  = re.sub("‘", '', querey )
        querey = re.sub("'", '', querey)
        querey = re.sub("—", ' ', querey)
        querey .strip()
        querey  = re.sub("\W", ' ', querey )
       
        querey = querey.casefold()
        querey = querey.split()
        for j in range(len(querey)):
            querey[j]=lemmatizer.lemmatize(querey[j])

        print(querey)
        quereySpace = dict()
        for term in querey:
            if(term != "" and term not in stopList):
                if (term not in quereySpace ):
                    temp = {term:1}
                    quereySpace.update(temp)
                else:
                    quereySpace[term] += 1

        normQuerey = 0
        for key in quereySpace.keys():
            if (key in vectorSpace):
                quereySpace[key] =  1 + math.log10(quereySpace[key])
                quereySpace[key] *= vectorSpace[key]["df"]
                normQuerey += math.pow(quereySpace[key],2)
            else:
                results.insert(END, "Term \""+key+"\" does not exist in dictionary\n")
        normQuerey = math.sqrt(normQuerey)

        result = [0] * 55
        if(normQuerey != 0 ):
            for j in range(0, 55):
                if( vectorSpace["-norm"][j] !=0):
                    product  = 0
                    for key in quereySpace.keys():
                        if (key in vectorSpace):
                            product += (quereySpace[key]) * (vectorSpace[key]["list"][j] )

                    result[j] = product/(normQuerey* vectorSpace["-norm"][j])
            index = numpy.argsort(result)
            k = 0;
            results.insert(END,"\t\tResults:\n")
            results.insert(END,"[")
            for i in range (54,-1,-1):
                if(result[index[i]] > 0.005):
                    k += 1
                  
                    results.insert(END,str(index[i]+1))
                   
                    results.insert(END,str(","))
                  
            results.insert(END,"]")
            results.insert(END,"\nLength:"+str(k),)
           
top =  Tk()
top.title("Assignment: 2")
top.geometry("400x400")
top.configure(background="black")

searchFrame = Frame(top,width = 300,height = 600)
searchFrame.pack(side=BOTTOM)
lable= Label(top,width = 70,bg="yellow",text="Enter your query bellow",font="bold")
lable.pack(side=BOTTOM)
results = Text(top, width=70,height=30, bg="lightblue")
results.pack(side = TOP,fill=X)
search = Button(searchFrame, font="Bold", text = "search",bg= "red",fg="white",activebackground = "green",activeforeground="white",width = 25,command=vectorSpace)
search.pack(side=BOTTOM,fill=X)
quereyBox = Entry(searchFrame,width = 50)
quereyBox.pack(side=BOTTOM,fill=X)
results.insert(END,"Related Documents")


top.mainloop()
