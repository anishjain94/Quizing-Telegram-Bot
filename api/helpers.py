from random import randint
from datetime import datetime
import cv2
import requests


from config.environment import *


def getWord():
    words = []
    file = open(wordsPath, 'r')
    words = file.read().splitlines()
    randomIndex = randint(0, len(words))

    while len(words[randomIndex]) >= 7 or len(words[randomIndex]) <= 3:
        randomIndex = randint(0, len(words))

    print(words[randomIndex])
    return words[randomIndex].lower()


def generateWords():
    url = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(url)

    with open(wordsPath, 'w') as f:
        f.write(response.text)
        f.close()


def generateImage(word):

    img = cv2.imread(imgPath)
    if len(word) == 4:
        cv2.putText(img, word, (140, 130),
                    cv2.FORMATTER_FMT_PYTHON, 1, (0, 0, 0), 2)

    if len(word) == 5:
        cv2.putText(img, word, (133, 130),
                    cv2.FORMATTER_FMT_CSV, 1, (0, 0, 0), 2)

    if len(word) == 6:
        cv2.putText(img, word, (127, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

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


def minsToAns(seconds: int) -> str:
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%02dm %02ds" % (minutes, seconds)
