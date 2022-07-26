from cmath import log
from distutils.log import Log
from http.server import BaseHTTPRequestHandler
import json
import redis
import telegram
import os
import logging as logger
from infra.redis import redisClient
from telegram.ext import Updater
from urllib.parse import urlparse, parse_qs

from config.environment import *
from api.helpers import *


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
            handleMessage(message)

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
    # {word}_groupId = count till now
    for key, value in groupInfo.items():
        value = str(value.decode())
        redisGrpId = "group_" + value
        redisWordGrpCount = word + "_" + value
        bot.send_photo(value, open(imageToSendPath, "rb"))
        redisClient.set(redisGrpId, word)
        redisClient.expire(redisGrpId, 216000)
        redisClient.set(redisWordGrpCount, 3)
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


def handleMessage(message: dict):
    groupId = str(message["chat"]["id"])
    redisGrpId = "group_" + groupId
    word = redisClient.get(redisGrpId).decode(
    ) if redisClient.get(redisGrpId) != None else None

    if word != None:
        redisWordGrpId = word + "_" + groupId
        wordCount = int(redisClient.get(redisWordGrpId).decode())

        if wordCount > 0:
            redisClient.decr(redisWordGrpId)
        if wordCount <= 1:
            redisClient.delete(redisWordGrpId)
            redisClient.delete(redisGrpId)
