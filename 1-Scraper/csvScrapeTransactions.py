__author__ = 'haaroony'
"""
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

This script will Scrape the most recent 50  transactions of the various coins and combinations. 

It will do the following,
    - Create get request to collect all marketdata shapeshift.io/marketinfo/
    - It does this, it downloads the rates, it saves them to a csv file rates_DDMMYYYY.csv
    - If no file for the day exists, it adds all the rates to the previous file, then saves all current rates
    - If a file already exists then it checks the previous current rates with a diff, it adds only rows which have changed
"""
import requests
import json
import logger
import time
import os
import csv
import sys

path = "transactions/"

def my_handler(type, value, tb):
    logger.logError("Uncaught exception: {0}".format(str(value)))

# Install exception handler
sys.excepthook = my_handler

def pullTransactionData():
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
    filename = path+"transactions_" + time.strftime("%d%m%Y") + ".csv"
    url = "https://shapeshift.io/recenttx/50"
    r = requests.get(url)
    if r.status_code is 200:
        transactions = json.loads(r.text)
        logger.logthis(str("Picked up " + str(len(transactions)) + " transactions."))
        logger.logthis("parsing")
        if not os.path.isfile(filename):
            logger.logthis("File not found, creating new one")
            csvFile = open(filename, "w+")
            csvWriter = csv.writer(csvFile, delimiter=",")
            csvWriter.writerow(["timestamp", "curIn", "curOut", "amount", "txid"])
            csvFile.close()
        else:
            logger.logthis("Appending to existing file")
        # to ensure we dont have duplicates
        inMemCSV = []
        csvFile = open(filename, "r")
        for row in csv.reader(csvFile):
            inMemCSV.append(row)
        csvFile.close()
        dupcount = 0
        with open(filename, "a") as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=",")
            for tx in transactions:
                row =[str(tx['timestamp']), str(tx['curIn']), str(tx['curOut']), str(tx['amount']), str(tx['txid'])]
                if row in inMemCSV:
                    # duplicate found
                    dupcount += 1
                    continue
                csvWriter.writerow(row)
            csvFile.close()
        logger.logthis("Found "+str(dupcount)+" duplicates, Wrote " + str(len(transactions)-dupcount)+ " to file")
        logger.logthis("All transactions have been written to a file")
        logger.logthis("Complete, closing")
    else:
        logger.logthis("Error when pulling the data")
        logger.logthis(str("Status code" + str(r.status_code)))

def main():
    pullTransactionData()

if __name__ == '__main__':
    main()