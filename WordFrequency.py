
# coding: utf-8

# In[1]:

import json
import numpy as np
np.random.seed(0)

from bokeh.io import curdoc
from bokeh.layouts import widgetbox, row, column, layout
from bokeh.models import ColumnDataSource, Select, Slider
from bokeh.palettes import Spectral6
from bokeh.io import output_notebook, show
from bokeh.plotting import figure, output_file, show
from sklearn import tree

from sklearn import neighbors, datasets
from sklearn.neighbors import NearestNeighbors
from sklearn import cluster, datasets
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler, MinMaxScaler

import xlrd
from sklearn.cluster import KMeans
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.models import BoxZoomTool
from bokeh.models import WheelZoomTool
from bokeh.models import PanTool


#read in the heavy metal music and the happiness data from 
file  = open("ranking.json", "r")
text = file.read()

file = open("metaldata.json", "r")
metal = file.read()


#load the data
parsed_text = json.loads(text)
metal_data = json.loads(metal)


# In[4]:
#this is just to look at the first 10 words and their ranks
number = 1
for i in range(0, 10):
    print(parsed_text['objects'][i]['word'], "\t\t", parsed_text['objects'][i]['rank'])


# In[5]:
#stemStepA an stemStepB executes the rules of the Porter Stemmer
def stemStepA(word):
    vowels = ['a', 'e', 'i',  'o', 'u', 'y']
    
    if word[len(word)-3:] == "ied" or word[len(word)-3:] == "ies":
        return word[:-2]
    
    
    if word[len(word)-4:] == "sses":
        if len(word) >= 4:
            word = word[:len(word)-4] + "ss"
        return word
    
    
    if word[len(word)-1:] == "s":
        if word[len(word)-2:-1] not in vowels:
            word = word[:-1]    
        return word
    
    
    return word    


# looks for the index of the first non-vowel character
def firstNonVowelIndex(word):
    
    vowels = ['a', 'e', 'i',  'o', 'u', 'y']
    
    index = -1
    
    for i in range(0, len(word)):
        if word[i] not in vowels and index == -1:
            index = i
            
    #print("index is ", index)
    return index


#checks if the root, the sequence of characters before the endingIndex has a vowel
def rootHasVowel(word, endingIndex):
    
    vowels = ['a', 'e', 'i',  'o', 'u', 'y']
    
    temp = word[:-endingIndex]
    
    for v in vowels:
        if v in temp:
            return True
         
    return False


# this follows the rules of the Porter Stemmer
def stemStepB(word):
    vowels = ['a', 'e', 'i',  'o', 'u', 'y']
    
    #print(word, "got past 0")
    
    if len(word) >= 4:
        if word[len(word)-3:] == "eed":
            if word[len(word)-4:-3] not in vowels:
                    if len(word)-4 == firstNonVowelIndex(word):
                        return word
                    else:
                        return word[:-3] + "ee"
                    
                    
                    
                    
    #print(word, "got past 1")
        
    if len(word) >= 6:
        if word[len(word)-5:] == "eedly":
            if word[len(word)-6:-5] not in vowels:
                if len(word)-6 == firstNonVowelIndex(word):
                    return word
                else:
                    return word[:-5] + "ee"
        
        
        
        
    #print(word, "got past 2")
    
    if word[len(word)-2:] == "ed":
        if rootHasVowel(word, 2) == True:
            word = word[:-2]
        
        if word[len(word)-2:] == "at" or word[len(word)-2:] == "bl" or word[len(word)-2:] == "az":
            word = word + "e"
            
        if word[len(word)-2:-1] == word[len(word)-1:]:
            if word[len(word)-2:] != "ll" and word[len(word)-2:] != "ss" and word[len(word)-2:] != "zz":                                  
                word = word[:-1]
            
        return word

    
    
    
    #print(word, "got past 3")
    
    if word[len(word)-4:] == "edly":
        if rootHasVowel(word, 4) == True:
            word = word[:-4]
        
        if word[len(word)-2:] == "at" or word[len(word)-2:] == "bl" or word[len(word)-2:] == "az":
            word = word + "e"
            
        if word[len(word)-2:-1] == word[len(word)-1:]:
            if word[len(word)-2:] != "ll" and word[len(word)-2:] != "ss" and word[len(word)-2:] != "zz":                                  
                word = word[:-1]
            
        return word
    
    
    
    
    #print(word, "got past 4")
    
    if word[len(word)-3:] == "ing":
        if rootHasVowel(word, 3) == True:
            word = word[:-3]
            
        if word[len(word)-2:] == "at" or word[len(word)-2:] == "bl" or word[len(word)-2:] == "az":
            word = word + "e"
            
        if word[len(word)-2:-1] == word[len(word)-1:]:
            if word[len(word)-2:] != "ll" and word[len(word)-2:] != "ss" and word[len(word)-2:] != "zz":                                  
                word = word[:-1]
            
            
        return word
    
    
    
    
    #print(word, "got past 5")
    
    if word[len(word)-5:] == "ingly":
        if rootHasVowel(word, 5) == True:
            word = word[:-5]
            
        if word[len(word)-2:] == "at" or word[len(word)-2:] == "bl" or word[len(word)-2:] == "az":
            word = word + "e"
            
        if word[len(word)-2:-1] == word[len(word)-1:]:
            if word[len(word)-2:] != "ll" and word[len(word)-2:] != "ss" and word[len(word)-2:] != "zz":                                  
                word = word[:-1]
            
        return word
        
    return word


