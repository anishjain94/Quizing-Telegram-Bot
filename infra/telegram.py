from telegram.ext import Updater


from config.environment import *
from api.helpers import *
from infra.redis import redisClient


token = str(botToken)
updater = Updater(token, use_context=True)
updater.bot.setWebhook(
    str(webhookUrl)
)

dp = updater.dispatcher
