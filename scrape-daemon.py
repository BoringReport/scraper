import datamanager as dm
from datamanager import Sitemap
import time
import sys

while True:
    meta = dm.load_meta()

    cnn_links = []
    fox_links = []

    try:
        cnn_links = dm.get_links(Sitemap.CNN)
        fox_links = dm.get_links(Sitemap.FOX)
    except:
        print ('failed to get links')
        print(sys.exc_info())

    for link in cnn_links:
        dm.add_article(meta, "CNN", link)

    for link in fox_links:
        dm.add_article(meta, "FOX", link)

    dm.download(meta, 1000)
    dm.save_meta(meta)

    time.sleep(60)
