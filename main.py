#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from requests import get
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import io
import smtplib  # for sending e-mails
import ssl  # for sending e-mails


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

# data path
htmlDataPath = "C:\\Users\\Stefan\\PycharmProjects\\Immo-Webscraper"

# set up email connection
mailServer = "smtp.web.de"
mailServerPort = 587
mailAddress = "testmail@web.de"

# set email message
message = "An error occurred while trying to reach an URL for web scraping. Please check your web scraping setup."


# DEFINE FUNCTIONS

def create_folder(path, name):
    if not os.path.isdir(path+"\\"+name):
        os.mkdir(path+"\\"+name)


def simple_get(url):
    """
    Gets the content of a URL, only works if website is html.
    """
    with closing(get(url, stream=True)) as resp:
        return resp.content


def check_url(url):
    """
    Checks if URL exists.
    """
    code = get(url).status_code
    return code


def send_error_mail(error_code, port, send_error=True):
    """
    Automated Mail can be sent if it doesn't.
    """
    if send_error is True and error_code != 200:
        sender_email = input("Please enter e-mail address: ")
        password = input("Please enter password: ")
        # Create secure SSL context
        context = ssl.create_default_context()
        server = smtplib.SMTP(mailServer, port)
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, message, msg=message)


def save_html(input_data, filename):
    """
    Convert raw html data to html text and save it to a file.
    """
    html = BeautifulSoup(input_data, "html.parser")
    pretty_html = html.prettify()
    with io.open(filename, "w", encoding="utf-8") as file:
        file.write(pretty_html)


def build_url(page, housing_type, province, city="", filters=False, room_min="0", room_max="0",
              size_min="0", size_max="0", price_min="0", price_max="0"):
    """
    Builds the search site urls according to some filters set in the script.
    """
    if housing_type == "Wohnung-Miete":
        if filters is True:
            url = ("https://www.immobilienscout24.de/Suche/S-T/" +
                   "P-" + str(page) + "/" +
                   "Wohnung-" + housing_type + "/" +
                   province + "/" +
                   city + "/" +
                   "-/" +  # find out which filter this is for
                   room_min + ",00" + "-" + room_max + ",00" + "/" +
                   size_min + ",00" + "-" + size_max + ",00" + "/" +
                   "EURO-" +
                   price_min + ",00" + "-" + price_max + ",00")
            return url
        else:
            url = ("https://www.immobilienscout24.de/Suche/S-T/" +
                   "P-" + str(page) + "/" +
                   "Wohnung-" + housing_type + "/" +
                   province + "/" +
                   city)
            return url
    if housing_type == "haus-kaufen":
        if filters is True:
            print("Filters for 'haus-kaufen' have not yet been implemented.")
        else:
            url = ("https://www.immobilienscout24.de/Suche/de/" +
                   "nordrhein-westfalen/" + "haus-kaufen?pagenumber=" + str(page))
            return url


def get_address(html, housing_type):
    """
    Get address from html file.
    """
    if housing_type == "Wohnung-Mieten":
        item_selection = html.select('div > button div')
    else:
        item_selection = html.select('button[title="Auf der Karte anzeigen"]')
    add_col = list()
    for i, j in enumerate(item_selection, 1):
        add_col.append(j.getText().strip())  # .strip() gets rid of all '\n'
    # filter empty list entries
    add_col = list(filter(None, add_col))
    return add_col


def get_cost(html, housing_type):
    """
    Get cost from html file.
    """
    if housing_type == "Wohnung-Mieten":
        item_selection = html.find_all(class_="font-nowrap font-line-xs")
        cost_col = list()
        for i, j in enumerate(item_selection, 1):
            if i % 3 == 0 and i != 0:
                cost_col.append(j.getText()[0])
        return cost_col
    else:
        item_selection = html.select('dl[class="grid-item result-list-entry__primary-criterion"]')
        cost_col = list()
        for i, j in enumerate(item_selection, 1):
            if i == 0 or (i+2) % 3 == 0:
                cost_col.append(j.getText().strip())
        cost_col = [item.split()[0] for item in cost_col]  # if (len(item.split()) == 3)]
        return cost_col


def get_rooms(html, housing_type):
    """
    Get number of rooms from html file.
    """
    if housing_type == "Wohnung-Mieten":
        item_selection = html.find_all(class_="font-nowrap font-line-xs")
        room_col = list()
        for i, j in enumerate(item_selection, 1):
            if (i+2) % 3 == 0 and i != 0:
                room_col.append(j.getText())
        return room_col
    else:
        item_selection = html.select('dl[class="grid-item result-list-entry__primary-criterion"]')
        room_col = list()
        for i, j in enumerate(item_selection, 1):
            if i % 3 == 0 and i != 0:
                room_col.append(j.getText().strip())
        room_col = [item.split()[0] for item in room_col]  # if (len(item.split()) == 4)]
        return room_col


