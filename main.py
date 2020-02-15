#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import get
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import io
import smtplib, ssl # for sending e-mails



"""
To DOs:
    - Fix problem: CSS selector doesnt get attributes when numbers are entered
        as a span (happens, when an ad contains multiple flats; e.g. "Rooms: 3-5")
    - looping over result pages: automatically get max. result page number
        (e.g. with CSS selector, must be somewhere in html code)
    - save raw data and result-file in a designated result folder
    - expand script: automatically get data for biggest cities (according to wikipedia list)
      in Germany
    - make "optional" search parameters optional
    - tidy up the code
In progress:
    - check if URL exists
    - send automated mail if url doesnt exist
    - --> get ssl connection to work
"""


# GLOBAL VARIABLES

# set up email connection
mailServer = "smtp.web.de"
mailServerPort = 587
mailAddress = "testmail@web.de"

# set email message
message = "An error occurred while trying to reach an URL for web scraping. Please check your web scraping setup."


# DEFINE FUNCTIONS

def simple_get(url):
    """
    Gets the content of a URL, only works if website is html.
    """
    with closing(get(url, stream=True)) as resp:
        return resp.content


def check_url(url, ):
    """
    Checks if URL exists.
    """
    code = get(url).status_code
    return code


def send_error_mail(error_code, sender_email, password, port, server, send_error=True):
    """
    Automated Mail can be sent if it doesn't.
    """
    if send_error is True and error_code != 200:
        sender_email = input("Please enter e-mail address: ")
        port = mailServerPort
        password = input("Please enter password: ")
        # Create secure SSL context
        context = ssl.create_default_context()
        server = smtplib.SMTP(mailServer, port)
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, message)


def save_html(inputData, filename):
    """
    Convert raw html data to html text and save it to a file.
    """
    html = BeautifulSoup(inputData, "html.parser")
    pretty_html = html.prettify()
    with io.open(filename, "w", encoding="utf-8") as file:
        file.write(pretty_html)

#    with open(filename, "w") as file:
#        file.write(pretty_html)

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
        # filter empty list entries
        ADDcol = list(filter(None, ADDcol))
    if cost == True:
        itemSelection = html.find_all(class_="font-nowrap font-line-xs")
        COSTcol = list()
        for i, j in enumerate(itemSelection, 1):
            if i % 3 == 0 and i != 0:
                COSTcol.append(j.getText()[0])           
    if rooms == True:
        itemSelection = html.find_all(class_="font-nowrap font-line-xs")
        ROOMcol = list()
        for i, j in enumerate(itemSelection, 1):
            if (i+2) % 3 == 0 and i != 0:
                ROOMcol.append(j.getText())
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

# required inputs
housingType = "Miete"
province = "Nordrhein-Westfalen"
city = "Koeln"
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


################# SCRIPT #####################

# required inputs
housingType = "Miete"
province = "Nordrhein-Westfalen"
city = "Koeln"

# get date and time
currDateTime = datetime.datetime.now()

# manually set max. result pages
max_pages = 1
# create empty data frame for saving search results
allDataDf = pd.DataFrame({'Quadratmeter':(), 'Zimmerzahl':(),
            'Kaltmiete':(), 'Adresse':()})

for page in range(1, max_pages+1):
    # build result page URL
    url = build_URL_withoutFilters(page, province, city)
    # check if URL exists

    # get html data
    raw_html = simple_get(url)
    # save raw html data to file
    save_html(raw_html, "immoscout" + "_" +
              currDateTime.strftime("%Y%m%d_%H%M") + "_" +
              "resultPage" + str(page) + # Zeile aktivieren, wenn per Schleife alle Ergebnisseiten abgefragt werden sollen
              ".html")
    # parse html
    html = BeautifulSoup(raw_html, "html.parser")
    # get text from html
    ADDcol = get_items()[0]
    ROOMcol = get_items()[1]
    COSTcol = get_items()[2]
    SIZEcol = get_items()[3]
    # put data into dataframe
    data = {'Quadratmeter':SIZEcol, 'Zimmerzahl':ROOMcol,
            'Kaltmiete':COSTcol, 'Adresse':ADDcol}
    allDataDf = allDataDf.append(pd.DataFrame(data), ignore_index=True)
    
# output data to .csv-file
allDataDf.to_csv('webData.csv')   


##############
# Code-Tests #
##############


# get html tags: 'script'
completeScriptData_html = html.select('script')
# get text list from list of tags
completeScriptData_text = [tag.getText() for tag in completeScriptData_html] 

# filter text list for the right item using length of string
scriptDataHousing = [item for item in completeScriptData_text if (len(item) >= 25000)]
scriptDataHousing = scriptDataHousing[0]
    
# regex for searching for housing data in script text
searchRegex = "\"attribute\":\[[a-zA-Z0-9]*\]{1}"

# search for housing data using regex
housingData = re.findall(searchRegex, scriptDataHousing)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
