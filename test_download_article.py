# This is added so that many files can reuse the function get_database()
import datetime
import traceback

import pytz
from bson import ObjectId
from bs4 import BeautifulSoup
from ImportContent import get_contents
from google_colab import replace_attr
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    # This is another valid field
}

r = requests.get("https://hoidapvietjack.com/", verify=False, timeout=10, headers=headers).content
r = r.decode("utf-8")
print("download content")
soups = BeautifulSoup(r)
img = soups.find_all("img")
for web in img:
    try:
        web.replace_with(replace_attr(web, 'data-src', 'src'))
        web.replace_with(replace_attr(web, 'data-lazy-src', 'src'))
        web.replace_with(replace_attr(web, 'lazy-src', 'src'))
        web.replace_with(replace_attr(web, 'data-srcset', 'srcset'))
        web.replace_with(replace_attr(web, 'data-lazy-srcset', 'srcset'))
        web.replace_with(replace_attr(web, 'lazy-srcset', 'srcset'))
        web.replace_with(replace_attr(web, 'data-original', 'src'))
    except:
        pass

    try:
        liii = re.findall("lazy.*=\".*\"", str(web))
        if len(liii) > 0:
            for j in liii:
                hhh = j.split(" ")[0].split("=")[-1]
                if ".JPG" in hhh.upper() or ".PNG" in hhh.upper():
                    web["src"] = hhh
                    break
    except Exception as e:
        print(e)
        traceback.print_exc()
soups = str(soups)
print(soups)
