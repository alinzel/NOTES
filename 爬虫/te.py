from selenium import webdriver

bro = webdriver.PhantomJS()

bro.get("https://www.bootcdn.cn/")
print(bro.current_url)

import aiohttp
import lxml
from bs4 import BeautifulSoup

soup = BeautifulSoup("<p>hello</p>", "lxml")

print(soup.p.string)

import tesserocr
from PIL import Image

img = Image.open(r"C:\Users\Zwl\Desktop\image.png")
print(tesserocr.image_to_text(img))

import pymysql
print(pymysql.VERSION)

import pymongo
print(pymongo.version)

import redis
print(redis.VERSION)