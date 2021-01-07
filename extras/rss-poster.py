import feedparser
import requests
import random
from bs4 import BeautifulSoup

# Hacker News
url1 = "https://hnrss.org/frontpage"
feed1 = feedparser.parse(url1)
for post in feed1.entries:
        # date = "(%d/%02d/%02d)" % (post.published_parsed.tm_year,\
        #     post.published_parsed.tm_mon, \
        #     post.published_parsed.tm_mday)
        # print("post date: " + date)
        # print("post title: " + post.title)
        # print("post description: " + post.description)
        # print("post link: " + post.link)

        # Thread Icons: art, attention, banme, computers, en, event, fap, funny, gaming, gross, help, hot, letsplay, link, music, newbie, news, photos, politics, poll, postyour, question, rant, release, repeat, request, school, serious, shitpost, stupid, tv, unfunny, weird, whine
        random_choices = ['art', 'attention', 'link', 'news', 'rant', 'release', 'repeat', 'serious', 'stupid', 'unfunny', 'weird']
        icon = random.choice(random_choices)
        #icon = "special-hackernews"
        query_url = "http://127.0.0.1:5000/api/site/"
        query_data = {"api": "INVALID_API",\
                "create_thread": "true",\
                "username": "admin",\
                "category": "news",\
                "content": BeautifulSoup(post.description).get_text(),\
                "title": post.title,\
                "icon": icon,\
                "anon": "0"}
        r = requests.post(query_url, query_data)
        print(r.text)

# BBC International
url2 = "http://feeds.bbci.co.uk/news/rss.xml?edition=int"
feed2 = feedparser.parse(url2)
for post in feed2.entries:
        # date = "(%d/%02d/%02d)" % (post.published_parsed.tm_year,\
        #     post.published_parsed.tm_mon, \
        #     post.published_parsed.tm_mday)
        # print("post date: " + date)
        # print("post title: " + post.title)
        # print("post description: " + post.description)
        # print("post link: " + post.link)

        # Thread Icons: art, attention, banme, computers, en, event, fap, funny, gaming, gross, help, hot, letsplay, link, music, newbie, news, photos, politics, poll, postyour, question, rant, release, repeat, request, school, serious, shitpost, stupid, tv, unfunny, weird, whine
        random_choices = ['art', 'attention', 'link', 'news', 'rant', 'release', 'repeat', 'serious', 'stupid', 'unfunny', 'weird']
        icon = random.choice(random_choices)
        #icon = "special-bbcworld"
        query_url = "http://127.0.0.1:5000/api/site/"
        query_data = {"api": "INVALID_API",\
                "create_thread": "true",\
                "username": "admin",\
                "category": "news",\
                "content": BeautifulSoup(post.description).get_text() + "\n\n" + post.link,\
                "title": post.title,\
                "icon": icon,\
                "anon": "0"}
        r = requests.post(query_url, query_data)
        print(r.text)