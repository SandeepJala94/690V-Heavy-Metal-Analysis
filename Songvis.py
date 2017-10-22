# coding: utf-8

# In[17]:

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


# In[18]:

file  = open("ranking.json", "r")
text = file.read()

file = open("metaldata.json", "r")
metal = file.read()
#print(text)


# In[19]:

parsed_text = json.loads(text)
metal_data = json.loads(metal)


# In[20]:

print(parsed_text['objects'][0])
print(len(parsed_text['objects']))


# In[21]:

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


# In[22]:

def firstNonVowelIndex(word):
    
    vowels = ['a', 'e', 'i',  'o', 'u', 'y']
    
    index = -1
    
    for i in range(0, len(word)):
        if word[i] not in vowels and index == -1:
            index = i
            
    #print("index is ", index)
    return index


# In[23]:

def rootHasVowel(word, endingIndex):
    
    vowels = ['a', 'e', 'i',  'o', 'u', 'y']
    
    temp = word[:-endingIndex]
    
    for v in vowels:
        if v in temp:
            return True
         
    return False


# In[24]:

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


# In[25]:

def stem(word):
    word = stemStepA(word)
    word = stemStepB(word)
    return word


# In[26]:

def findWords(metal_data):
    uniqueWords = []

    for band in metal_data.keys():
        for album in metal_data[band].keys():
            for song in metal_data[band][album].keys():
                lyrics = metal_data[band][album][song]
                wordsInSong = lyrics.split(" ")
                for w in wordsInSong:
                    if w != '':
                        if w not in uniqueWords:
                            uniqueWords.append(stem(w.lower()))
            
    return uniqueWords

def getSongLyricWords(metal_data, artist, album, song):
    uniqueWords = []
    lyrics = metal_data[artist][album][song]
    wordsInSong = lyrics.split(" ")
    for w in wordsInSong:
        if w != '':
                uniqueWords.append(stem(w.lower()))

    return uniqueWords


def getGoogleTwitterNYRanks(metal_data, parsed_text):
    uniqueWords = findWords(metal_data)
    word_google_twitter_ny = {}
    
    for word in uniqueWords:
        for i in range(0, len(parsed_text['objects'])):
            if parsed_text['objects'][i]['word'] == word:
                if word not in word_google_twitter_ny.keys():
                    word_google_twitter_ny[word] = (parsed_text['objects'][i]['happs'],
                     parsed_text['objects'][i]['twitterRank'], parsed_text['objects'][i]['newYorkTimesRank'])                  
                
    
    return word_google_twitter_ny

def getSongHappiness(metal_data, parsed_text, artist, album, song):
    uniqueWords = getSongLyricWords(metal_data, artist, album, song)
    word_happiness = {}
    
    for word in uniqueWords:
        for i in range(0, len(parsed_text['objects'])):
            if parsed_text['objects'][i]['word'] == word:
                if word not in word_happiness.keys():
                    word_happiness[word] = parsed_text['objects'][i]['happs']                 
                
    
    return word_happiness

def getSongList():
    songList = []
    for band in metal_data.keys():
        for album in metal_data[band].keys():
            for song in metal_data[band][album].keys():
                songList.append("{} | {} | {}".format(song,album,band))
    return songList


def buildScatterPlot(word_happiness):
    wordList = []
    wordHappiness = []
    
    for word in word_happiness.keys():
        wordList.append(word)
        wordHappiness.append(word_happiness[word])


    datasource = {'x':range(1,len(wordList)+1) , 'y':wordHappiness , 'labels':wordList}
    source = ColumnDataSource(datasource)
    print(len(wordList))
    hover = HoverTool(
        tooltips=[
            ("word", "@labels"),
            ]
        )
    p = figure(plot_width=800, plot_height=800, tools = [hover])
   
    p.outline_line_width = 13
    p.outline_line_alpha = 0.3  
    p.outline_line_color = "navy"
    p.line('x', 'y', source = source)
    return p


songSelect = Select(title = "Song",
                      value = "theSong",
                      width=200,
                      options = getSongList())


def update(attrname, old, new):
    currK = songSelect.value.split(' | ')
    print(currK)
    words1 = getSongHappiness(metal_data, parsed_text, currK[2], currK[1], currK[0])
    scatterPlot1 = buildScatterPlot(words1)
    layout.children[1] = scatterPlot1



songSelect.on_change('value', update)


words = getSongHappiness(metal_data, parsed_text, 'gojira', 'terraincognita', 'Clone')
print(words)
print('-----------------------------')

scatterPlot = buildScatterPlot(words)
inputs = column(widgetbox( songSelect))
layout = row(inputs, scatterPlot)
curdoc().add_root(layout)
curdoc().title = "SongVis"