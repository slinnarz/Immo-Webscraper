#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime


'''
To DOs:
    - write loop that builds URLs for each result page and gets the data
    - save raw data and result-file in a designated result folder
    - tidy up the code
'''


################# DEFINE FUNCTIONS #####################

def simple_get(url):
    """
    Attempts to get the content at "url" by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error("Error during requests to {0} : {1}".format(url, str(e)))
        return None
    
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers["Content-Type"].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find("html") > -1)
    
def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def save_html(inputData, filename):
    """
    Convert raw html data to html text and save it to a file.
    """
    html = BeautifulSoup(inputData, "html.parser")
    pretty_html = html.prettify()
    with open(filename, "w") as file:
        file.write(pretty_html)

def build_URL(page, housingType, province, city, roomMin, roomMax,
              sizeMin, sizeMax, priceMin, priceMax):
    '''
    Care: URL of first site of search results differs from other pages.
    If first page is visited via setting the page counter to 1, search results
    on page 1 are different.
    '''
    url = ("https://www.immobilienscout24.de/Suche/S-T/" +
            "P-" + page + "/" +
            "Wohnung-" + housingType + "/" +
            province + "/" +
            city + "/" +
            "-/" + # find out which filter this is for
            roomMin + ",00" + "-" + roomMax + ",00" + "/" +
            sizeMin + ",00" + "-" + sizeMax + ",00" + "/" +
            "EURO-" +
            priceMin + ",00" + "-" + priceMax + ",00")
    return url

def get_items(adress = True, cost = True, rooms = True, size = True):
    '''
    Get values for specified item from html-file.
    Allowed inputs (must be str):
        adress
        cost
        rooms
        size
    '''
    if adress == True:
        itemSelection = html.select('div > button div')
        ADDcol = list()
        for i, j in enumerate(itemSelection, 1):
            ADDcol.append(j.getText())
        ADDcol = ADDcol[1:len(ADDcol)]
        # filter empty list entries
        ADDcol = list(filter(None, ADDcol))
    if cost == True:
        itemSelection = html.find_all(class_="font-nowrap font-line-xs")
        COSTcol = list()
        for i, j in enumerate(itemSelection, 1):
            if (i+2) % 3 == 0 and i != 0:
                COSTcol.append(j.getText())
    if rooms == True:
        itemSelection = html.find_all(class_="font-nowrap font-line-xs")
        ROOMcol = list()
        for i, j in enumerate(itemSelection, 1):
            if i % 3 == 0 and i != 0:
                # Zieht den Text aus dem Tag und speichert erstes Stringelement in Liste
                ROOMcol.append(j.getText()[0])
    if size == True:
        itemSelection = html.find_all(class_="font-nowrap font-line-xs")
        SIZEcol = list()
        for i, j in enumerate(itemSelection, 1):
            if (i+1) % 3 == 0 and i != 0:
                SIZEcol.append(j.getText())
    return ADDcol, COSTcol, ROOMcol, SIZEcol

# link examples
'''
Some examples of different search result links for a quick lookup.
For rent, just city, no other filters, page 1:
"https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln?enteredFrom=one_step_search"
For rent, filtered for spans of rent, qm, rooms, page 1:
"https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/2,00-45,00/30,00-110,00/EURO-500,00-2000,00?enteredFrom=result_list"
For rent, filtered for spans of rent, qm, rooms, page 2:
"https://www.immobilienscout24.de/Suche/S-T/P-2/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/2,00-45,00/30,00-110,00/EURO-500,00-2000,00"
'''
        

############### SEARCH SETTINGS ##############

# required inputs
housingType = "Miete"
province = "Nordrhein-Westfalen"
city = "Koeln"

# optional data
roomMin = str(2) # don't forget ",00" in link!
roomMax = str(5)
sizeMin = str(45) # don't forget ",00" in link!
sizeMax = str(80)
priceMin = str(500) # don't forget "EURO" and ",00" in link!
priceMax = str(1000)


################# SCRIPT #####################

# get date and time
currDateTime = datetime.datetime.now()
# get raw html
raw_html = simple_get("https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/-/-/EURO--1000,00?enteredFrom=one_step_search")
# save raw html
save_html(raw_html, "immoscout" + "_" +
          currDateTime.strftime("%Y%m%d_%H%M") + "_" +
          #"resultPage" + page + # Zeile aktivieren, wenn per Schleife alle Ergebnisseiten abgefragt werden sollen
          ".html")
# parse html
html = BeautifulSoup(raw_html, "html.parser")    
    
# get text data from html
ADDcol = get_items()[0]
ROOMcol = get_items()[1]
COSTcol = get_items()[2]
SIZEcol = get_items()[3]

# Daten in Dataframe zusammenfassen
data = {'Quadratmeter':SIZEcol, 'Zimmerzahl':ROOMcol, 'Kaltmiete':COSTcol, 'Adresse':ADDcol}
df = pd.DataFrame(data)

# Daten in .csv-File ausgeben
df.to_csv('webData.csv')

#with open('webData.cvs', 'w') as file:
#    file.write(df)

##############
# Code-Tests #
##############   
    



    
    
