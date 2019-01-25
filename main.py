#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import get
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime


'''
To DOs:
    - write loop that builds URLs for each result page and gets the data;
        Problem: when looping, CSS filters of "get_item" function doesnt work
        properly on addresses (works for page 1, doesnt for page 2).
    - save raw data and result-file in a designated result folder
    - expand script: automatically get data for biggest cities (according to wikipedia list)
      in Germany
    - make "optinal" search parameters optional
    - tidy up the code
In progress:
    - Trying to fix CSS filter problem, when iterating over result pages.
        Next step: compare html files of page 1 and 2 of search results
'''


################# DEFINE FUNCTIONS #####################

def simple_get(url):
    """
    Gets the content of a URL, only works if website is html.
    """
    with closing(get(url, stream=True)) as resp:
        return resp.content

def save_html(inputData, filename):
    """
    Convert raw html data to html text and save it to a file.
    """
    html = BeautifulSoup(inputData, "html.parser")
    pretty_html = html.prettify()
    with open(filename, "w") as file:
        file.write(pretty_html)

def build_URL_withFilters(page, housingType, province, city, roomMin, roomMax,
                          sizeMin, sizeMax, priceMin, priceMax):
    '''
    Builds the search site urls according to some filters set in the script.
    '''
    url = ("https://www.immobilienscout24.de/Suche/S-T/" +
            "P-" + str(page) + "/" +
            "Wohnung-" + housingType + "/" +
            province + "/" +
            city + "/" +
            "-/" + # find out which filter this is for
            roomMin + ",00" + "-" + roomMax + ",00" + "/" +
            sizeMin + ",00" + "-" + sizeMax + ",00" + "/" +
            "EURO-" +
            priceMin + ",00" + "-" + priceMax + ",00")
    return url

def build_URL_withoutFilters(page, province, city):
    '''
    Builds the search site urls according to some filters set in the script.
    '''
    url = ("https://www.immobilienscout24.de/Suche/S-T/" +
            "P-" + str(page) + "/" +
            "Wohnung-" + housingType + "/" +
            province + "/" +
            city)
    return url

def get_items(adress = True, cost = True, rooms = True, size = True):
    '''
    Get values for specified item from html-file.
    Allowed inputs (must be str):
        adress
        cost
        rooms
        size
    Function has to be shortened but works for now.
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
No filter except of city:
    "https://www.immobilienscout24.de/Suche/S-T/P-2/Wohnung-Miete/Nordrhein-Westfalen/Koeln"
'''
        

############### SEARCH SETTINGS ##############

## required inputs
#housingType = "Miete"
#province = "Nordrhein-Westfalen"
#city = "Koeln"
#
## optional data
#'''
#Problem, that needs to be solved: when using all filters below,
#CSS filter for adress search doesnt find adress of first search result
#of each result page.
#'''
#roomMin = str(2) # don't forget ",00" in link!
#roomMax = str(5)
#sizeMin = str(45) # don't forget ",00" in link!
#sizeMax = str(80)
#priceMin = str(500) # don't forget "EURO" and ",00" in link!
#priceMax = str(1000)
#
#
################## SCRIPT #####################
#
## get date and time
#currDateTime = datetime.datetime.now()
## get raw html
##raw_html = simple_get("https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/-/-/EURO--1000,00?enteredFrom=one_step_search")
#raw_html = simple_get("https://www.immobilienscout24.de/Suche/S-T/P-1/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/-/-/EURO--1000,00/")
## save raw html
#save_html(raw_html, "immoscout" + "_" +
#          currDateTime.strftime("%Y%m%d_%H%M") + "_" +
#          #"resultPage" + page + # Zeile aktivieren, wenn per Schleife alle Ergebnisseiten abgefragt werden sollen
#          ".html")
## parse html
#html = BeautifulSoup(raw_html, "html.parser")    
#    
## get text data from html
#ADDcol = get_items()[0]
#ROOMcol = get_items()[1]
#COSTcol = get_items()[2]
#SIZEcol = get_items()[3]
#
## put data together into dataframe
#data = {'Quadratmeter':SIZEcol, 'Zimmerzahl':ROOMcol,
#        'Kaltmiete':COSTcol, 'Adresse':ADDcol}
#df = pd.DataFrame(data)
#
## output data to .csv-file
#df.to_csv('webData.csv')



##############
# Code-Tests #
##############

# required inputs
housingType = "Miete"
province = "Nordrhein-Westfalen"
city = "Koeln"

# get date and time
currDateTime = datetime.datetime.now()

# manually set max. result pages
max_pages = 5
# create empty data frame for saving search results
allDataDf = pd.DataFrame({'Quadratmeter':(), 'Zimmerzahl':(),
            'Kaltmiete':(), 'Adresse':()})

for page in range(1, max_pages+1):
    url = build_URL_withoutFilters(page, province, city)
    raw_html = simple_get(url)
    save_html(raw_html, "immoscout" + "_" +
              currDateTime.strftime("%Y%m%d_%H%M") + "_" +
              "resultPage" + str(page) + # Zeile aktivieren, wenn per Schleife alle Ergebnisseiten abgefragt werden sollen
              ".html")
    html = BeautifulSoup(raw_html, "html.parser")  
    ADDcol = get_items()[0]
    ROOMcol = get_items()[1]
    COSTcol = get_items()[2]
    SIZEcol = get_items()[3]
    data = {'Quadratmeter':SIZEcol, 'Zimmerzahl':ROOMcol,
            'Kaltmiete':COSTcol, 'Adresse':ADDcol}
    allDataDf = allDataDf.append(pd.DataFrame(data), ignore_index=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
