from cmath import log
from distutils.log import Log
from http.server import BaseHTTPRequestHandler
import json
import time
import redis
import telegram
import os
import logging as logger
from infra.redis import redisClient
from telegram.ext import Updater
from urllib.parse import urlparse, parse_qs

from config.environment import *
from api.helpers import *


# TODO: Ask how to reduce the if conditions..
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = str(botToken)
        updater = Updater(token)
        updater.bot.setWebhook(
            str(webhookUrl)
        )

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        return

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        res = json.loads(post_body)
        print(res)

        if self.path == "/sendMsg":
            sendMsg(self)

        myChatMember = res.get("my_chat_member", None)
        newChatMember = myChatMember.get(
            "new_chat_member", None) if myChatMember != None else None

        message = res.get("message", None)
        leftChatMember = message.get(
            "left_chat_participant") if message != None else None

        if leftChatMember != None:
            handleRemovalFromGroup(res)

        elif myChatMember != None and newChatMember["status"] == "member":
            handleAdditionToGroup(myChatMember)

        elif message != None:
            handleReceivedMessage(message)

        else:
            logger.debug("unhandled webhook: {} ".format(json.dumps(res)))

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        return


def sendMsg(self):
    word = getWord()
    generateImage(word)
    print(word)
    groupInfo = redisClient.hgetall(groupData)
    bot = telegram.Bot(token=botToken)

    # Redis Keys
    # group_groupID = word
    # {word}_groupId = {count till now, timestamp}
    # {word_timestamp} = timestamp of send set word
    for key, groupId in groupInfo.items():
        groupId = str(groupId)
        redisGrpId = "group_" + groupId
        redisWordGrpCount = word + "_" + groupId
        bot.send_photo(groupId, open(imageToSendPath, "rb"))
        redisClient.set(redisGrpId, word)
        redisClient.expire(redisGrpId, 216000)
        redisClient.hmset(redisWordGrpCount, {
            "count": 3, "timestamp": int(time.time())})
        redisClient.expire(redisWordGrpCount, 216000)

    self.send_response(200)
    self.send_header('Content-Type', 'text/plain')
    self.end_headers()

    return


def handleAdditionToGroup(myChatMember: dict):
    newChatMember = myChatMember.get("new_chat_member", None)

    if newChatMember != None and str(newChatMember["user"]["id"]) == botId:
        logger.info("Bot added to a group")

        redisClient.hset(
            groupData, myChatMember["chat"]["title"], myChatMember["chat"]["id"])

        logger.info("added group id to redis")


def handleRemovalFromGroup(res: dict):
    logger.debug("removing group Id from redis")
    message = res.get("message", None)
    leftChatMember = res["message"]["left_chat_participant"]

    if str(leftChatMember["id"]) == botId:
        res = redisClient.hdel(
            groupData, message["chat"]["title"])
        print(res)


def handleReceivedMessage(message: dict):
    groupId = str(message["chat"]["id"])
    redisGrpId = "group_" + groupId
    word = redisClient.get(redisGrpId) if redisClient.get(
        redisGrpId) != None else None

    whenMsgWasReceived = int(message["date"])
    if word != None:
        redisWordGrpId = word + "_" + groupId
        wordDataObj = redisClient.hgetall(redisWordGrpId)
        whenWordWasSent = int(wordDataObj["timestamp"])

        wordDataObj["count"] = int(wordDataObj["count"])
        if wordDataObj["count"] > 0:
            wordDataObj["count"] -= 1
            redisClient.hmset(redisWordGrpId, wordDataObj)

            setScoreOfUser(message, whenWordWasSent - whenMsgWasReceived)

            if wordDataObj["count"] <= 1:
                redisClient.delete(redisWordGrpId)
                redisClient.delete(redisGrpId)


def setScoreOfUser(message: dict, timeDiff: int):

    redisKey = "user_" + message["from"]["username"] + \
        "_" + str(message["chat"]["id"])

    if(timeDiff < 100):
        score = 10
        redisClient.incrby(redisKey, score)

    elif(timeDiff < 300):
        score = 5
        redisClient.incrby(redisKey, score)

    else:
        score = 1
        redisClient.incrby(redisKey, score)
