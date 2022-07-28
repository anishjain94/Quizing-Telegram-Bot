from cmath import log
from http.server import BaseHTTPRequestHandler
import json
from pickle import TRUE
import time
import redis
import telegram
import os
import logging as logger
from infra.redis import redisClient
from telegram.ext import Updater
from urllib.parse import urlparse, parse_qs
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters


from config.environment import *
from api.helpers import *


token = str(botToken)
updater = Updater(token, use_context=TRUE)
updater.bot.setWebhook(
    str(webhookUrl)
)

dp = updater.dispatcher
