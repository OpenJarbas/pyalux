import requests
from bs4 import BeautifulSoup
from pyalux.exceptions import InvalidCategoryException, InvalidTagException, \
    UnknownPageFormatException, NoArticlesFoundException, \
    UnknownUrlException, BadPostException, NoVideosFoundException, \
    NotVideoUrlException, NotNetworthUrlException, NoRichestFoundException, \
    NotRichestUrlException


class Alux(object):

    @staticmethod
    def _get_html(url):
        return requests.get(url, verify=False).text

    @staticmethod
    def _get_soup(html):
        return BeautifulSoup(html, 'html.parser')

    @staticmethod
    def num_pages(url="http://www.alux.com/page/1"):
        soup = Alux._get_soup(Alux._get_html(url))
        next_page = soup.find("div", {"class": "navigation"}).find_all("a")
        if next_page[-1].text == "»":
            next_page = next_page[-2]
        else:
            next_page = next_page[-1]
        return int(next_page.text)

    @staticmethod
    def num_trending_pages():
        url = "http://www.alux.com/trending/page/1"
        return Alux.num_pages(url)

    @staticmethod
    def num_rich_pages():
        url = "https://www.alux.com/networth/page/1"
        return Alux.num_pages(url)

    @staticmethod
    def _get_posts(soup):
        if isinstance(soup, str) and soup.startswith("http"):
            soup = Alux._get_soup(Alux._get_html(soup))
        # main page
        el = soup.find("div", {"class": "item post-listing"})
        if not el:
            # category / trending pages
            el = soup.find("div", {"class": "post-listing"})
            if not el:
                # tag / search pages
                el = soup.find("div", {"class": "grid-listing"})

        if not el:
            raise UnknownPageFormatException
        articles = el.find_all("article")
        if not articles:
            raise NoArticlesFoundException
        for a in articles:
            category = a.find("a", {"class": "category"})
            if category:
                category = category.text
            else:
                category = ""
            content = a.find("div", {"class": "entry-content"})
            if content:
                title = content.find("h3", {"class":
                                                "entry-title"}).text.strip()
                url = content.find("a")["href"]
                content = content.find("p").text
                yield {"title": title, "url": url, "category": category,
                       "summary": content}
            else:
                # probably an ad to amazon
                continue

    @staticmethod
    def crawl(base_url="http://www.alux.com", page=1, last_page=1,
              total_pages=None, soup_handler=None):
        if requests.get(base_url, verify=False).status_code == 404:
            raise UnknownUrlException
        total_pages = total_pages or Alux.num_pages()
        if str(page).startswith("http"):
            url = page
            page = int(page.split("/")[-2])
        else:
            page = int(page)
            if page < 0:
                page = total_pages - page
            url = base_url + "/page/" + str(page)
        if total_pages < page:
            page = total_pages

        soup = Alux._get_soup(Alux._get_html(url))
        nav = soup.find("div", {"class": "navigation"})

        if nav is not None:
            next_page = nav.find_all("a")[-1]
            if int(next_page["href"].split("/")[-2]) == page:
                return
            last_page = 1
            page = 2

        soup_handler = soup_handler or Alux._get_posts
        for a in soup_handler(soup):
            yield a

        if last_page > 0 and page > last_page:
            return

        for p in Alux.crawl(base_url, next_page["href"]):
            yield p

    @staticmethod
    def crawl_posts(page=1, last_page=1):
        for p in Alux.crawl("http://www.alux.com", page, last_page):
            yield p

    @staticmethod
    def crawl_trending(page=1, last_page=1):
        for p in Alux.crawl("http://www.alux.com/trending", page, last_page,
                            total_pages=Alux.num_trending_pages()):
            yield p

    @staticmethod
    def parse_post(url):
        soup = Alux._get_soup(Alux._get_html(url))
        el = soup.find(id="thepost")
        if el is None:
            raise BadPostException
        tags = el.find("div", {"class": "the-tags"})
        tags = [t.text for t in tags.find_all("a")]
        content = el.find("div", {"class": "the-content"})
        title = content.find("h2")
        if title:
            title = title.text
        else:
            title = url.replace("https://www.alux.com/", "") \
                .replace("/", "").replace("-", " ")
        date = content.find("meta", {"itemprop": "datePublished"})["content"]
        paragraphs = content.find_all("p")
        parsed = {"title": title, "post": content.text, "tags": tags,
                  "youtube_videos": [], "date": date, "parsed": []}
        bucket = {"idx": 0, "subtitle": "intro", "entry": ""}
        num = 0
        for p in paragraphs:
            subtitle = p.find("strong")
            bucket["entry"] += p.text + "\n"
            if subtitle:
                subtitle = subtitle.text

                if "alux.com" not in subtitle:
                    parsed["parsed"].append(bucket)
                    num += 1
                    if "number" in subtitle.lower():
                        # n = subtitle.lower().split(":")[0].replace("number", "").strip()
                        subtitle = subtitle.split(":")[1].strip()
                    bucket["entry"] = ""
                    bucket["idx"] = num
                    bucket["subtitle"] = subtitle

            iframe = p.find("iframe")
            if iframe:
                vid_url = iframe["src"]
                if "youtube.com/embed" in vid_url:
                    parsed["youtube_videos"].append(vid_url)
        return parsed

    @staticmethod
    def search_by_category(category):
        url = "https://www.alux.com/category/" + category
        if requests.get(url, verify=False).status_code == 404:
            raise InvalidCategoryException
        for post in Alux._get_posts(url):
            yield post

    @staticmethod
    def search_by_tag(tag):
        url = "https://www.alux.com/tag/" + tag
        try:
            for post in Alux._get_posts(url):
                yield post
        except UnknownPageFormatException:
            raise InvalidTagException

    @staticmethod
    def search(query):
        url = "https://www.alux.com/?s=" + query
        try:
            for post in Alux._get_posts(url):
                yield post
        except UnknownPageFormatException:
            raise NoArticlesFoundException

    @staticmethod
    def _get_videos(soup):
        if isinstance(soup, str) and soup.startswith("http"):
            soup = Alux._get_soup(Alux._get_html(soup))
        el = soup.find("div", {"class": "video-listing"})
        if not el:
            el = soup.find("div", {"class": "post-listing"})
            if not el:
                raise NoVideosFoundException

        videos = soup.find_all("li", {"class": "video-widget wideimg"})
        if not videos:
            videos = el.find_all("article")
            if not videos:
                raise NoVideosFoundException

        for v in videos:
            v = v.find("div", {"class": "post-img"})
            url = v.find("a")["href"]
            pic = v.find("img")["src"]
            title = v.find("a")["title"]
            yield {"url": url, "pic": pic, "title": title}

    @staticmethod
    def parse_video(url):
        if "/video/" not in url:
            raise NotVideoUrlException
        soup = Alux._get_soup(Alux._get_html(url))
        title = soup.find("h1", {"class": "entry-title"}).text
        url = soup.find("div", {"class": "video-layer"}).find("iframe")["src"]
        return {"url": url, "title": title}

    @staticmethod
    def top_videos():
        url = "https://www.alux.com/"
        soup = Alux._get_soup(Alux._get_html(url))
        for v in Alux._get_videos(soup):
            yield v

    @staticmethod
    def trending_videos():
        url = "https://www.alux.com/videos"
        soup = Alux._get_soup(Alux._get_html(url))
        for v in Alux._get_videos(soup):
            yield v

    @staticmethod
    def hottest_videos():
        url = "https://www.alux.com/videos/?sort=hottest"
        soup = Alux._get_soup(Alux._get_html(url))
        for v in Alux._get_videos(soup):
            yield v

    @staticmethod
    def latest_videos():
        url = "https://www.alux.com/videos/?sort=latest"
        soup = Alux._get_soup(Alux._get_html(url))
        for v in Alux._get_videos(soup):
            yield v

    @staticmethod
    def parse_networth(url):
        if "/networth/" not in url:
            raise NotNetworthUrlException
        soup = Alux._get_soup(Alux._get_html(url))
        info = soup.find("div", {"class": "the-info"})
        if info is None:
            raise BadPostException
        name = info.find("h4").text
        networth = info.find("p", {"class": "networth"}).text \
            .replace("Net Worth", "").strip()
        salary = info.find("p", {"class": "salary"}).text \
            .replace("Salary:", "").strip()
        info = info.find_all("li")
        bucket = {"url": url, "name": name, "networth": networth,
                  "salary": salary}
        for i in info:
            key = i.find("span").text.replace(":", "").strip()
            a = i.find("a")
            if a is not None:
                data = a.text
                data_url = a["href"]
            else:
                data = i.text.replace(key + ":", "").strip()
                data_url = url
            bucket[key.lower().strip()] = data
        text = soup.find("div", {"class": "celebrity-content"}).text
        bucket["info"] = text.strip()
        return bucket

    @staticmethod
    def richest_politicians():
        url = "https://www.alux.com/richest/politician/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_producers():
        url = "https://www.alux.com/richest/producer/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_presidents():
        url = "https://www.alux.com/richest/president/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_talk_show_hosts():
        url = "https://www.alux.com/richest/talk-show-host/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_directors():
        url = "https://www.alux.com/richest/director/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_youtube_personalities():
        url = "https://www.alux.com/richest/youtube-personality/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_lyricists():
        url = "https://www.alux.com/richest/lyricist/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_stuntmans():
        url = "https://www.alux.com/richest/stuntman/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_athletes():
        url = "https://www.alux.com/richest/athlete/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_boxers():
        url = "https://www.alux.com/richest/boxer/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_record_producers():
        url = "https://www.alux.com/richest/record-producers/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_entrepeneurs():
        url = "https://www.alux.com/richest/entrepeneur/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_socialites():
        url = "https://www.alux.com/richest/socialite/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_entertainers():
        url = "https://www.alux.com/richest/entertainer/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_songwriters():
        url = "https://www.alux.com/richest/songwriter/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_authors():
        url = "https://www.alux.com/richest/author/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_businessman():
        url = "https://www.alux.com/richest/businessman"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_television_hosts():
        url = "https://www.alux.com/richest/television-host/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_media_proprietors():
        url = "https://www.alux.com/richest/media-proprietor/"
        return Alux.parse_richest(url)

    @staticmethod
    def richest_basketball_players():
        url = "https://www.alux.com/richest/basketball-player/"
        return Alux.parse_richest(url)

    @staticmethod
    def parse_richest(url):
        if "/richest/" not in url:
            raise NotRichestUrlException
        soup = Alux._get_soup(Alux._get_html(url))
        for rich in Alux._get_rich(soup):
            yield rich

    @staticmethod
    def _get_rich(soup):
        if isinstance(soup, str) and soup.startswith("http"):
            soup = Alux._get_soup(Alux._get_html(soup))
        el = soup.find("div", {"class": "celebrity-listing"})
        if not el:
            raise NoRichestFoundException
        for rich in el.find_all("article"):
            url = rich.find("a")["href"]
            pic = rich.find("img")["src"]
            name = rich.find("h3", {"class": "celeb-title"}).text \
                .replace("Net Worth", "").strip()
            yield {"url": url, "pic": pic, "name": name}

    @staticmethod
    def random_rich():
        url = "https://www.alux.com/networth/"
        soup = Alux._get_soup(Alux._get_html(url))
        url = soup.find("a", {"class": "randomceleb"})["href"]
        return Alux.parse_networth(url)

    @staticmethod
    def trending_riches():
        url = "https://www.alux.com/networth/"
        soup = Alux._get_soup(Alux._get_html(url))
        soup = soup.find("div", {"class": "trending-celebs"})
        return Alux._get_rich(soup)

    @staticmethod
    def latest_riches():
        url = "https://www.alux.com/networth/"
        soup = Alux._get_soup(Alux._get_html(url))
        soup = soup.find("div", {"class": "latest-celebs"})
        return Alux._get_rich(soup)

    @staticmethod
    def crawl_riches(page=1, last_page=1):
        url = "https://www.alux.com/networth/"

        def handler(soup):
            soup = soup.find("div", {"class": "latest-celebs"})
            return Alux._get_rich(soup)

        for p in Alux.crawl(url, page, last_page, Alux.num_rich_pages(),
                            soup_handler=handler):
            yield p
