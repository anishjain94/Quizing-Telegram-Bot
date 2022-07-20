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
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        return

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
        # self.end_headers()
        return