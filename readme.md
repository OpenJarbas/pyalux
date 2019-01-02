# PyAlux

Home of Luxury & Fine Living Enthusiasts! 

Find luxury with this unofficial api for [Alux.com](https://www.alux.com/)

wth pyalux you can find:

* articles
* videos
* celebrities
* net worth of rich people

## Install

    pip install pyalux
    
## Usage

More examples [here](/examples)

    from pyalux import Alux    
    
    for post in Alux.search("money"):
        print(post)
        
    for post in Alux.search_by_category("Education"):
        print(post)
    
    for p in Alux.crawl_posts(start_page, last_page):
        print(p)
        print(Alux.parse_post(p["url"]))
        
    for p in Alux.crawl_riches(start_page, last_page):
        print(p)
        print(Alux.parse_networth(p["url"]))
        
    for post in Alux.top_videos():
        print(post)
        print(Alux.parse_video(post["url"]))
