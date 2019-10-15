#!/bin/bash
while true; do
    python csvScrapeTransactions.py >> txlog.txt
    sleep 5
done