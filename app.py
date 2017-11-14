# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import bot
import os
from flask import Flask, request, make_response, render_template, jsonify
from slackclient import SlackClient
import requests

pyBot = bot.Bot()
slack = pyBot.client



# Slack Prod
# sc = SlackClient("xoxp-222558384727-220926773297-232297273809-6c29eb8da1c528b44f5c0de5c31dea7e")
# token = "xoxp-222558384727-220926773297-232297273809-6c29eb8da1c528b44f5c0de5c31dea7e"
# url = "https://slack.com/api/chat.postMessage"

# Slack Dev
sc = SlackClient("xoxp-12434129009-12434129089-16184187936-bc5468ef88a33b31c917b29c270db439")
token = "xoxp-12434129009-12434129089-16184187936-bc5468ef88a33b31c917b29c270db439"
url = "https://dev.slack.com/api/chat.postMessage"



# client_id = os.environ["SLACK_CLIENT_ID"]
# client_secret = os.environ["SLACK_CLIENT_SECRET"]
# oauth_scope = os.environ["SLACK_SCOPE"]

# Slack Prod
# client_id = "222558384727.229866327719"
# client_secret = "17d7347287c88768148a368d67916dac"

# Slack Dev
client_id = "12434129009.15561199617"
client_secret = "f7bfdf9f59bdcaf2b6d54527da938ef4"

oauth_scope = "incoming-webhook,commands,channels:history"

access_token = ''

app = Flask(__name__)


@app.route("/", methods=["POST"])
def app_actions():
    """
    API endpoint for app actions test to hit
    """
    return make_response("Received app action", 200,)

@app.route("/hello", methods=["POST"])
def hello():
    return jsonify({
        "response_type": "in_channel",
        "text": "Hello World",
        "attachments": [
        {
            "text": "Actions",
            "fallback": "You are unable to execute action",
            "callback_id": "hello",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "action",
                    "text": "Explode",
                    "type": "button",
                    "value": "boom"
                },
                {
                    "name": "action list",
                    "text": "Choose your poison",
                    "type": "select",
                    "options": [
                        {
                            "text": "Chocolate",
                            "value": "chocolate",
                        },
                        {
                            "text": "Ghost peppers",
                            "value": "ghost peppers",
                        }
                    ]
                }
            ]
        }]
    })

@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.

    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code = request.args.get('code')

    # An empty string is a valid token for this request
    sc = SlackClient("")

    # After the user has authorized this app for use in their Slack team,
    # Slack returns a temporary authorization code that we'll exchange for
    # an OAuth token using the oauth.access endpoint

    # The below method using SlackClient doesn't work in dev environment
    # auth_response = sc.api_call(
    #     "oauth.access",
    #     client_id=client_id,
    #     client_secret=client_secret,
    #     code=code
    # )
    auth_response = requests.post("https://dev.slack.com/api/oauth.access", params={
        "client_id":client_id,
        "client_secret":client_secret,
        "code":code
    })

    # To keep track of authorized users, we will save the tokens to the global
    # access_tokens object
    token = json.loads(auth_response._content)["access_token"]
    print(token)
    access_token = token

    return render_template("thanks.html")

@app.route("/event", methods=["GET", "POST"])
def handle_event():

    print('handling event')

    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    event_type = slack_event["event"]["type"]

    if event_type == "reaction_added":
        channel = slack_event["event"]["item"]["channel"]
        # The below method using SlackClient doesn't work in dev environment
        # ret = sc.api_call("chat.postMessage",
        #     channel=channel,
        #     text="reaction added",
        # )
        print(token)
        ret = requests.post(url, params={
            "token":token,
            "channel":channel,
            "text":"reaction added"
        })
        print ret.text
        return make_response("Heard a message", 200,)

    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/action", methods=["GET", "POST"])
def handle_action():

    payload = json.loads(request.form.get('payload'))
    
    if 'action_type' in payload and payload['action_type'] == 'message_action':
        print(payload)
        ret = requests.post(url, params={
            "token":token,
            "channel":payload['channel']['id'],
            "text":"Received action invocation from message: " + payload['message']['text']
        })
        return make_response("Received app action invocation", 200,)

    action = payload['actions'][0]

    if action['type'] == 'button' and action['value'] == 'boom':
        return jsonify({
            "response_type": "in_channel",
            "text": "Boom",
        })

    elif action['type'] == 'select' and action['selected_options'][0]['value'] == 'chocolate':
        return jsonify({
            "response_type": "in_channel",
            "text": "Death by sweetness",
        })

    elif action['type'] == 'select' and action['selected_options'][0]['value'] == 'ghost peppers':
        return jsonify({
            "response_type": "in_channel",
            "text": "Death by hotness",
        })

    else:
        return jsonify({
            "response_type": "in_channel",
            "text": "Something went wrong",
        })


if __name__ == '__main__':
    app.run(debug=True)
