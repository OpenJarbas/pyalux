from pyalux import Alux

from pprint import pprint

pprint(Alux.random_rich())

for rich in Alux.crawl_riches():
    pprint(rich)
    pprint(Alux.parse_networth(rich["url"]))

for rich in Alux.latest_riches():
    pprint(rich)

for rich in Alux.trending_riches():
    pprint(rich)

for rich in Alux.richest_presidents():
    pprint(rich)

for rich in Alux.richest_directors():
    pprint(rich)

for rich in Alux.richest_youtube_personalities():
    pprint(rich)

url = "https://www.alux.com/networth/vladimir-putin/"
pprint(Alux.parse_networth(url))

url = "https://www.alux.com/richest/athlete/"
for rich in Alux.parse_richest(url):
    pprint(rich)
