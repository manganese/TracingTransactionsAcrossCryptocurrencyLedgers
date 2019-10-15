



# Scraper

There are two scrapers which scrape rates and transactions from the
Shapeshift API. The following sites are scraped

    For Transactions: https://shapeshift.io/recenttx/50
    For Rates: https://shapeshift.io/marketinfo/

The scripts can be found in the scraper folder.
They can be run via Python.
This will run the scraper only once.
The results are saved to a csv file, one csv file per day.
This program can be run once or can be run periodically, I recommend to run it often. 
Json is scraped and processed into a CSV file. If any duplicate transactions are found, these are not added. 
The format for the CSV files created is as follows

transactions_DDMMYYYY.csv

    timestamp,curIn,curOut,amount,txid
    1538521072.372,ETH,BTC,1.38229905,116269

rates_DDMMYYYY.csv

    timestamp,pair,rate,limit,maxLimit,min,minerFee
    1538521203.607979,BCH_DASH,2.92945282,9.26891491,18.53782983,0.00135073,0.002

To run them periodically, the following .sh scripts can be used.
It is recommended to run these as cron jobs or as system daemons.

    scrapeRates.sh
    scrapeTransactions.sh

You can run the following `.sh` files to perform the scraping procedure. 
The log is piped into the txt file. 


    python csvScrapeRates.py >> ratelog.txt
    python csvScrapeTransactions.py >> txlog.txt

