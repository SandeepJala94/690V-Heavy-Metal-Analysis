
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


# open the happiness scores and heavy metal data
file  = open("ranking.json", "r")
text = file.read()

file = open("metaldata.json", "r")
metal = file.read()
#print(text)


# load the data
parsed_text = json.loads(text)
metal_data = json.loads(metal)


# this just prints out the data at index 0
print(parsed_text['objects'][0])
print(len(parsed_text['objects']))


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


# In[25]:
# runs StepA and StepB of the Porter Stemmer
def stem(word):
    word = stemStepA(word)
    word = stemStepB(word)
    return word


#find all unique words in metal_data
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


# get the Google, Twitter, and New York Times rank for every word
def getGoogleTwitterNYRanks(metal_data, parsed_text):
    uniqueWords = findWords(metal_data)
    word_google_twitter_ny = {}
    
    for word in uniqueWords:
        for i in range(0, len(parsed_text['objects'])):
            if parsed_text['objects'][i]['word'] == word:
                if word not in word_google_twitter_ny.keys():
                    word_google_twitter_ny[word] = (parsed_text['objects'][i]['googleBooksRank'], parsed_text['objects'][i]['twitterRank'], parsed_text['objects'][i]['newYorkTimesRank'], parsed_text['objects'][i]['lyricsRank'])                  
                
    
    return word_google_twitter_ny



# build the scatter plot.  The variables are names googleRanks and twitterRanks, but after making the code more flexible
# these names are meaningless. They simply hold the data at word_google_twitter_ny[word][0] and word_google_twitter_ny[word][1]
def buildScatterPlot(word_google_twitter_ny):
    googleRanks = []
    twitterRanks = []
    
    for word in word_google_twitter_ny.keys():
        googleRanks.append(word_google_twitter_ny[word][0])
        twitterRanks.append(word_google_twitter_ny[word][1])

    p = figure(plot_width=800, plot_height=800)
    p.outline_line_width = 7
    p.outline_line_alpha = 0.3
    p.outline_line_color = "navy"
    p.circle(googleRanks, twitterRanks, size=3)
    return p


# In[66]:

def createPair(word_google_twitter_ny):
    xyValPairs = []
    
    for word in word_google_twitter_ny.keys():
        onePair = []
        xRank = int(word_google_twitter_ny[word][0])
        yRank =int(word_google_twitter_ny[word][1])
        onePair.append(xRank)
        onePair.append(yRank)
        xyValPairs.append(onePair)        
        
    return xyValPairs



