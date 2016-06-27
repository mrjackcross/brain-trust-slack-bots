from datetime import date, datetime, time
import os
from slackclient import SlackClient

# TheBrain's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

user_arrive_times = {}

def handle_command(command, user, channel, timestamp):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print(command)
    if command == '?' or command == ':question:':
        if user in user_arrive_times:
            midnight = datetime.combine(date.today(), time.min)
            if user_arrive_times[user] > midnight:
                slack_client.api_call("reactions.add", channel=channel,
                                      name='anger', as_user=True,
                                      timestamp=timestamp)
            else:
                user_arrive_times[user] = timestamp
                # response = '!'
                # slack_client.api_call("chat.postMessage", channel=channel,
                #                      text=response, as_user=True)
                slack_client.api_call("reactions.add", channel=channel,
                                      name='exclamation', as_user=True,
                                      timestamp=timestamp)
        else:
            user_arrive_times[user] = timestamp
            # response = '!'
            # slack_client.api_call("chat.postMessage", channel=channel,
            #                      text=response, as_user=True)
            slack_client.api_call("reactions.add", channel=channel,
                                  name='exclamation', as_user=True,
                                  timestamp=timestamp)

    else:
        response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
                   "* command with numbers, delimited by spaces."
        if command.startswith(EXAMPLE_COMMAND):
            response = "Sure...write some more code then I can do that!"
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['user'], output['channel'], output['timestamp']
            if (output and 'text' in output and output['text'] == '?') or (
                    output and 'text' in output and output['text'] == ':question:') and (
                            output and 'user' in output and output['user'] != BOT_ID):
                # return text after the @ mention, whitespace removed
                return output['text'], output['user'], output['channel'], output['ts']

    return None, None, None
    
def parse_slack_history():
    has_more = True
    oldest_message = datetime.combine(date.today(), time.min)
    while has_more:
        response = slack_client.api_call("channels.history", channel='bot-sandbox', count=1000,
                                          oldest=oldest_message)
        if response and 'has_more' in response:
            has_more = response['has_more']

        if response and 'messages' in response:
            message_list = response['messages']
            for message in message_list:
                command = message['text']
                timestamp = message['ts']
                if command == '?' or command == ':question:':
                    user_arrive_times[user] = timestamp
                if oldest_message < timestamp:
                    oldest_message = timestamp

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("TheBrain connected and running!")
        parse_slack_history()
        print("Parsed today's history!")
        print(user_arrive_times)
    while True:
            command, user, channel, ts = parse_slack_output(slack_client.rtm_read())
            if command and channel and ts:
                handle_command(command, user, channel, ts)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