# runs StepA and StepB of the Porter Stemmer
def stem(word):
    word = stemStepA(word)
    word = stemStepB(word)
    return word


#find all unique words and their # of occurences in metal_data
def findUniqueWords(metal_data):
    uniqueWords = {}
    words = []

    for band in metal_data.keys():
        for album in metal_data[band].keys():
            for song in metal_data[band][album].keys():
                lyrics = metal_data[band][album][song]
                wordsInSong = lyrics.split(" ")
                for w in wordsInSong:
                    if w != '':
                        words.append(w.lower())

    for w in words:
        if w in uniqueWords.keys():
            uniqueWords[w] += 1
        else:
            uniqueWords[w] = 1
            
    return uniqueWords


# builds a bar plot for the words at startingIndex and the number of words after it (1-10)
def buildWordFrequencyBarPlot(startingIndex, numOfWords, uniqueWords):
    if (startingIndex + numOfWords) <= len(uniqueWords):
        wordsInSet = []

        for k in uniqueWords.keys():
            wordsInSet.append(k)

        wordsForPlot = []
        countsForPlot = []

        for i in range(startingIndex, startingIndex + numOfWords):
            wordsForPlot.append(wordsInSet[i])
            countsForPlot.append(uniqueWords[wordsInSet[i]])

        for i in range(0, len(wordsForPlot)):
            print(wordsForPlot[i], "\t", countsForPlot[i])
            
        p = figure(x_range=wordsForPlot, plot_height = 250, title="Frequency of Words")                             
        p.vbar(x=wordsForPlot, top=countsForPlot, width = 0.9)
               
        return p


# This creates the initial bar plot
uniqueWords = findUniqueWords(metal_data)
wordFreqBarPlot = buildWordFrequencyBarPlot(0, 10, uniqueWords)
endOfSliderNum = len(uniqueWords)-10


# Sliders for starting point and number of words to look after the starting point
startingPoint_slider = Slider(title="Starting Index",
                         value=0.0,
                         start=1.0,
                         end=endOfSliderNum,
                         step=1,
                         width=200)

numOfWordsLookingAt_slider = Slider(title="Number of words to look after Starting Point",
                         value=10.0,
                         start=1.0,
                         end=10.0,
                         step=1,
                         width=200)


# Functionality of clicking on startingPoint_slider
def updateStartingPoint(attrname, old, new):
    s = int(startingPoint_slider.value)
    n = int(numOfWordsLookingAt_slider.value)
    wordFreqBarPlot = buildWordFrequencyBarPlot(s, n, uniqueWords)
    layout.children[1] = wordFreqBarPlot


#Functionality of clicking on startingPoint_slider and numOfWordsLookingAt_slider
def updateNumOfWordsLookingAt(attrname, old, new):
    s = int(startingPoint_slider.value)
    n = int(numOfWordsLookingAt_slider.value)
    wordFreqBarPlot = buildWordFrequencyBarPlot(s, n, uniqueWords)
    layout.children[1] = wordFreqBarPlot



# Execute the corresponding functions when changed
startingPoint_slider.on_change('value', updateStartingPoint)
numOfWordsLookingAt_slider.on_change('value', updateNumOfWordsLookingAt)


# sets up and displays the initial bar plot
inputs = column(widgetbox(startingPoint_slider, numOfWordsLookingAt_slider, sizing_mode="scale_both"))
layout = row(inputs, wordFreqBarPlot)
curdoc().add_root(layout)
curdoc().title = "WordFrequency"

