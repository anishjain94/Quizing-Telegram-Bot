from http.server import BaseHTTPRequestHandler
import json
import telegram
import redis
import os
from telegram.ext import Updater
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = str(os.environ.get("botToken"))
        updater = Updater(token)
        updater.bot.setWebhook(
            str(os.environ.get("webhookUrl"))
        )

        if self.path == "/sendMsg":
            sendMsg(self)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        return

# TODO: Now we have to keep track of all the groups that the bot has been added to and store them in redis.
# TODO: Now when we receive a get request on sendmsg endpoint, we would send a word to all the groups.
# TODO: After that we keep track of the messages that we have received and from which grps we have received them.
# TODO: We will decrease the count of that keyword of that group and if it reaches to 0 from 3, we will delete that group from the list.

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        res = json.loads(post_body)
        print(res)

        # send message to telegram
        # token = str(os.environ.get("botToken"))
        # updater = Updater(token)
        # updater.bot.send_message(
        #     res["message"]["chat"]["id"], res["message"]["text"])
        # telegram.Update.message.reply_to_message.text = res["message"]

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        return


def sendMsg(self):
    return
