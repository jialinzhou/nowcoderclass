#   -*- encoding=UTF-8 -*-
import  re
import  urllib

def gethtml(url):
    page = urllib
    page = urllib.urlopen(url)
    html = page.read()
    return html

def getimages(html):
    reg = r'"regular":"(.+?)"'
    imgre = re.compile(reg)
    imglist = re.findall(imgre,html)
    # x = 0
    # for imgurl in imglist:
    #     urllib.urlretrieve(imgurl, './images/%s.jpg' % x)
    #     x += 1
    return  imglist

def getusername(html):
    name = r'"username":"(.+?)","name"'
    namere = re.compile(name)
    namelist = re.findall(namere,html)
    return  namelist

def gethead_url(html):
    head = r'"small":"(https://images.unsplash.com/profile-.+?)"'
    # "small":"https://images.unsplash.com/profile-1462658975816-ed"
    headre = re.compile(head)
    head_urllist = re.findall(headre,html)
    return head_urllist
