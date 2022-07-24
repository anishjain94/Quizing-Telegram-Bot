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

# TODO: Now we have to keep track of all the groups that the bot has been added to and store them in redis using hash.
# TODO: Now when we receive a get request on sendmsg endpoint, we would send a word to all the groups that the bot has been added to.
# TODO: After that we keep track of the messages that we have received and from which grps we have received them.
# TODO: We will decrease the count of that keyword of that group and if it reaches to 0 from 3, we will delete that group from the list.
# TODO: Handle addition and removal from group


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

        else:
            logger.debug("unhandled webhook: {} ".format(json.dumps(res)))

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        return


def sendMsg(self):

    word = getWord()
    print(word)
    generateImage(word)

    groupInfo = redisClient.hgetall(groupData)
    bot = telegram.Bot(token=botToken)

    # bot.send_photo("-1001530624354", open(imageToSendPath, "rb"))

    for key, value in groupInfo.items():
        bot.send_photo(value, open(imageToSendPath, "rb"))

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
