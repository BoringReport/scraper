import sys

from newspaper import Article, fulltext
import json
from tqdm import tqdm
from enum import Enum
import requests
import xml.etree.ElementTree as et
from pymongo import MongoClient
import datetime
from datetime import timezone
import pytz

class Sitemap(Enum):
    CNN = "https://www.cnn.com/sitemaps/article-2021-03.xml"
    FOX = "https://www.foxnews.com/sitemap.xml?type=articles&from=1613063599000"

def get_date_info(publication):
    print (publication)
    if publication == "CNN":
        return ('%Y-%m-%dT%H:%M:%SZ', True)
    elif publication == "FOX":
        return ('%Y-%m-%dT%H:%M:%S%z', False)
    else:
        return ('%Y-%m-%dT%H:%M:%S%z', False)

def get_datetime(publication, time_string):
    if ":" == time_string[-3:-2]:
        time_string = time_string[:-3]+time_string[-2:]
    date_format, should_localize = get_date_info(publication)
    date = datetime.datetime.strptime(time_string, date_format)
    if should_localize:
        date = pytz.utc.localize(date)
    return date

def get_links(sitemap):
    links = []

    r = requests.get(sitemap.value).text

    root = et.fromstring(r)
    
    for child in root:
        links.append((child[0].text, child[1].text))
    
    return links

def download(meta, limit=None, if_in_last_n_days=None):
    downloaded = 0
    for i in tqdm(range(len(meta['articles']))):
        if limit is not None and downloaded >= limit:
            break
        article = meta['articles'][i]
        lastmod = get_datetime(article['publication'], article['lastmod'])
        if if_in_last_n_days is not None:
            if (datetime.datetime.now(timezone.utc) - lastmod).days > if_in_last_n_days:
                continue
        if 'failures' in article:
            if article['failures'] > 5:
                continue
        if not article['downloaded']:
            ar = Article(article['loc'])
            try:
                ar.download()
                ar.parse()

                article['downloaded'] = True
                article['title'] = ar.title
                article['authors'] = ar.authors
                if ar.publish_date is not None:
                    article['publish_date'] = ar.publish_date.strftime("%m/%d/%Y, %H:%M:%S")

                filename = '/home/ubuntu/scraper/data/{}.txt'.format(article['localId'])
                write_article_file(filename, ar.text)

                downloaded = downloaded + 1

                add_article_to_mongo(article)
            except:
                print ('error downloading: {}'.format(article['loc'], ''))
                print(sys.exc_info())
                article['downloaded'] = False
                if 'failures' in article:
                    article['failures'] = article['failures'] + 1
                else:
                    article['failures'] = 1
    print ("downloaded {} articles".format(downloaded))

def contains(meta, loc):
    articles = meta['articles']
    for article in meta['articles']:
        if article['loc'] == loc:
            return True 
    return False

def load_meta():
    with open('/home/ubuntu/scraper/meta.json') as data:
        meta = json.load(data)
        return meta

def save_meta(meta):
    with open('/home/ubuntu/scraper/meta.json', 'w') as fp:
        json.dump(meta, fp)

def write_article_file(filename, text):
    with open(filename, 'w') as a:
        a.write(text)

def add_article(meta, publication, loc, lastmod):
    if not contains(meta, loc):
        meta['articles'].append({
            'localId': abs(hash(loc)),
            'publication': publication,
            'loc': loc,
            'lastmod': lastmod,
            'downloaded': False
        })

        return True
    return False

def add_article_to_mongo(article):
    lastmod_string = article['lastmod']
    article = article.copy()
    article["date_added"] = datetime.datetime.utcnow()
    article["lastmod"] = get_datetime(article['publication'], lastmod_string)

    client = MongoClient('localhost', 27017)
    db = client["boring-report"]

    article_id = db.articles.insert_one(article).inserted_id
    