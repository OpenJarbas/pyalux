from pyalux import Alux

from pprint import pprint

for post in Alux.trending_videos():
    pprint(post)
    pprint(Alux.parse_video(post["url"]))

for post in Alux.top_videos():
    pprint(post)
    pprint(Alux.parse_video(post["url"]))

for post in Alux.latest_videos():
    pprint(post)
    pprint(Alux.parse_video(post["url"]))

for post in Alux.hottest_videos():
    pprint(post)
    pprint(Alux.parse_video(post["url"]))