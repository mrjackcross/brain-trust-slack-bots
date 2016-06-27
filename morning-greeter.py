import os
from slackclient import SlackClient

# TheBrain's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

if __name__ == "__main__":
    if slack_client.rtm_connect():
        slack_client.api_call("chat.postMessage", channel='C19FKETK4', text=':question:', as_user=True)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
