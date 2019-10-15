#!/bin/bash
while true; do
    python csvScrapeRates.py >> ratelog.txt
    sleep 5
done