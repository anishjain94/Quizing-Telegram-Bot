import json
import logging as logger
import time

from config.constants import *
from config.environment import *
from flask import request
from infra.redis import redisClient
from infra.telegram import *
from telegram.ext import Updater
from api.helpers import *


def setWebhook():
    token = str(BOT_TOKEN)
    updater = Updater(token, use_context=True)
    res = request.get_json()
    webhookUrl = res.get("webhook_url", None)
    updater.bot.setWebhook(
        webhookUrl
    )
    return


def handleIncomingWebhook():
    res = request.get_json()
    print(res)
    myChatMember = res.get("my_chat_member", None)
    newChatMember = myChatMember.get(
        "new_chat_member", None) if myChatMember != None else None

    message = res.get("message", None)

    if isLeftChatMember(message) != False:
        handleRemovalFromGroup(res)

    elif myChatMember != None and newChatMember["status"] == "member":
        handleAdditionToGroup(myChatMember)

    elif message != None:
        handleReceivedMessage(message)

    else:
        logger.debug("unhandled webhook: {} ".format(json.dumps(res)))

    return


def sendMsg():
    print("starting timer")
    word = getWord()
    generateImage(word)
    groupInfo = redisClient.hgetall(groupData)
    # Redis Keys
    # group:groupID = word
    # {word}:groupId = {count till now, timestamp}
    # {word:timestamp} = timestamp of send set word
    for key, groupId in groupInfo.items():
        # groupId = str(groupId)
        redisGrpId = "group:" + groupId
        redisWordGrpCount = word + ":" + groupId
        try:
            updater.bot.send_photo(groupId, open(
                imageToSendPath, "rb"), caption=imageCaption)
        except Exception as e:
            print(e)
            continue
        redisClient.set(redisGrpId, word)
        redisClient.expire(redisGrpId, 216000)
        redisClient.hmset(redisWordGrpCount, {
            "count": 3, "timestamp": int(time.time())})
        redisClient.expire(redisWordGrpCount, 216000)
    return


def handleAdditionToGroup(myChatMember: dict):
    newChatMember = myChatMember.get("new_chat_member", None)

    if newChatMember != None and str(newChatMember["user"]["id"]) == BOT_ID:

        redisClient.hset(
            groupData, myChatMember["chat"]["title"], myChatMember["chat"]["id"])


def handleRemovalFromGroup(res: dict):
    message = res.get("message", None)
    leftChatMember = res["message"]["left_chat_participant"]

    if str(leftChatMember["id"]) == BOT_ID:
        res = redisClient.hdel(
            groupData, message["chat"]["title"])


def handleReceivedMessage(message: dict):
    if message.get("new_chat_title", None) != None:
        return

    if checkIfCommand(message):
        if message["text"] == "/help" or message["text"] == "/start" or message["text"] == ("/help" + str(BOT_NAME)) or message["text"] == ("/start" + str(BOT_NAME)):
            handleHelp(message)
            return

        elif message["text"] == "/myscore" or message["text"] == ("/myscore" + str(BOT_NAME)):
            getUserScoreFromRedis(message)
            return

        elif message["text"] == "/leaderboard" or message["text"] == ("/leaderboard" + str(BOT_NAME)):
            getLeaderboardFromRedis(message)
            return
        return

    groupId = str(message["chat"]["id"])
    redisGrpId = "group:" + groupId
    word = redisClient.get(redisGrpId)

    whenMsgWasReceived = int(message["date"])
    messageReceived = message.get("text", None)

    if messageReceived == None:
        return

    messageReceived = messageReceived.lower()
    if word != None and (messageReceived is not None and messageReceived == word):
        redisWordGrpId = word + ":" + groupId
        wordDataObj = redisClient.hgetall(redisWordGrpId)
        whenWordWasSent = int(wordDataObj["timestamp"])

        wordDataObj["count"] = int(wordDataObj["count"])
        if wordDataObj["count"] > 0:
            wordDataObj["count"] -= 1
            redisClient.hmset(redisWordGrpId, wordDataObj)

            setScoreOfUser(message, whenMsgWasReceived - whenWordWasSent)

            if wordDataObj["count"] <= 1:
                redisClient.delete(redisWordGrpId)
                redisClient.delete(redisGrpId)


def setScoreOfUser(message: dict, timeDiff: int):

    redisKey = "user:" + str(message["from"]["id"]) + \
        ":" + str(message["chat"]["id"])

    redisClient.hmset(
        redisKey, {"userName": message["from"]["username"]})

    score = 1

    if(timeDiff < 100):
        score = 10
        redisClient.hincrby(redisKey, "score", score)

    elif(timeDiff < 300):
        score = 5
        redisClient.hincrby(redisKey, "score", score)

    else:
        score = 1
        redisClient.hincrby(redisKey, "score", score)

    sendSuccessMsg(message, timeDiff)


def sendSuccessMsg(message: dict, timeDiff: int = 0):
    userId = str(message["from"]["id"])
    redisKey = "user:" + userId + \
        ":" + str(message["chat"]["id"])

    score = redisClient.hgetall(redisKey)
    print(score)
    if not score:
        updater.bot.send_message(
            message["chat"]["id"], "No Score found @" + message["chat"]["username"])
    elif score != None:
        updater.bot.send_message(
            message["chat"]["id"], successMessage.format(name=score["userName"], score=score["score"], time=minsToAns(timeDiff)))


def getUserScoreFromRedis(message: dict):
    userId = str(message["from"]["id"])
    redisKey = "user:" + userId + \
        ":" + str(message["chat"]["id"])

    score = redisClient.hgetall(redisKey)
    print(score)
    if not score:
        updater.bot.send_message(
            message["chat"]["id"], "No Score found @" + message["chat"]["username"])
    elif score != None:
        updater.bot.send_message(
            message["chat"]["id"], scoreIs.format(name=score["userName"], score=score["score"]))


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
        redisData = redisClient.hgetall(key)
        print(redisData)
        userScore[redisData["userName"]] = redisData["score"]

    sortedUserScore = sorted(
        userScore.items(), key=lambda x: x[1], reverse=True)

    leaderboardMsg = "🏆 Leaderboard 🏆 \n\n"

    for i in range(0, len(sortedUserScore)):
        leaderboardMsg += str(i + 1) + ": @{userName} your score is: {score} \n".format(
            userName=sortedUserScore[i][0], score=sortedUserScore[i][1])

    if sortedUserScore == []:
        leaderboardMsg += "No users yet!"

    updater.bot.send_message(message["chat"]["id"], leaderboardMsg)
