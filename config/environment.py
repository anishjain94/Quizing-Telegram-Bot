import os
from PIL import Image
from telegram import Update

cwd = os.path.abspath('.')
wordsPath = cwd + '/static/words.txt'
staticFilesPath = cwd + '/static'
backgroundImg = Image.open(staticFilesPath + '/background.jpg')
imageToSendPath = staticFilesPath + '/toSend.jpg'

botToken = os.environ.get("botToken")
webhookUrl = os.environ.get("webhookUrl")
botId = os.environ.get("botId")

# Redis
redisHost = os.environ.get("REDIS_HOST")
redisPort = os.environ.get("REDIS_PORT")
redisPassword = os.environ.get("REDIS_PASSWORD")

# TODO: update this.
groupData = str(botId) + "_group_data"
