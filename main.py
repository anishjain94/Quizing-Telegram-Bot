from http.server import HTTPServer
from dotenv import load_dotenv
import os
import time
from telegram.ext import Updater
from api.webhooks import handler

load_dotenv()

# HOST_NAME = os.environ.get("host", "localhost")
# PORT_NUMBER = int(os.environ.get("port", 8000))

HOST_NAME = "localhost"
PORT_NUMBER = 8000

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
