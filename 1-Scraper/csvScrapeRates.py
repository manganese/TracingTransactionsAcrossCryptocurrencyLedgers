__author__ = 'haaroony'
'''


 .d8888b. 888                              .d8888b. 888     d8b .d888888    
d88P  Y88b888                             d88P  Y88b888     Y8Pd88P" 888    
Y88b.     888                             Y88b.     888        888   888    
 "Y888b.  88888b.  8888b. 88888b.  .d88b.  "Y888b.  88888b. 888888888888888 
    "Y88b.888 "88b    "88b888 "88bd8P  Y8b    "Y88b.888 "88b888888   888    
      "888888  888.d888888888  88888888888      "888888  888888888   888    
Y88b  d88P888  888888  888888 d88PY8b.    Y88b  d88P888  888888888   Y88b.  
 "Y8888P" 888  888"Y88888888888P"  "Y8888  "Y8888P" 888  888888888    "Y888 
                          888                                               
                          888                                               
                          888                                              

This script will Scrape the Rate of the various coins and combinations. 

It will do the following,
    - Create get request to collect all marketdata shapeshift.io/marketinfo/
    - It does this, it downloads the rates, it saves them to a csv file rates_DDMMYYYY.csv
    - If no file for the day exists, it adds all the rates to the previous file, then saves all current rates
    - If a file already exists then it checks the previous current rates with a diff, it adds only rows which have changed
'''

import requests
import json
import logger
import time
import os
import csv
import sys
from decimal import *
path= "rates/"

# Config variables, so i dont make a spelling mistake
text_timestamp = "timestamp"
text_pair = "pair"
text_rate = "rate"
text_limit = "limit"
text_maxlimit = "maxLimit"
text_min = "min"
text_minerfee = "minerFee"


# handles code exceptions
def my_handler(type, value, tb):
    logger.logError("Uncaught exception: {0}".format(str(value)))


# Install exception handler
sys.excepthook = my_handler


# generates a row for the csv file
def makeRow(timestamp, rateX, addTimeStamp):
    '''
    Creating a row properly, with empty parts if need be
    :param timestamp:
    :param rateX:
    :param addTimeStamp:
    :return:
    '''
    pair = "Unknown"
    rate = 0
    limit = 0
    maxLimit = 0
    min = 0
    minerFee = 0.0

    if text_pair in rateX:
        pair = rateX[text_pair]
    if text_rate in rateX:
        rate = rateX[text_rate]
    if text_limit in rateX:
        limit = rateX[text_limit]
    if text_maxlimit in rateX:
        maxLimit = rateX[text_maxlimit]
    if text_min in rateX:
        min = rateX[text_min]
    if text_minerfee in rateX:
        minerFee = rateX[text_minerfee]

    if addTimeStamp:
        row = (timestamp, pair, rate, limit, maxLimit, min, minerFee)
    else:
        row = (pair, rate, limit, maxLimit, min, minerFee)

    return row


# converts a json to a list object
def jsonTolist(data, addTimestamp):
    '''
    coverts loaded json to list, simple as
    :param data:
    :param addTimestamp:
    :return:
    '''
    timestamp = time.time()
    listFormat = list()
    for rateX in data:
        if addTimestamp:
            row = makeRow(timestamp, rateX, True)
            listFormat.append(row)
        else:
            row = makeRow(0, rateX, False)
            listFormat.append(row)
    return listFormat


# downloads the rates from shapeshift
def pullAllTheRates():
    if not os.path.exists(path):
        logger.logError("Path (%s) doesnt exist. Creating new path'" % path)
        try:
            os.mkdir(path)
            if not os.path.exists(path):
                logger.logError("Path (%s) creation failed. Exiting" % path)
                sys.exit(1)
            else:
                logger.logthis("Path created")
        except FileExistsError:
            logger.logError("Folder (%s) already exists" % path)
    todaysDate = time.strftime("%d%m%Y")
    filename = path+"rates_"+todaysDate+".csv"
    logger.logthis("Path : " + path)
    url = "https://shapeshift.io/marketinfo/"
    r = requests.get(url)
    timestamp = time.time()
    if r.status_code is 200:
        rates = json.loads(r.text)
        logger.logthis(str("Picked up " + str(len(rates)) + " rates."))
        logger.logthis("Parsing into a file")
        # if file dont exist create it
        if not os.path.isfile(filename):
            logger.logthis("File not found, creating new one")
            csvFile = open(filename, "w+")
            csvWriter = csv.writer(csvFile, delimiter=",")
            csvWriter.writerow([text_timestamp, text_pair, text_rate, text_limit, text_maxlimit, text_min, text_minerfee])
            csvFile.close()
        else:
            logger.logthis("Appending to existing file")

        # Create temp file
        previousFile = path+"rates"+todaysDate+"_last.json"
        # if the file dont exist create it then add all the rates
        if not os.path.isfile(previousFile):
            logger.logthis("last file not found, creating new one")
            jsonFile = open(previousFile, "w+")
            json.dump(rates, jsonFile)
            jsonFile.close()
            # then add all the rates to the current file as it must be empty
            with open(filename, "a") as csvFile:
                csvWriter = csv.writer(csvFile, delimiter=",")
                for rateX in rates:
                    rowToWrite = makeRow(timestamp, rateX, True)
                    csvWriter.writerow(rowToWrite)
                csvFile.close()
        else:
            # if we already have a _last file, we need to compare what rates have changed and only add those
            # create a new temp file
            logger.logthis("Last file found")
            logger.logthis("Comparing current rates to previous")
            tempFile = path+"rates_temp.json"
            jsonFileTemp = open(tempFile, "w+")
            json.dump(rates, jsonFileTemp)
            jsonFileTemp.close()
            # diff it with the last file
            newRows = list()
            oldRows = list()

            with open(tempFile, "r") as nf:
                dataTemp = json.load(nf)
                newRows = jsonTolist(dataTemp, False)
            nf.close()
            with open(previousFile, "r") as pf:
                dataTemp = json.load(pf)
                oldRows = jsonTolist(dataTemp, False)
            pf.close()
            # add the diff'ed entries to the main file
            diff = set(newRows) - set(oldRows)
            if len(diff):
                logger.logthis("Found " + str(len(diff)) + " rate changes, adding")
                with open(filename, "a") as csvFile:
                    csvWriter = csv.writer(csvFile, delimiter=",")
                    for rateX in diff:
                        row = [timestamp, rateX[0], rateX[1], rateX[2], rateX[3], rateX[4], rateX[5]]
                        csvWriter.writerow(row)
                    csvFile.close()
            else:
                logger.logthis("Found no new rates, not adding")
            # remove the last file
            os.remove(previousFile)
            # rename temp to last
            os.rename(tempFile, previousFile)
        logger.logthis("Rates, if any, have been written to todays file closing")
    else:
        logger.logthis("Error when pulling the data")
        logger.logthis(str("Status code" + str(r.status_code)))


def main():
    logger.logthis("\n**START**")
    pullAllTheRates()


if __name__ == '__main__':
    main()
