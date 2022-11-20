from pickle import TRUE
from newspaper import Config
from sys import prefix
from pymongo import MongoClient
import time
import html.parser    
import requests
from requests.models import HTTPBasicAuth
from Settings import *
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from SpinService import *
import json
from unidecode import unidecode
from Title_fix import *
from aiohttp import request
import requests
import json
import base64
import html
import html.parser  
from Settings import *
from bson import ObjectId
from pymongo import MongoClient
import time
from PIL import Image
import io
from unidecode import unidecode
from aiohttp import request
from extract import ContentExtractor
from lxml.html import tostring
from difflib import SequenceMatcher

spinService = SpinService()

config = Config()
campaign_root  = MongoClient(CONNECTION_STRING_MGA1).campaignsupport.data
keywords  = MongoClient(CONNECTION_STRING_MGA1).keywordssuport
contenttier  = MongoClient(CONNECTION_STRING_MGA1).contenttier
contentcycle  = MongoClient(CONNECTION_STRING_MGA1).contentcycle

contentExtractor = ContentExtractor(config)
from bs4 import BeautifulSoup
def replace_attr(soup, from_attr: str, to_attr: str):
    if from_attr in str(soup):
        soup[to_attr] = soup[from_attr]
        del soup[from_attr]

        return soup
    else:
        return soup


