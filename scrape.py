import datamanager as dm
from datamanager import Sitemap

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
    loc, lastmod = link
    dm.add_article(meta, "CNN", loc, lastmod)

for link in fox_links:
    loc, lastmod = link
    dm.add_article(meta, "FOX", loc, lastmod)

dm.download(meta, limit=1000, if_in_last_n_days=3)
dm.save_meta(meta)
