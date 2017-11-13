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
# sc = SlackClient("xoxp-12434129009-12434129089-16184187936-bc5468ef88a33b31c917b29c270db439")
token = "xoxp-12434129009-12434129089-16184187936-bc5468ef88a33b31c917b29c270db439"
url = "https://dev.slack.com/api/chat.postMessage"



# client_id = os.environ["SLACK_CLIENT_ID"]
# client_secret = os.environ["SLACK_CLIENT_SECRET"]
# oauth_scope = os.environ["SLACK_SCOPE"]

client_id = "222558384727.229866327719"
client_secret = "17d7347287c88768148a368d67916dac"
oauth_scope = "incoming-webhook,commands,channels:history"

access_token = ''

app = Flask(__name__)


def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.
    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event
    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error
    """
    team_id = slack_event["team_id"]
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        # Send the onboarding message
        pyBot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200,)

    # ============== Share Message Events ============= #
    # If the user has shared the onboarding message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    elif event_type == "message" and slack_event["event"].get("attachments"):
        user_id = slack_event["event"].get("user")
        if slack_event["event"]["attachments"][0].get("is_share"):
            # Update the onboarding message and check off "Share this Message"
            pyBot.update_share(team_id, user_id)
            return make_response("Welcome message updates with shared message",
                                 200,)

    # ============= Reaction Added Events ============= #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "reaction_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_emoji(team_id, user_id)
        return make_response("Welcome message updates with reactji", 200,)

    # =============== Pin Added Events ================ #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "pin_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_pin(team_id, user_id)
        return make_response("Welcome message updates with pin", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

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
    auth_response = sc.api_call(
        "oauth.access",
        client_id=self.oauth["client_id"],
        client_secret=self.oauth["client_secret"],
        code=code
    )

    # To keep track of authorized users, we will save the tokens to the global
    # access_tokens object
    token = auth_response["access_token"]
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


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
