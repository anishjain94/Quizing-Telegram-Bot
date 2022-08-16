import os

cwd = os.path.abspath('.')
wordsPath = cwd + '/static/words.txt'
staticFilesPath = cwd + '/static'
imgPath = staticFilesPath + '/background.jpg'
imageToSendPath = staticFilesPath + '/toSend.jpg'

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
BOT_ID = os.environ.get("BOT_ID")
BOT_NAME = os.environ.get("BOT_NAME")
# Redis
redisHost = os.environ.get("REDIS_HOST")
redisPort = os.environ.get("REDIS_PORT")
redisPassword = os.environ.get("REDIS_PASSWORD")


HOST_NAME = os.environ.get("host", "localhost")
PORT_NUMBER = int(os.environ.get("port", 8000))

groupData = str(BOT_ID) + ":groupData"
