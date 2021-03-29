#!/bin/sh

# start scrape
nohup python3 /home/ubuntu/scraper/scrape-daemon.py > /var/log/scrape.log 2>&1 &