from http.server import HTTPServer
from dotenv import load_dotenv
import os
import time
from telegram.ext import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
import telebot


from api.webhooks import handler
from config.environment import *
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


load_dotenv()


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), handler)
    print(time.asctime(), f"Server Starts - {HOST_NAME}:{PORT_NUMBER}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), f"Server Stops - {HOST_NAME}:{PORT_NUMBER}")
