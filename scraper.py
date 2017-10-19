from bs4 import BeautifulSoup
from urllib.request import urlopen
import string
import re
import json


#gets lyrics for album page 
def getAlbumLyrics(url):
    thelyrics = None
    print(url)
    with urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
       
        classes  = soup.find_all(class_=True)
        print(classes)
        for i in classes:
            if i["class"] == ['lyrics']:
                thelyrics = i 
    if thelyrics ==None:
        return None 
    thelyrics = thelyrics.prettify().split('<h3>')
    thelyrics[-1] = thelyrics[-1].split('<div class="thanks">')[0]
    thelyrics = thelyrics[1:]
    thelyrics = [i.replace(' <br/>','') for i in thelyrics]
    
    theTitle = [i.split(' </h3>')[0] for i in thelyrics]
    thelyrics =[i.split(' </h3>')[1].replace('\n','  ') for i in thelyrics]

    theTitle = [i.split('\n')[2] for i in theTitle]

    theTitle = [i.split('.')[1].strip() if '.' in i else i.strip() for i in theTitle]
    theAlbum = {}

    for i in range(len(theTitle)):
        theAlbum[theTitle[i]] = thelyrics[i]

    # print(theAlbum.keys())
    """dict of key song name, value lyric"""
    return theAlbum


    #gets all albums from artist
def getAlbumList(url):
    with urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.prettify())
        # print(soup.body.)
        classes  = soup.find_all(class_=True)
        albums = []
        for i in classes:
            if i["class"] == ['album']:
                 albums.append(i)

    # swap to regex and watch for no match 
    theUrls = [   (i.prettify().split('href="..')[1].split('.html#')[0]) for i in albums ]
    theAlbum = [i.split('/')[3] for i in theUrls]
    albumList = {}

    for i in range(len(theUrls)):   
        print(theUrls[i])
        albumList[theAlbum[i]] = getAlbumLyrics('http://www.darklyrics.com' + theUrls[i]+'.html')
    return albumList

    # print(theUrls)
    # print(theUrls)
        # print(thelyrics)







# get all artists from letter page
def getArtistList(url):
    with urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.prettify())
        # print(soup.body.)
        classes  = soup.find_all(class_=True)
        artists = []
        for i in classes:
            if i["class"] == ['artists', 'fl'] or i["class"] == ['artists', 'fr'] :
                # print(re.findall(r'href=".\/[a-z]+.html', i.prettify()))
                # print(i)
                artists = artists + re.findall(r'href=".\/[a-z]+.html', i.prettify())
        

        artistset = {}
        for i in artists:
            print('http://www.darklyrics.com/'+i[6:])
            artistset[i[8:-5]]  = getAlbumList('http://www.darklyrics.com/'+i[6:])
            
    return artistset

def scraper():
    result = {}
    result.update(getArtistList('http://www.darklyrics.com/r.html'))
    # for i in string.ascii_lowercase:
    #     result.update(getArtistList('http://www.darklyrics.com/' + i + '.html'))
    return result 

result = {}
artistsurls = ['http://www.darklyrics.com/g/gojira.html','http://www.darklyrics.com/g/gadget.html','http://www.darklyrics.com/a/abandonallships.html','http://www.darklyrics.com/b/badomens.html']
for i in artistsurls:
     result[i[28:-5]] = getAlbumList(i)
# print(getAlbumLyrics('http://www.darklyrics.com/lyrics/steeler/rulintheearth.html'))

with open('metaldata.txt', 'w') as outfile:
    json.dump(result, outfile)


