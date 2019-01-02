from pyalux import Alux
from pprint import pprint

start_page = 1
last_page = -1

print(Alux.num_pages())
for p in Alux.crawl_posts(start_page, last_page):
    pprint(p)
    pprint(Alux.parse_post(p["url"]))

print(Alux.num_trending_pages())
for p in Alux.crawl_trending(start_page, last_page):
    pprint(p)

print(Alux.num_rich_pages())
for p in Alux.crawl_riches(start_page, last_page):
    pprint(p)
    pprint(Alux.parse_networth(p["url"]))
