
# coding: utf-8

# In[29]:

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


# open the happiness scores and heavy metal data
file  = open("ranking.json", "r")
text = file.read()

file = open("metaldata.json", "r")
metal = file.read()
#print(text)


# load the data
parsed_text = json.loads(text)
metal_data = json.loads(metal)


#this is just to look at the first 10 words and their ranks
number = 1
for i in range(0, 10):
    print(parsed_text['objects'][i]['word'], "\t\t", parsed_text['objects'][i]['rank'])


# stemStepA an stemStepB executes the rules of the Porter Stemmer
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


# #find all unique words in metal_data
def findUniqueWords(metal_data):
    uniqueWords = []

    for band in metal_data.keys():
        for album in metal_data[band].keys():
            for song in metal_data[band][album].keys():
                lyrics = metal_data[band][album][song]
                wordsInSong = lyrics.split(" ")
                for w in wordsInSong:
                    if w != '':
                        if stem(w.lower()) not in uniqueWords:
                            uniqueWords.append(stem(w.lower()))

            
    return uniqueWords


# creates a dictionary of {dict[song] : {dict[word]:1} }
def createSongToWordsDict(metal_data):
    songsToWords = {}
    
    for band in metal_data.keys():
        for album in metal_data[band].keys():
            for song in metal_data[band][album].keys():
                
                songsToWords[song] = {}
                
                lyrics = metal_data[band][album][song]
                wordsInSong = lyrics.split(" ")
                for w in wordsInSong:
                    if w != '':
                        if songsToWords[song].keys == None:
                            songsToWords[song][stem(w.lower())] = 1
                        if stem(w.lower()) not in songsToWords[song].keys():
                            songsToWords[song][stem(w.lower())] = 1 
                        else:#if stem(w.lower()) in songsToWord[song].keys()
                            songsToWords[song][stem(w.lower())] += 1
                            
    return songsToWords                


# goes through songsToWords and returns a list and np.array of the number of occurences of wordX and wordY in all songs
# if word does not exist, then give value of 0
def createPair(songsToWords, wordX, wordY):
    pairs = []
    
    for song in songsToWords.keys():
        onePair = []
        
        if wordX not in songsToWords[song].keys():
            onePair.append(0)
        else:
            onePair.append(songsToWords[song][wordX])
            
            
        if wordY not in songsToWords[song].keys():
            onePair.append(0)
        else:
            onePair.append(songsToWords[song][wordY])
        
        pairs.append(onePair)
        
    return pairs, np.array(pairs)


# finds the number of identical pairs and returns as dictionary
def findPairCounts(X):
    uniquePairs = {}
    
    for pair in X:
        if (pair[0], pair[1]) in uniquePairs.keys():
            uniquePairs[(pair[0], pair[1])] += 1
        else:
            uniquePairs[(pair[0], pair[1])] = 1
            
    return uniquePairs


# build the KMeansPlot
def buildSongKMeansPlot(songsToWords, wordX, wordY, kValue):
    pairs, X = createPair(songsToWords, wordX, wordY)
    
    pairCounts= findPairCounts(pairs)
    print(pairCounts)
    
    kmeans = KMeans(n_clusters=kValue, random_state=0).fit(X)
    print("kmeans.labels_ = ",kmeans.labels_)
    print("len(kmeans.labels_) = ", len(kmeans.labels_))
    
    print("making figure")
    p = figure(plot_width=800, plot_height=800, title= wordX + " vs " + wordY,  tools=[PanTool(), BoxZoomTool(), WheelZoomTool()])                    
    
    print("making points")
    for i in range(0, len(X)):
        if kmeans.labels_[i] == 0:
            #print("did for 0 at ", i)
            p.circle(X[i][0], X[i][1], size=5, line_color="green", fill_color="green", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 1:
            #print("did for 1 at ", i)
            p.triangle(X[i][0], X[i][1], size=5, line_color="blue", fill_color="blue", fill_alpha=0.5)
        elif kmeans.labels_[i] == 2:
            #print("did for 2 at ", i)
            p.square(X[i][0], X[i][1], size=5, line_color="red", fill_color="red", fill_alpha=0.5)
        elif kmeans.labels_[i] == 3:
            #print("did for 3 at ", i)
            p.circle(X[i][0], X[i][1], size=5, line_color="blue", fill_color="blue", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 4:
            #print("did for 4 at ", i)
            p.triangle(X[i][0], X[i][1], size=5, line_color="red", fill_color="red", fill_alpha=0.5)
        elif kmeans.labels_[i] == 5:
            #print("did for 5 at ", i)
            p.square(X[i][0], X[i][1], size=5, line_color="green", fill_color="green", fill_alpha=0.5)
        elif kmeans.labels_[i] == 6:
            #print("did for 6 at ", i)
            p.circle(X[i][0], X[i][1], size=5, line_color="red", fill_color="red", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 7:
            #print("did for 7 at ", i)
            p.triangle(X[i][0], X[i][1], size=5, line_color="green", fill_color="green", fill_alpha=0.5)
        elif kmeans.labels_[i] == 8:
            #print("did for 8 at ", i)
            p.square(X[i][0], X[i][1], size=5, line_color="blue", fill_color="blue", fill_alpha=0.5)
        elif kmeans.labels_[i] == 9:
            #print("did for 9 at ", i)
            p.circle(X[i][0], X[i][1], size=5, line_color="black", fill_color="white", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 10:
            #print("did for 10 at ", i)
            p.triangle(X[i][0], X[i][1], size=5, line_color="black", fill_color="white", fill_alpha=0.5)
    
    print("showing plot")
    return p


# initial set
uniqueWords = findUniqueWords(metal_data)
print("len(uniqueWords) = ", len(uniqueWords))
songsToWords = createSongToWordsDict(metal_data)
print(len(songsToWords))
#print(songsToWords)
songKMeansPlot = buildSongKMeansPlot(songsToWords, "every", "death", 2)


#Selections and Sliders
k_slider = Slider(title="Number of Neighbors",
                         value=2.0,
                         start=2.0,
                         end=10.0,
                         step=1,
                         width=200)

XData_select = Select(title = "XData",
                      value = "every",
                      width=200,
                      options = uniqueWords)


YData_select = Select(title = "YData",
                      value = "death",
                      width=200,
                      options = uniqueWords)


#Functionality of Slider
def update(attrname, old, new):
    currK = int(k_slider.value)
    currX = XData_select.value
    currY = YData_select.value
    
    songKMeansPlot = buildSongKMeansPlot(songsToWords, currX, currY, currK)
    
    layout.children[1] = songKMeansPlot


# execute update() when changed
k_slider.on_change('value', update)
XData_select.on_change('value', update)
YData_select.on_change('value', update)


# create and display original plot in document
inputs = column(widgetbox(k_slider, XData_select, YData_select))
layout = row(inputs, songKMeansPlot)
curdoc().add_root(layout)
curdoc().title = "Clustering Songs Based on # of Wordds"

