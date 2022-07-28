from cmath import log
from http.client import RemoteDisconnected
from http.server import BaseHTTPRequestHandler
import json
import time
import redis
import telegram
import os
import logging as logger
from telegram.ext import Updater
from urllib.parse import urlparse, parse_qs
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

from config.environment import *
from api.helpers import *
from infra.redis import redisClient
from infra.telegram import *

# TODO: replace if conditions with reducer and dispatcher
# {"group1":"-620006425","temp1":"-1001530624354"}


class handler(BaseHTTPRequestHandler):

    def acknowledgeWebhook(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        token = str(botToken)
        updater = Updater(token, use_context=True)
        updater.bot.setWebhook(
            str(webhookUrl)
        )
        self.acknowledgeWebhook()
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

        if isLeftChatMember(message) != None:
            handleRemovalFromGroup(res)

        elif myChatMember != None and newChatMember["status"] == "member":
            handleAdditionToGroup(myChatMember)

        elif message != None:
            handleReceivedMessage(self, message)

        else:
            logger.debug("unhandled webhook: {} ".format(json.dumps(res)))

        self.acknowledgeWebhook(self)
        return


def sendMsg(self):
    word = getWord()
    generateImage(word)
    print(word)
    groupInfo = redisClient.hgetall(groupData)
    bot = telegram.Bot(token=botToken)

    # Redis Keys
    # group:groupID = word
    # {word}:groupId = {count till now, timestamp}
    # {word:timestamp} = timestamp of send set word
    for key, groupId in groupInfo.items():
        # groupId = str(groupId)
        redisGrpId = "group:" + groupId
        redisWordGrpCount = word + ":" + groupId
        bot.send_photo(groupId, open(imageToSendPath, "rb"))
        redisClient.set(redisGrpId, word)
        redisClient.expire(redisGrpId, 216000)
        redisClient.hmset(redisWordGrpCount, {
            "count": 3, "timestamp": int(time.time())})
        redisClient.expire(redisWordGrpCount, 216000)

    self.acknowledgeWebhook()

    return


def handleAdditionToGroup(myChatMember: dict):
    newChatMember = myChatMember.get("new_chat_member", None)

    if newChatMember != None and str(newChatMember["user"]["id"]) == botId:

        redisClient.hset(
            groupData, myChatMember["chat"]["title"], myChatMember["chat"]["id"])


def handleRemovalFromGroup(res: dict):
    message = res.get("message", None)
    leftChatMember = res["message"]["left_chat_participant"]

    if str(leftChatMember["id"]) == botId:
        res = redisClient.hdel(
            groupData, message["chat"]["title"])


def handleReceivedMessage(self, message: dict):
    if message.get("new_chat_title", None) != None:
        self.acknowledgeWebhook(self)
        return

    if checkIfCommand(message):

        if message["text"] == "/help" or message["text"] == "/start" or message["text"] == ("/help" + str(botName)) or message["text"] == ("/start" + str(botName)):
            handleHelp(message)
            self.acknowledgeWebhook()
            return

        elif message["text"] == "/myscore" or message["text"] == ("/myscore" + str(botName)):
            getUserScoreFromRedis(message)
            self.acknowledgeWebhook()
            return

        elif message["text"] == "/leaderboard" or message["text"] == ("/leaderboard" + str(botName)):
            getLeaderboardFromRedis(message)
            self.acknowledgeWebhook()
            return

    groupId = str(message["chat"]["id"])
    redisGrpId = "group:" + groupId
    word = redisClient.get(redisGrpId) if redisClient.get(
        redisGrpId) != None else None

    whenMsgWasReceived = int(message["date"])
    if word != None:
        redisWordGrpId = word + ":" + groupId
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

    redisKey = "user:" + message["from"]["id"] + \
        ":" + str(message["chat"]["id"])

    redisClient.hmset(
        redisKey, {"userName": message["from"]["userName"]})

    if(timeDiff < 100):
        score = 10
        redisClient.hincrby(redisKey, "score", score)

    elif(timeDiff < 300):
        score = 5
        redisClient.hincrby(redisKey, "score", score)

    else:
        score = 1
        redisClient.hincrby(redisKey, "score", score)


def getUserScoreFromRedis(message: dict):
    userId = message["from"]["id"]
    redisKey = "user_" + userId + \
        "_" + str(message["chat"]["id"])

    score = redisClient.hget(redisKey)
    if score != None:
        updater.bot.send_message(
            message["chat"]["id"], "{name} your score is: {score}".format(name=score["userName"], score=score["score"]))


def handleHelp(message: dict) -> None:
    infoMsg = "👋 Welcome to the WordBot " + message["from"]["first_name"] + "! \n\n" + \
        "WordBot will periodically send a photo containing a word to guess in your group. The user who will write the word first, will win coins. \n\n" + \
        "• /leaderboard: shows the leaderboard of the group. \n\n" + \
        "• /myscore: shows your score for that group."

    updater.bot.send_message(
        message["chat"]["id"], infoMsg)


def getLeaderboardFromRedis(message: dict) -> None:
    redisKey = "user:*:" + str(message["chat"]["id"])

    userScore = dict()

    for key in redisClient.scan_iter(redisKey):
        redisData = redisClient.get(key)
        userScore[redisData["userName"]] = redisData["score"]

    sortedUserScore = sorted(
        userScore.items(), key=lambda x: x[1], reverse=True)

    leaderboardMsg = "🏆 Leaderboard 🏆 \n\n"

    for i in range(0, len(sortedUserScore)):
        leaderboardMsg += "{name} - {score} \n".format(
            name=sortedUserScore[i][0], score=sortedUserScore[i][1])

    if sortedUserScore == []:
        leaderboardMsg += "No users yet!"

    updater.bot.send_message(message["chat"]["id"], leaderboardMsg)