# build the KMeans Scatter Plot
def buildKMeansScatterPlot(word_google_twitter_ny, kValue):
    X = createPair(word_google_twitter_ny)
    
    kmeans = KMeans(n_clusters=kValue, random_state=0).fit(X)
    print("kmeans.labels_ = ",kmeans.labels_)
    print("len(kmeans.labels_) = ", len(kmeans.labels_))
    
    hover = HoverTool(
        tooltips=[
            ("xRank", "$x"),
            ("yRank", "$y")
        ]
    )

    print("making figure")
    p = figure(plot_width=800, plot_height=800,  tools=[hover, PanTool(), BoxZoomTool(), WheelZoomTool()])                    

    print("making points")
    for i in range(0, len(X)):
        if kmeans.labels_[i] == 0:
            print("did for 0 at ", i)
            p.circle(X[i][0], X[i][1], size=3, line_color="green", fill_color="green", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 1:
            print("did for 1 at ", i)
            p.triangle(X[i][0], X[i][1], size=3, line_color="blue", fill_color="blue", fill_alpha=0.5)
        elif kmeans.labels_[i] == 2:
            print("did for 2 at ", i)
            p.square(X[i][0], X[i][1], size=3, line_color="red", fill_color="red", fill_alpha=0.5)
        elif kmeans.labels_[i] == 3:
            print("did for 3 at ", i)
            p.circle(X[i][0], X[i][1], size=3, line_color="blue", fill_color="blue", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 4:
            print("did for 4 at ", i)
            p.triangle(X[i][0], X[i][1], size=3, line_color="red", fill_color="red", fill_alpha=0.5)
        elif kmeans.labels_[i] == 5:
            print("did for 5 at ", i)
            p.square(X[i][0], X[i][1], size=3, line_color="green", fill_color="green", fill_alpha=0.5)
        elif kmeans.labels_[i] == 6:
            print("did for 6 at ", i)
            p.circle(X[i][0], X[i][1], size=3, line_color="red", fill_color="red", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 7:
            print("did for 7 at ", i)
            p.triangle(X[i][0], X[i][1], size=3, line_color="green", fill_color="green", fill_alpha=0.5)
        elif kmeans.labels_[i] == 8:
            print("did for 8 at ", i)
            p.square(X[i][0], X[i][1], size=3, line_color="blue", fill_color="blue", fill_alpha=0.5)
        elif kmeans.labels_[i] == 9:
            print("did for 9 at ", i)
            p.circle(X[i][0], X[i][1], size=3, line_color="black", fill_color="white", fill_alpha=0.5)     
        elif kmeans.labels_[i] == 10:
            print("did for 10 at ", i)
            p.triangle(X[i][0], X[i][1], size=3, line_color="black", fill_color="white", fill_alpha=0.5)
    
    #p.xaxis.axis_label = "Google Ranks"
    #p.yaxis.axis_label = "Twitter Ranks"
    
    print("showing plot")
    return p


# grab the data and create initial plot with k=2 and focusing on Google vs Twitter
word_google_twitter_ny = getGoogleTwitterNYRanks(metal_data, parsed_text)  

temp = {}
for word in word_google_twitter_ny.keys():
    temp[word] = (word_google_twitter_ny[word][0], word_google_twitter_ny[word][1])
        
scatterPlot = buildScatterPlot(temp)
kMeansScatterPlot = buildKMeansScatterPlot(temp, 2)


#Selections and Sliders
k_slider = Slider(title="Number of Neighbors",
                         value=2.0,
                         start=2.0,
                         end=10.0,
                         step=1,
                         width=200)

XData_select = Select(title = "XData",
                      value = "Google",
                      width=200,
                      options = ["Google", "Twitter", "New York", "lyricsRank"])


YData_select = Select(title = "YData",
                      value = "Twitter",
                      width=200,
                      options = ["Google", "Twitter", "New York", "lyricsRank"])


#Functionality of Slider
def update(attrname, old, new):
    currK = int(k_slider.value)
    currX = XData_select.value
    currY = YData_select.value
    x_index = -1
    y_index = -1
    
    if currX == "Google":
        x_index = 0
    elif currX == "Twitter":
        x_index = 1
    elif currX == "New York":
        x_index = 2
    else:#currX == lyricsRank
        x_index = 3
        
    if currY == "Google":
        y_index = 0
    elif currY == "Twitter":
        y_index = 1
    elif currY == "New York":
        y_index = 2
    else:#currY == lyricsRank
        y_index = 3
        
    temp = {}
    for word in word_google_twitter_ny.keys():
        temp[word] = (word_google_twitter_ny[word][x_index], word_google_twitter_ny[word][y_index])
        
    scatterPlot = buildScatterPlot(temp)
    kMeansScatterPlot = buildKMeansScatterPlot(temp, currK)
    

    layout.children[1] = scatterPlot
    layout.children[2] = kMeansScatterPlot
    

def updateXYData():
    currK = int(k_slider.value)
    currX = XData_select.value
    currY = YData_select.value
    
    if currX == "Google":
        x_index = 0
    elif currX == "Twitter":
        x_index == 1
    else:
        x_index == 2
        
    if currY == "Google":
        y_index = 0
    elif currY == "Twitter":
        y_index == 1
    else:
        y_index == 2
    
    temp = {}
    for word in word_google_twitter_ny.keys():
        temp[word] = (word_google_twitter_ny[word][x_index], word_google_twitter_ny[word][x_index])
    
    scatterPlot = buildScatterPlot(temp)
    kMeansScatterPlot = buildKMeansScatterPlot(temp, currK)
    
    layout.children[1] = scatterPlot
    layout.children[2] = kMeansScatterPlot
    

#execute these functions when any inputs are changed
k_slider.on_change('value', update)
XData_select.on_change('value', update)
YData_select.on_change('value', update)

# create and display plots in document
inputs = column(widgetbox(k_slider, XData_select, YData_select))
layout = row(inputs, scatterPlot, kMeansScatterPlot)
curdoc().add_root(layout)
curdoc().title = "Google VS Twitter"























