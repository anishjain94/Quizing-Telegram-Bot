import os
from PIL import Image

cwd = os.path.abspath('.')
wordsPath = cwd + '/static/words.txt'
staticFilesPath = cwd + '/static'
backgroundImg = Image.open(staticFilesPath + '/background.jpg')
imageToSendPath = staticFilesPath + '/toSend.jpg'

botToken = os.environ.get("botToken")
webhookUrl = os.environ.get("webhookUrl")
botId = os.environ.get("botId")
botName = os.environ.get("botName")
# Redis
redisHost = os.environ.get("REDIS_HOST")
redisPort = os.environ.get("REDIS_PORT")
redisPassword = os.environ.get("REDIS_PASSWORD")


HOST_NAME = os.environ.get("host", "localhost")
PORT_NUMBER = int(os.environ.get("port", 8000))

groupData = str(botId) + ":groupData"
