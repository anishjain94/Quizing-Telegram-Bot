from config.environment import *
from api.helpers import *

from infra.redis import redisClient
from telegram.ext import Updater

token = str(BOT_TOKEN)
updater = Updater(token, use_context=True)