def process_content(article,url,self_url,first_tier_link,first_tier_title):
    
        article["article_html"] = str(html.unescape(article["article_html"]))

        soup = BeautifulSoup(article["article_html"], 'html.parser')

        domain = urlparse(url["link"]).netloc
        img = soup.find_all("img")
        src_img = []
        pre_link = None
        for i in img:
            try:
                if i.has_attr("src"):
                    if i["src"] in src_img:
                        i.decompose()
                    else:
                        if "http" in i["src"]:
                            src_img.append(i["src"])
                        elif i["src"]  =="":
                            i.decompose()
                        elif i["src"][:2] =="//" and "." in i["src"][3:].split("/")[0] and "jpg" not in i["src"][3:].split("/")[0]  and "png" not in i["src"][3:].split("/")[0]:
                            i["src"] = "http:" + i["src"]
                            src_img.append(i["src"])
                        else:
                            i["src"] = "http://"+domain +i["src"]
                            src_img.append(i["src"])

                elif i.has_attr("srcset"):
                    if i["srcset"] in src_img:
                        i.decompose()
                    else:
                        if "http" in i["srcset"]:
                            src_img.append(i["srcset"])
                        elif i["srcset"]  =="":
                            i.decompose()
                        elif i["srcset"][:2] =="//" and "." in i["srcset"][3:].split("/")[0] and "jpg" not in i["srcset"][3:].split("/")[0]  and "png" not in i["srcset"][3:].split("/")[0]:
                            i["srcset"] = "http" + i["srcset"]
                            src_img.append(i["srcset"])
                        else:
                            i["srcset"] = "http://"+domain +i["srcset"]
                            src_img.append(i["srcset"])
            except Exception as e:
                print(e)

        thumb = None
        if len(src_img)>0:
            try:
                for iii in range(5):
                    thumb = random.choice(src_img)
                    if ".PNG" in thumb or ".JPG" in thumb:
                        break
            except:
                pass
        # print(src_img)


        if url["campaign"]["CategoryId"]!=None and url["campaign"]["CategoryName"]!=None and url["campaign"]["CategoryLink"]!=None:
            # print(acate_name)
            cate_name = url["campaign"]["CategoryName"]
            cate_link = url["campaign"]["CategoryLink"]
        else:
            cate_name = None
            cate_link = None
        article["article_html"] = str(soup)
        paper = html.unescape(article["article_html"])
        paper = BeautifulSoup(paper,"html.parser")
        for elem in paper.find_all(['a']):
            elem.unwrap()
        domain = domain.split(".")
        domain[-2] = list(domain[-2])
        domain[-2][0] = ".?"
        domain[-2][-1] = ".?"
        domain[-2][2] = ".?"
        domain[-2][-2] = ".?"
        domain[-2] = "".join(domain[-2])
        domain = ".".join(domain)
        article["title"] = re.sub(re.compile(domain),url["web_info"]["Website"],article["title"])
        titles = []
        for i in article["title"].split(" "):
            if ".com" in i or ".org" in i or ".vn" in i or ".us" in i or ".mobi" in i or ".gov" in i or ".net" in i or ".edu" in i or ".info" in i:
                titles.append(url["web_info"]["Website"])
            else:
                titles.append(i)
        article["title"] = " ".join(titles)

        for elem in paper.find_all(["img"],{"alt":re.compile("https://"+domain)}):
            elem['alt'] =re.sub(re.compile("https://"+domain),url["web_info"]["Website"],elem['alt'])
        for elem in paper.find_all(text = re.compile("https://"+domain)):
            elem = elem.replace_with(re.sub(re.compile("https://"+domain),url["web_info"]["Website"],elem))
        heading_p = []
        for heading in soup.find_all(["h1", "h2", "h3"]):
            for p in heading.find_all("p"):
                heading_p.append(p)
        thepp =  paper.find_all('p')
        thep = []
        for i in thepp:
            if i not in heading_p:
                thep.append(i)
        max_match_index = 0
        size_match = 1
        first_match_string = url["keyword"]["Keyword"][0]
        for a,j in enumerate(thep):
            j_string= j.text
            if j_string!= None:
                match = SequenceMatcher(None,url["keyword"]["Keyword"], j_string).find_longest_match(0, len(url["keyword"]["Keyword"]), 0, len(j_string))
                if match.size>size_match:
                    match_b = match.b
                    match_size =match.size
                    max_match_index = a
                    if match_b>0:
                        while j_string[match_b-1]!=" " and j_string[match_b-1]!="\n" and j_string[match_b-1]!="." and j_string[match_b-1]!="," and j_string[match_b-1]!="!" and match_b>0:
                            match_b = match_b -1 
                            match_size = match_size+1
                    if match_b+match_size< len(j_string):
                        while j_string[match_b+match_size]!=" " and j_string[match_b+match_size]!="\n" and j_string[match_b+match_size]!="." and j_string[match_b+match_size]!="," and j_string[match_b+match_size]!="!" and match_b+match_size< len(j_string):
                            match_size = match_size+1
                    first_match_string = j_string[match_b:match_b+match_size]
                    size_match = match_size
        thep[max_match_index].replace_with(BeautifulSoup("<p>"+str(thep[max_match_index]).replace(first_match_string,"<a href='{}'>{}</a>".format(url["keyword"]["linksupport"],url["keyword"]["keywordsupport"]),1)+"</p>"))


        self_link_p_tag =  '<div style="margin-bottom:15px;margin-top:15px;"><p style="padding: 20px; background: #eaf0ff;">Bạn đang đọc: <a target="_blank" href="{}" rel="bookmark" title="{}">{}</a> </p></div>'.format(url["web_info"]["Website"]+'/'+self_url,article["title"],article["title"])


        self_link_p_tag = BeautifulSoup(self_link_p_tag,"html.parser")
        try:
            thep[min(len(thep),3)].append(self_link_p_tag)
        except:
            pass
        if first_tier_link !="" and first_tier_title != "":

            internal_link3 = first_tier_link
            internal_link_title3 = first_tier_title
            internal_link_p_tag3 =  '<div style="margin-bottom:15px;margin-top:15px;"><p style="padding: 20px; background: #eaf0ff;">Xem ngay: <a target="_blank" href="{}" rel="bookmark" title="{}">{}</a></p></div>'.format(url["web_info"]["Website"]+'/'+internal_link3,internal_link_title3,internal_link_title3)
            internal_link_p_tag3 = BeautifulSoup(internal_link_p_tag3,"html.parser")
            if len(thep)>3:
                thep[len(thep)-3].append(internal_link_p_tag3)
            else:
                paper.append(internal_link_p_tag3)
        else:
            if url["campaign"]["Top10url"]!=None and url["campaign"]["Top10url"]!=[]:
                if len(url["campaign"]["Top10url"])>0:
                    internal_link_total = random.choice(url["campaign"]["Top10url"])
                    internal_link3 = internal_link_total["link"]
                    internal_link_title3 = internal_link_total["name"]
                    internal_link_p_tag3 =  '<div style="margin-bottom:15px;margin-top:15px;"><p style="padding: 20px; background: #eaf0ff;">Xem thêm: <a target="_blank" href="{}" rel="bookmark" title="{}">{}</a></p></div>'.format(internal_link3,internal_link_title3,internal_link_title3)
                    internal_link_p_tag3 = BeautifulSoup(internal_link_p_tag3,"html.parser")
                    if len(thep)>3:
                        thep[len(thep)-3].append(internal_link_p_tag3)
                    else:
                        paper.append(internal_link_p_tag3)


        if cate_link and cate_name:
            nguon = '<div style="margin-bottom:15px;margin-top:15px;"><p style="padding: 20px; background: #eaf0ff;">Source: <a target="_blank" href="{}" rel="bookmark" title="{}">{}</a> <br> Category: <a target="_blank" href="{}" rel="bookmark" title="{}">{}</a> </p></div>'.format(url["web_info"]["Website"]+'/',url["web_info"]["Website"],url["web_info"]["Website"],cate_link,cate_name,cate_name)

            nguon = BeautifulSoup(nguon,"html.parser")
        else:
            nguon = '<div style="margin-bottom:15px;margin-top:15px;"><p style="padding: 20px; background: #eaf0ff;">Source: <a target="_blank" href="{}" rel="bookmark" title="{}">{}</a>'.format(url["web_info"]["Website"]+'/',url["web_info"]["Website"],url["web_info"]["Website"])
            nguon = BeautifulSoup(nguon,"html.parser")

        paper.append(nguon)
        listp = [{"ptag":m,"keywords":url["keyword"]["Keyword"],"linksp":url["keyword"]["linksupport"],"language":url["campaign"]["language"]} for m in paper.find_all("p")]
        resultp= []
        try:
            for i in listp:
                if i["language"]== "vi":
                    resultp.append(spinService.spin_paragraph(i["ptag"],i["keywords"]))
                else:
                    resultp.append(spinService.spin_paragraph_en(i["ptag"],i["keywords"]))

            for k1,k2 in zip(listp,resultp):
                k1["ptag"].replace_with(k2)
        except:
            pass
        paper = str(paper)
        paper  = paper.replace("&lt;","<")
        paper  = paper.replace("&gt;",">")
        paper= paper.replace(" . ", ". ")
        paper = paper.replace(" , ", ", ")
        try:
            if url["web_info"]["Email_replace"]!='':
                match = re.findall(r'[\w\.-]+@[\w\.-]+', paper)
                email = url["web_info"]["Email_replace"]
                for i in match:
                    paper = paper.replace(i,email)

            if len(url["web_info"]["Text_replace_doc"].keys())>0:
                for i in url["web_info"]["Text_replace_doc"].keys():
                    paper = paper.replace(i,url["web_info"]["Text_replace_doc"][i])
        except:
            pass
        content = {
            "user":url,
            "title":article["title"],
            "content":str(paper),
            "category":url["campaign"]["CategoryId"],
            "url_img":thumb,
            "src_img":src_img,
            "slug":self_url

        }
        
        return content



