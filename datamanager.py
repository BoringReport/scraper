import sys

from newspaper import Article, fulltext
import json
from tqdm import tqdm
from enum import Enum
import requests
import xml.etree.ElementTree as et

class Sitemap(Enum):
    CNN = "https://www.cnn.com/sitemaps/article-2021-03.xml"
    FOX = "https://www.foxnews.com/sitemap.xml?type=articles&from=1613055203000"

def get_links(sitemap):
    links = []

    r = requests.get(sitemap.value).text
    root = et.fromstring(r)
    
    for child in root:
        links.append(child[0].text)

    return links

def download(meta, limit=None):
    downloaded = 0
    for i in tqdm(range(len(meta['articles']))):
        if limit is not None and i == limit:
            break
        article = meta['articles'][i]
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

                filename = 'data/{}.txt'.format(article['id'])
                write_article_file(filename, ar.text)

                downloaded = downloaded + 1 
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
    with open('meta.json') as data:
        meta = json.load(data)
        return meta

def save_meta(meta):
    with open('meta.json', 'w') as fp:
        json.dump(meta, fp)

def write_article_file(filename, text):
    with open(filename, 'w') as a:
        a.write(text)

def add_article(meta, publication, loc):
    if not contains(meta, loc):
        meta['articles'].append({
            'id': abs(hash(loc)),
            'publication': publication,
            'loc': loc,
            'downloaded': False
        })

        return True
    return False