def get_size(html, housing_type):
    """
    Get dwelling size from html file.
    """
    if housing_type == "Wohnung-Mieten":
        item_selection = html.find_all(class_="font-nowrap font-line-xs")
        size_col = list()
        for i, j in enumerate(item_selection, 1):
            if (i+1) % 3 == 0 and i != 0:
                size_col.append(j.getText())
        return size_col
    else:
        item_selection = html.select('dl[class="grid-item result-list-entry__primary-criterion"]')
        size_col = list()
        for i, j in enumerate(item_selection, 1):
            if (i+1) % 3 == 0 and i != 0:
                size_col.append(j.getText().strip())
        size_col = [item.split()[0] for item in size_col]  # if (len(item.split()) == 3)]
        return size_col

# link examples


"""
Some examples of different search result links for a quick lookup.
For rent, just city, no other filters, page 1:
    "https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln?enteredFrom=one_step_search"
For rent, filtered for spans of rent, qm, rooms, page 1:
    "https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/2,00-45,00/30,00-110,00/EURO-500,00-2000,00?enteredFrom=result_list"
For rent, filtered for spans of rent, qm, rooms, page 2:
    "https://www.immobilienscout24.de/Suche/S-T/P-2/Wohnung-Miete/Nordrhein-Westfalen/Koeln/-/2,00-45,00/30,00-110,00/EURO-500,00-2000,00"
For rent, no filter except of city:
    "https://www.immobilienscout24.de/Suche/S-T/P-2/Wohnung-Miete/Nordrhein-Westfalen/Koeln"
For sale, filtered for province:
    "https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/haus-kaufen?pagenumber=2" (about 20.000 results total)
"""
        

# SEARCH SETTINGS

# required inputs
# searchHousingType = "Wohnung-Miete"
searchHousingType = "haus-kaufen"
searchProvince = "Nordrhein-Westfalen"
searchCity = "Koeln"


# optional inputs
"""
Uncomment following block if you want to use search filters.

To Do:
When using all filters below,
CSS filter for address search doesnt find adress of first search result
of each result page.
"""
# searchRoomMmin = str(2)   # don't forget ",00" in link!
# searchRoomMax = str(5)
# searchSizeMin = str(45)  # don't forget ",00" in link!
# searchSizeMax = str(80)
# searchPriceMin = str(500)    # don't forget "EURO" and ",00" in link!
# searchPriceMax = str(1000)


# SCRIPT

# get date and time
currDateTime = datetime.datetime.now()

# create raw data folder
create_folder(path=htmlDataPath, name="html_data")
create_folder(path=htmlDataPath + "\\html_data", name=currDateTime.strftime("%Y%m%d_%H%M"))

# manually set max. result pages
max_pages = 500

for resultPage in range(1, max_pages+1):
    # build result page URL
    pageUrl = build_url(page=resultPage, housing_type=searchHousingType, province=searchProvince)
    # check if URL exists

    # get html data
    raw_html = simple_get(url=pageUrl)
    # save raw html data to file
    save_html(raw_html, htmlDataPath + "\\html_data\\" + currDateTime.strftime("%Y%m%d_%H%M") + "\\immoscout" + "_" +
              currDateTime.strftime("%Y%m%d_%H%M") + "_" +
              "resultPage" + str(resultPage) +    # dont comment out if all result pages are to be scraped
              ".html")

# create empty data frame for saving search results
allDataDf = pd.DataFrame({'Quadratmeter': (), 'Zimmerzahl': (),
                         'Kaltmiete': (), 'Adresse': ()})

# read data from html files
for htmlFile in os.listdir(htmlDataPath + "\\html_data" + "\\20200223_1605"):
    with open(htmlDataPath + "\\html_data" + "\\20200223_1605\\" + htmlFile, "r") as raw_html:
        print(htmlFile)
        try:
            # parse html
            parsedHtml = BeautifulSoup(raw_html, "html.parser")
            # get text from html
            # adresses
            addColText = get_address(html=parsedHtml, housing_type='haus-kaufen')
            # room numbers
            roomColText = get_rooms(html=parsedHtml, housing_type='haus-kaufen')
            # sale prices
            costColText = get_cost(html=parsedHtml, housing_type='haus-kaufen')
            # house sizes
            sizeColText = get_size(html=parsedHtml, housing_type='haus-kaufen')
            # put data into dataframe
            data = {'Quadratmeter': sizeColText, 'Zimmerzahl': roomColText,
                    'Preis': costColText, 'Adresse': addColText}
            allDataDf = allDataDf.append(pd.DataFrame(data), ignore_index=True)
        except UnicodeDecodeError:
            print("Error while trying to decode " + htmlFile)
    
# output data to .csv-file
# allDataDf.to_csv('webData.csv')


##############
# Code-Tests #
##############


