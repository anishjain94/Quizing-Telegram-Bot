from cgi import print_exception
from html import entities
import os
from random import randint
from turtle import back
import requests
from PIL import ImageDraw
from PIL import ImageFont


from config.environment import *


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


# Generate better imgage
def generateImage(word):
    I1 = ImageDraw.Draw(backgroundImg)
    myFont = ImageFont.truetype(staticFilesPath + '/font.ttf', 30)
    I1.text((100, 100), word, font=myFont, fill=(0, 0, 0))
    os.remove(imageToSendPath)
    backgroundImg.save(imageToSendPath)


def checkIfCommand(message) -> bool:
    entities = message.get("entities", None)
    if entities != None and entities[0]["type"] == "bot_command":
        return True
    else:
        return False


def isLeftChatMember(message: dict) -> bool:
    leftChatMember = message.get(
        "left_chat_participant") if message != None else None

    if leftChatMember is None:
        return False
    else:
        return True
