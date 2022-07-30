from dotenv import load_dotenv
from flask import Flask


from api.webhooks import *
from config.environment import *


load_dotenv()

app = Flask(__name__)


@app.route("/health_check")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/", methods=['POST'])
def handleIncomingWebhooks():
    do_POST()
    return "OK"


@app.route("/send_message", methods=['GET'])
def handleSendMessage():
    sendMsg()
    return "OK"


# if __name__ == '__main__':
#     server_class = HTTPServer
#     httpd = server_class((HOST_NAME, PORT_NUMBER), handler)
#     print(time.asctime(), f"Server Starts - {HOST_NAME}:{PORT_NUMBER}")
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     httpd.server_close()
#     print(time.asctime(), f"Server Stops - {HOST_NAME}:{PORT_NUMBER}")
