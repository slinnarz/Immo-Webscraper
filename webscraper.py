#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime

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
    Is is always a good idea to log errors.
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
    
################# SCRIPT #####################

# get date and time
currDateTime = datetime.datetime.now()
# get raw html
raw_html = simple_get("https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/-/-/EURO--1000,00?enteredFrom=one_step_search")
# save raw html
save_html(raw_html, "immoscout" + "_" +
          currDateTime.strftime("%Y%m%d_%H%M") +
          ".html")
# parse html
html = BeautifulSoup(raw_html, "html.parser")    
    
# Suche von tags mit Adressen
ADDselection = html.select('div > button div')
ADDsearch = html.find_all("div", class_="font-ellipsis")

for i, j in enumerate(ADDselection, 1):
#    if i % 3 == 0 and i != 0:
#        continue
    print(i, j.getText())
    
for i, j in enumerate(ADDsearch, 1):
#    if i % 3 == 0 and i != 0:
#        continue
    print(i, j.getText())

# Suche von tags mit Mietpreisen und Quadratmeterzahlen
COSTsearch = html.find_all(class_="font-nowrap font-line-xs")

for i, search in enumerate(COSTsearch, 1):
#    if i % 3 == 0 and i != 0:
#        continue
    print(i, search.getText())

# Liste mit Zimmeranzahl
ROOMcol = list()
for i, j in enumerate(COSTsearch, 1):
    if i % 3 == 0 and i != 0:
        # Zieht den Text aus dem Tag und speichert erstes Stringelement in Liste
        ROOMcol.append(j.getText()[0])

# Liste mit Kaltmietpreisen
COSTcol = list()
for i, j in enumerate(COSTsearch, 1):
    if (i+2) % 3 == 0 and i != 0:
        COSTcol.append(j.getText())

# Liste mit Quadratmeterzahlen 
SIZEcol = list()
for i, j in enumerate(COSTsearch, 1):
    if (i+1) % 3 == 0 and i != 0:
        SIZEcol.append(j.getText())

# list with adresses        
ADDcol = list()
for i, j in enumerate(ADDselection, 1):
    ADDcol.append(j.getText())
ADDcol = ADDcol[1:len(ADDcol)]
# filter empty list entries
ADDcol = list(filter(None, ADDcol))

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
    
#data = {'Quadratmeter':SIZEcol, 'Zimmerzahl':ROOMcol, 'Kaltmiete':COSTcol}
#df = pd.DataFrame(data) 
#
#    
#    
#    
#data = pd.DataFrame()
#for i, search in enumerate(COSTsearch, 1):
#    if i % 3 == 0 and i != 0:
#        print(i, data.append(search.getText()))
#
#
#ROOMcol = list()
#for i, j in enumerate(COSTsearch, 1):
#    if i % 3 == 0 and i != 0:
#        ROOMcol.append(j.getText()[0])
#    print(i, j.getText())


    
    
