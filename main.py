#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

#    with open(filename, "w") as file:
#        file.write(pretty_html)


def build_url_with_filters(page, housing_type, province, city, room_min, room_max,
                           size_min, size_max, price_min, price_max):
    """
    Builds the search site urls according to some filters set in the script.
    TO DO: merge with other build_url function.
    """
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


def build_url(page, housing_type, province, city):
    """
    Builds the search site urls according to some filters set in the script.
    """
    url = ("https://www.immobilienscout24.de/Suche/S-T/" +
           "P-" + str(page) + "/" +
           "Wohnung-" + housing_type + "/" +
           province + "/" +
           city)
    return url


def get_address(html):
    """
    Get address from html file.
    """
    item_selection = html.select('div > button div')
    add_col = list()
    for i, j in enumerate(item_selection, 1):
        add_col.append(j.getText())
    # filter empty list entries
    add_col = list(filter(None, add_col))
    return add_col


def get_cost(html):
    """
    Get cost from html file.
    """
    item_selection = html.find_all(class_="font-nowrap font-line-xs")
    cost_col = list()
    for i, j in enumerate(item_selection, 1):
        if i % 3 == 0 and i != 0:
            cost_col.append(j.getText()[0])
    return cost_col


def get_rooms(html):
    """
    Get number of rooms from html file.
    """
    item_selection = html.find_all(class_="font-nowrap font-line-xs")
    room_col = list()
    for i, j in enumerate(item_selection, 1):
        if (i+2) % 3 == 0 and i != 0:
            room_col.append(j.getText())
    return room_col


def get_size(html):
    """
    Get dwelling size from html file.
    """
    item_selection = html.find_all(class_="font-nowrap font-line-xs")
    size_col = list()
    for i, j in enumerate(item_selection, 1):
        if (i+1) % 3 == 0 and i != 0:
            size_col.append(j.getText())
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
No filter except of city:
    "https://www.immobilienscout24.de/Suche/S-T/P-2/Wohnung-Miete/Nordrhein-Westfalen/Koeln"
"""
        

# SEARCH SETTINGS

# required inputs
searchHousingType = "Miete"
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

# manually set max. result pages
max_pages = 1
# create empty data frame for saving search results
allDataDf = pd.DataFrame({'Quadratmeter': (), 'Zimmerzahl': (),
                         'Kaltmiete': (), 'Adresse': ()})

for resultPage in range(1, max_pages+1):
    # build result page URL
    pageUrl = build_url(page=resultPage, housing_type=searchHousingType, province=searchProvince, city=searchCity)
    # check if URL exists

    # get html data
    raw_html = simple_get(url=pageUrl)
    # save raw html data to file
    save_html(raw_html, "immoscout" + "_" +
              currDateTime.strftime("%Y%m%d_%H%M") + "_" +
              "resultPage" + str(resultPage) +    # dont comment out if all result pages are to be scraped
              ".html")
    # parse html
    parsedHtml = BeautifulSoup(raw_html, "html.parser")
    # get text from html
    addColText = get_address(html=parsedHtml)
    roomColText = get_rooms(html=parsedHtml)
    costColText = get_cost(html=parsedHtml)
    sizeColText = get_size(html=parsedHtml)
    # put data into dataframe
    data = {'Quadratmeter': sizeColText, 'Zimmerzahl': roomColText,
            'Kaltmiete': costColText, 'Adresse': addColText}
    allDataDf = allDataDf.append(pd.DataFrame(data), ignore_index=True)
    
# output data to .csv-file
allDataDf.to_csv('webData.csv')   


##############
# Code-Tests #
##############
