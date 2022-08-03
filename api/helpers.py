from random import randint

import cv2
import requests
from config.environment import *


def getWord():
    words = []
    file = open(wordsPath, 'r')
    words = file.read().splitlines()
    randomIndex = randint(0, len(words))

    while len(words[randomIndex]) >= 6 or len(words[randomIndex]) <= 2:
        randomIndex = randint(0, len(words))

    print(words[randomIndex])
    return words[randomIndex]


def generateWords():
    url = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(url)

    with open(wordsPath, 'w') as f:
        f.write(response.text)
        f.close()


def generateImage(word):

    img = cv2.imread(imgPath)
    cv2.putText(img, word, (100, 130),
                cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 2)
    cv2.imwrite(imageToSendPath, img)


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
