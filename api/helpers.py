from random import randint
import requests
from PIL import Image, ImageDraw, ImageFont

from time import sleep


from config.environment import *


def getWord():
    words = []
    file = open(wordsPath, 'r')
    words = file.read().splitlines()
    randomIndex = randint(0, len(words))

    while len(words[randomIndex]) >= 7 or len(words[randomIndex]) <= 3:
        randomIndex = randint(0, len(words))

    print(words[randomIndex])
    sleepTimer = randint(0, 1000)
    sleep(sleepTimer)

    return (words[randomIndex].capitalize())


def generateWords():
    url = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(url)

    with open(wordsPath, 'w') as f:
        f.write(response.text)
        f.close()


def create_image(size, message, font, fontColor):
    W, H = size
    image = Image.open(imgPath)
    draw = ImageDraw.Draw(image)

    w, h = draw.textsize(message, font=font)
    draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
    return image


def generateImage(myMessage: str):
    myFont = ImageFont.truetype(fontPath, 200)
    myImage = create_image((1900, 1050), myMessage, myFont, '#a5a58d')
    myImage.save(imageToSendPath, "PNG")


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


def minsToAns(seconds: int) -> str:
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%02dm %02ds" % (minutes, seconds)
