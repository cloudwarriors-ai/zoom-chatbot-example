
from flask import Flask, request
import json
import requests
import dotenv
import os
import logging
import sys
import base64
# Set up logging



#load the environment variables from .env file


dotenv.load_dotenv()



zoomClientId = os.getenv("zoomClientId")
zoomClientSecret = os.getenv("zoomClientSecret")

#create a base 64 encoded string of the client id and client secret with a colon in between

# create a base 64 encoded string of the client id and client secret with a colon in between
encode_auth = zoomClientId + ":" + zoomClientSecret

# encode the string to bytes
encode_auth_base64 = encode_auth.encode('utf-8')

# encode the bytes to base 64
userid_cid_base64 = base64.b64encode(encode_auth_base64)

userid_cid_base64 = userid_cid_base64.decode('ascii')
("zoomClientId :"+zoomClientId)

print("userid :"+userid_cid_base64)

app = Flask(__name__)

app.logger.info("Starting the app...")

auth_token = None
# create a data object to send to the zoom api

def create_data_object(to_jid, user_jid, robot_jid, account_id, message):
    data = {
        "content": {
            "head": {
                "type": "message",
                "text": "Life ain't nuthin but bits and money"
            },
            "body": [
                {
                    "type": "message",
                    "text": f"{message}"
                }
            ]
        },
        "to_jid": f"{to_jid}",
        "user_jid": f"{user_jid}",
        "robot_jid": f"{robot_jid}",
        "account_id": f"{account_id}"
        
    }
    return data

#write an authorization function to get the auth token

def get_auth_token():
    app.logger.info("getting auth token...")
    url = "https://zoom.us/oauth/token?grant_type=client_credentials"
    headers = {
        "Authorization": f"Basic {userid_cid_base64}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    app.logger.info(response.json())
    return response.json()['access_token']

auth_token = get_auth_token()

#lets create a /command route this is a post request

@app.route('/talkalot', methods=['POST'])
def command():
    global auth_token

    #print request data route
    app.logger.info("in command route...")
    app.logger.info(request.json) 
    
    robotJid = request.json['payload']['robotJid']
    toJid = request.json['payload']['toJid']
    userJid = request.json['payload']['userJid']
    userId = request.json['payload']['userId']
    userName = request.json['payload']['userName']
    channelName = request.json['payload']['channelName']
    cmd = request.json['payload']['cmd']
    accountId = request.json['payload']['accountId']
    data = create_data_object(toJid, userJid, robotJid, accountId, "I like mooney")
    
    
    app.logger.info("command received...")
    url = "https://api.zoom.us/v2/im/chat/messages"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=data, headers=headers)
    #check to see if the response is 200
    #print(response.status_code)
    app.logger.info(response.json())

    #userid_cid_base64
    #if the response is not 200 then get a new auth token
    #{'event': 'bot_notification', 'payload': {'accountId': '98cKrPiRQUanKn9bULRWnA', 'channelName': 'catapp', 'cmd': 'help', 'robotJid': 'v1qbk5ll8jrmq_1x-pvlhdvw@xmpp.zoom.us', 'timestamp': 1701703994342, 'toJid': 
    #'j8uogi_1qiknvq_n0-zopg@xmpp.zoom.us', 'triggerId': 'KkDWnEuVStaBSU3bi7vJNQ', 'userId': 'j8UOGi_1QIKNVQ_N0-zOPg', 'userJid': 'j8uogi_1qiknvq_n0-zopg@xmpp.zoom.us', 'userName': 'Doug Ruby'}}
    
    


    if response.status_code != 201:
        auth_token = get_auth_token()
        response = requests.post(url, json=data, headers=headers)

    #lets grab the users channels using a get request
    #https://api.zoom.us/v2/im/users/j8uogi_1qiknvq_n0-zopg/channels

    #j8uogi_1qiknvq_n0-zopg
    url = "https://api.zoom.us/v2/chat/users/j8uogi_1qiknvq_n0-zopg/channels"
    #response_channels = requests.get(url, headers=headers)
    #print(response_channels)

    return ""
 

@app.route('/test_message')
def test_message():
    global auth_token
    print("in test message received...")
    url = "https://api.zoom.us/v2/im/chat/messages"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=data, headers=headers)
    #check to see if the response is 200
    print(response.status_code)
    print(response.json())
    #if the response is not 200 then get a new auth token
    
    if response.status_code != 200:
        auth_token = get_auth_token()
        #response = requests.post(url, json=data, headers=headers)

    return response.json()


#app.run(host='0.0.0.0', port=8000, debug=True)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    app.run()
 
