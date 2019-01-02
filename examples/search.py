from pyalux import Alux

from pprint import pprint

for post in Alux.search("money"):
    pprint(post)

for post in Alux.search_by_category("Education"):
    pprint(post)

for post in Alux.search_by_tag("rules"):
    pprint(post)
