from cgi import print_exception
import os
from random import randint
from turtle import back
import requests
from environment import *

from PIL import ImageDraw
from PIL import ImageFont


def getWord():
    words = []
    file = open(wordsPath, 'r')
    words = file.read().splitlines()
    randomIndex = randint(0, len(words))
    return words[randomIndex]


def generateWords():
    url = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(url)

    with open(wordsPath, 'w') as f:
        f.write(response.text)
        f.close()


def generateImage(word):
    I1 = ImageDraw.Draw(backgroundImg)
    myFont = ImageFont.truetype(staticFilesPath + 'font.ttf', 30)
    I1.text((50, 50), word, font=myFont, fill=(0, 0, 0))
    backgroundImg.save(staticFilesPath + 'toSend.jpg')
