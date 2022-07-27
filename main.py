from http.server import HTTPServer
from dotenv import load_dotenv
import os
import time
from telegram.ext import Updater
from api.webhooks import handler

from config.environment import *


load_dotenv()

# HOST_NAME = os.environ.get("host", "localhost")
# PORT_NUMBER = int(os.environ.get("port", 8000))


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), handler)
    print(time.asctime(), f"Server Starts - {HOST_NAME}:{PORT_NUMBER}")

    token = str(botToken)
    updater = Updater(token)
    updater.bot.setWebhook(
        str(webhookUrl)
    )
    updater.dispatcher.add_handler(
        CommandHandler('start', startCommandHandler))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), f"Server Stops - {HOST_NAME}:{PORT_NUMBER}")


# TODO: Use reducer and dispatcher to handle conditions
# mediator('subtract')


# def add():
#     pass

def dummy():
    pass

# def sub(a, b):
#     return b - a

# listOfActions = { 'add': add, 'subtract': sub, None: dummy }

# def mediator(res):
#     if res == 'add':
#         return listOfActions['add'](res)
#     elif res == 'subtract':
#         return listOfActions['subtract'](res)
