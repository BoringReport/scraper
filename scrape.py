import datamanager as dm
from datamanager import Sitemap

meta = dm.load_meta()

cnn_links = dm.get_links(Sitemap.CNN)
fox_links = dm.get_links(Sitemap.FOX)

for link in cnn_links:
    dm.add_article(meta, "CNN", link)

for link in fox_links:
    dm.add_article(meta, "FOX", link)

# dm.save_meta(meta)

dm.download(meta, 1000)
dm.save_meta(meta)
