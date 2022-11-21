# This is added so that many files can reuse the function get_database()
import traceback

from bson import ObjectId
from bs4 import BeautifulSoup
from ImportContent import get_contents
from google_colab_support import ColabSupport
from Settings import CONNECTION_STRING_MGA1
from googlesearch import search
import requests
import random
from Title_fix import Article
from configuration import Configuration
from urllib.parse import urlparse
from requests import get
import time
import re

filename = get('http://172.28.0.2:9000/api/sessions').json()[0]['name']


def get_database():
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING_MGA1)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client


def replace_attr(soup, from_attr: str, to_attr: str):
    if from_attr in str(soup):
        soup[to_attr] = soup[from_attr]
        del soup[from_attr]

        return soup
    else:
        return soup


client1 = get_database()
lasttime = 0
userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1']
cl = client1.queuekeywords.mlink
url = client1.url_test.data
cl1 = client1.keywords
colab_status = client1.colabstatus.data

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    # This is another valid field
}


def ColabSimple():
    if cl.count_documents({}) > 0:
        try:
            keyword = cl.find_one_and_delete({})
            print("key word: ", keyword)
            if keyword:
                if keyword["campaign"]["language"] == "vi":
                    try:
                        h = 0
                        for i in search(keyword["keyword"], tld="com.vn", start=0, num=20, stop=20, pause=1,
                                        user_agent=random.choice(userAgents), lang="vi", country="vn"):
                            i = i.split("#")[0]

                            h = h + 1
                            if client1.urldone[str(keyword["web_info"]["_id"])].count_documents({"link": i}) > 0:
                                continue
                            domain = urlparse(i).netloc
                            if domain in keyword["web_info"]["Blacklist"]:
                                continue
                            a = [{"link": i, "campaign": keyword["campaign"], "web_info": keyword["web_info"],
                                  "keyword": keyword["keyword"]}]

                            config = Configuration()
                            config.set_language("vi")
                            config.request_timeout = 10
                            config.browser_user_agent = random.choice(userAgents)

                            try:
                                r = requests.get(a[0]["link"], verify=False, timeout=10, headers=headers).content
                                r = r.decode("utf-8")
                                soups = BeautifulSoup(r)
                                img = soups.find_all("img")
                                for i in img:
                                    try:
                                        i.replace_with(replace_attr(i, 'data-src', 'src'))
                                        i.replace_with(replace_attr(i, 'data-lazy-src', 'src'))
                                        i.replace_with(replace_attr(i, 'lazy-src', 'src'))
                                        i.replace_with(replace_attr(i, 'data-srcset', 'srcset'))
                                        i.replace_with(replace_attr(i, 'data-lazy-srcset', 'srcset'))
                                        i.replace_with(replace_attr(i, 'lazy-srcset', 'srcset'))
                                        i.replace_with(replace_attr(i, 'data-original', 'src'))
                                    except:
                                        pass

                                    try:
                                        liii = re.findall("lazy.*=\".*\"", str(i))
                                        if len(liii) > 0:
                                            for j in liii:
                                                hhh = j.split(" ")[0].split("=")[-1]
                                                if ".JPG" in hhh.upper() or ".PNG" in hhh.upper():
                                                    i["src"] = hhh
                                                    break
                                    except Exception as e:
                                        traceback.print_exc()
                                soups = str(soups)
                                article = Article("", keep_article_html=True, config=config)
                                article.download(soups)
                                article.parse()
                                if len(article.text.split(" ")) > 400 and (
                                        "content=\"vi_" in article.html or "lang=\"vi\"" in article.html):
                                    try:
                                        done = get_contents(article, a[0])
                                        if done:
                                            client1.urldone[str(keyword["web_info"]["_id"])].insert_one(
                                                {"link": a[0]["link"]})
                                            break
                                    except Exception as e:
                                        traceback.print_exc()
                                if h == 20:
                                    cl1[keyword['campaign']["WebsiteId"]].update_one(
                                        {"_id": ObjectId(keyword["keyword"]["_id"])}, {"$set": {"status": "fail"}})
                                    break
                            except Exception as e:
                                traceback.print_exc()

                    except Exception as e:
                        print(str(e))
                else:
                    h = 0
                    for i in search(keyword["keyword"], tld="com", start=0, num=20, stop=20, pause=1,
                                    user_agent=random.choice(userAgents), lang="en"):
                        i = i.split("#")[0]
                        h = h + 1
                        if client1.urldone[str(keyword["web_info"]["_id"])].count_documents({"link": i}) > 0:
                            continue
                        domain = urlparse(i).netloc
                        if domain in keyword["web_info"]["Blacklist"]:
                            continue
                        a = [{"link": i, "campaign": keyword["campaign"], "web_info": keyword["web_info"],
                              "keyword": keyword["keyword"]}]

                        config = Configuration()
                        config.request_timeout = 10
                        config.browser_user_agent = random.choice(userAgents)

                        try:
                            r = requests.get(a[0]["link"], verify=False, timeout=10, headers=headers).content
                            r = r.decode("utf-8")

                            soups = BeautifulSoup(r)
                            img = soups.find_all("img")
                            for i in img:
                                try:
                                    i.replace_with(replace_attr(i, 'data-src', 'src'))
                                    i.replace_with(replace_attr(i, 'data-lazy-src', 'src'))
                                    i.replace_with(replace_attr(i, 'lazy-src', 'src'))
                                    i.replace_with(replace_attr(i, 'data-srcset', 'srcset'))
                                    i.replace_with(replace_attr(i, 'data-lazy-srcset', 'srcset'))
                                    i.replace_with(replace_attr(i, 'lazy-srcset', 'srcset'))
                                    i.replace_with(replace_attr(i, 'data-original', 'src'))
                                except:
                                    pass
                                try:
                                    liii = re.findall("lazy.*=\".*\"", str(i))
                                    if len(liii) > 0:
                                        for j in liii:
                                            hhh = j.split(" ")[0].split("=")[-1]
                                            if ".JPG" in hhh.upper() or ".PNG" in hhh.upper():
                                                i["src"] = hhh
                                                break
                                except Exception as e:
                                    traceback.print_exc()
                            soups = str(soups)
                            article = Article("", keep_article_html=True, config=config)
                            article.download(soups)
                            article.parse()
                            if len(article.text.split(" ")) > 400 and (
                                    "content=\"en_" in article.html or "lang=\"en\"" in article.html):
                                try:
                                    done = get_contents(article, a[0])
                                    if done:
                                        client1.urldone[str(keyword["web_info"]["_id"])].insert_one(
                                            {"link": a[0]["link"]})
                                        break
                                except Exception as e:
                                    traceback.print_exc()
                            if h == 20:
                                cl1[keyword['campaign']["WebsiteId"]].update_one(
                                    {"_id": ObjectId(keyword["keyword"]["_id"])}, {"$set": {"status": "fail"}})
                                break
                        except Exception as e:
                            traceback.print_exc()
        except Exception as e:
            traceback.print_exc()
            if "429" in str(e):
                raise ("too many")


while True:

    while True:
        if time.time() - lasttime > 100:
            colab_status.replace_one({'may': filename}, {'may': filename, 'lasttimeupdate': time.time()}, True)
            lasttime = time.time()
        cancle = False
        ColabSimple()
        ColabSupport()
        # except Exception as e:
        if cancle:
            break
            # print(h)
