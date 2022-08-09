from config.environment import *
from flask import Flask
from api.webhooks import *
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


# TODO: Handle message reply on bot, and when a message is received. send a acknowlegdement to the user.

@app.route("/health")
def hello_world():
    return "Healthy."


@app.route("/", methods=['POST'])
def handleIncomingWebhooks():
    handleIncomingWebhook()
    return "OK"


@app.route("/send_message", methods=['POST'])
def handleSendMessage():
    sendMsg()
    return "OK"


@app.route("/set_webhook", methods=['POST'])
def handleSetWebhook():
    setWebhook()
    return "OK"