def restImgUL(website,user,password,urlimg,src_img):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',  # This is another valid field
    }
    newID = None
    if urlimg ==None:
        return newID
    else:
        try:
            path_files = urlimg.split("/")[-1].split("?")[0]
            with requests.get(urlimg,stream=True,allow_redirects=False,verify=False,timeout=50,headers=headers) as response:
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    image = image.resize((900,603))
                    output = io.BytesIO()
                    credentials = user + ':' + password
                    token = base64.b64encode(credentials.encode())
                    if "JPG" in path_files.upper():
                        image.save(output,format='JPEG',optimize = True,quality = 30)
                        headers={ 'Authorization': 'Basic ' + token.decode('utf-8'),'Content-Type': 'image/jpeg','Content-Disposition' : 'attachment; filename=%s'%path_files}

                    elif "PNG" in path_files.upper():
                        image.save(output,format='PNG',optimize = True,quality = 30)
                        headers={ 'Authorization': 'Basic ' + token.decode('utf-8'),'Content-Type': 'image/png','Content-Disposition' : 'attachment; filename=%s'%path_files,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
                    image = output.getvalue()

                    with requests.post(website,
                        data=image,
                        headers=headers,timeout=10) as response:
                            res = response.json(encoding="utf-8")
                            newID= res.get('id')
                            return newID
        except Exception as e:
            print(str(e))
            return None

def importcontent(content):



    #cl = await clientt.user["userdatabase"].find_one({'_id':ObjectId(content['UserId'])})
    cl = content['user']["web_info"]
    website = cl["WebsitePost"]
    websiteimg  = cl["Website"] + "/wp-json/wp/v2/media"
    user = cl["UserWP"]
    password = cl["PasswordWP"]
    idthump=None

    idthump =  restImgUL(websiteimg,user,password,content['url_img'],content["src_img"])
    if idthump == None:
        idthump = content['user']["web_info"]["imageid"]
    # if len(a_link) == len(content['src_img']):
    #     for i,j in zip(content['src_img'],a_link):
    #         content["content"] = content["content"].replace(i,j)
    credentials = user + ':' + password
    token = base64.b64encode(credentials.encode())
    header = {'Authorization': 'Basic ' + token.decode('utf-8'),'Content-Type': 'application/json','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    post = {
        'status': 'publish', 
        "title":content["title"],
        "content":content["content"],
        'categories':content["category"],
        'featured_media':int(idthump),
        'slug': content['slug'] 
    }

    with requests.post(website , headers=header,json = post) as response:
        res = response.status_code
    if res!=None:
        print(res)
        print(post["slug"])
        url = content['user']["campaign"]
        if url["Top10url"] == None or url["Top10url"] == []:
            url["Top10url"] = [{"link":content['user']["web_info"]["Website"] +"/"+ post['slug'],"name":content["title"]}]
        elif len(url["Top10url"])<10:
            url["Top10url"].append({"link":content['user']["web_info"]["Website"] +"/"+ post['slug'],"name":content["title"]})
        else:
            url["Top10url"]= [{"link":content['user']["web_info"]["Website"] +"/"+ post['slug'],"name":content["title"]}] + url["Top10url"][1:10]

        campaign_root.update_one({"_id":ObjectId( content['user']["campaign"]["_id"])},{"$set":{"Top10url":url["Top10url"]}})
        keywords[content['user']['campaign']["WebsiteId"]].update_one({"_id":ObjectId( content['user']["keyword"]["_id"])},{"$set":{"status":"done","link":content['user']["web_info"]["Website"] +"/"+ post['slug']}})

        return True
    else:
        return False

def ImportContentssp(article,url):
    self_url = unidecode(url["keyword"]["Keyword"])+ ' ' + str(time.time()).split(".")[0]
    self_url = self_url.replace(" ","-")
    self_url = self_url.replace(".","")
    article = {
        "article_html":article.article_html,
        "title":article.title
    }
    if url["keyword"]["tier"] == 1:
        numbercount = contenttier.data.count({"campaignid":str(url["campaign"]["_id"])})
        if numbercount==0:
            keywords[url['campaign']["WebsiteId"]].update_one({"_id":ObjectId( url["keyword"]["_id"])},{"$set":{"status":"waiting_import","link":url["web_info"]["Website"] +"/"+ self_url}})
            if url["campaign"]["MaxTier"]>url["keyword"]["tier"]:
                url["campaign"]["queue_support_keyword"].append(url["keyword"]["_id"])
                campaign_root.update_one({"_id":ObjectId( url["campaign"]["_id"])},{"$set":{"queue_tier":url["campaign"]["queue_tier"],"FirstCircle":False,"queue_support_keyword": url["campaign"]["queue_support_keyword"]}})

            contenttier.data.insert_one({"campaignid":str(url["campaign"]["_id"]),"tt":url,"article_html":article["article_html"],"title":article["title"],"self_url":self_url,"last_circle_link":self_url,"last_circle_tile":article["title"]})
            done = True
        else:
            text = contenttier.data.find_one({"campaignid":str(url["campaign"]["_id"])})
            done = importcontent(process_content(article,url,self_url,text["last_circle_link"],text["last_circle_tile"]))
            if done:
                contenttier.data.update_one({"_id":text["_id"]},{"$set":{"last_circle_link":self_url,"last_circle_tile":article["title"]}})
        return done
    else:
        ct = process_content(article,url,self_url,"","")
        done = importcontent(ct)
        if url["campaign"]["MaxTier"]>url["keyword"]["tier"]:
            url["campaign"]["queue_support_keyword"].append(url["keyword"]["_id"])
            campaign_root.update_one({"_id":ObjectId( url["campaign"]["_id"])},{"$set":{"queue_tier":url["campaign"]["queue_tier"],"FirstCircle":False,"queue_support_keyword": url["campaign"]["queue_support_keyword"]}})
        return done
def update_tier1(url):
    if contenttier.data.count({"campaignid":str(url["campaign"]["_id"])})>=1:
        numbercount = contenttier.data.count({"campaignid":str(url["campaign"]["_id"])})
        text = []
        text1 = contenttier.data.find_one_and_delete({"campaignid":str(url["campaign"]["_id"])})
        text.append(text1)
        for i in range(len(text)):
            if text[i]["last_circle_tile"] == text[i]["title"]:
                text[i]["last_circle_link"] = ""
                text[i]["last_circle_tile"] = ""
            article1 = {
                "article_html":text[i]["article_html"],
                "title":text[i]["title"]
            }
            url["keyword"] = text[i]["tt"]["keyword"]
            importcontent(process_content(article1,url,text[i]["self_url"],text[i]["last_circle_link"],text[i]["last_circle_tile"]))
    contenttier.data.delete_many({"campaignid":str(url["campaign"]["_id"])})


