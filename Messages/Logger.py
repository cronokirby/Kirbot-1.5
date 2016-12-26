"""
this module is used to construct txt files from a list of messages
"""
import os


# turns a discord message into a loggable format
def format_message(message):
    return "<{}> {}: {}".format(
        str(message.timestamp)[:-7],
        message.author.name,
        message.clean_content)


async def log_messages(msg_list, filename):
    # need to reverse to get chronological order
    msg_list = [format_message(msg) for msg in list(reversed(msg_list))]
    with open(filename, mode='w', encoding='utf-8') as fp:
        fp.write("\n".join(msg_list))


# returns a list of messages in that channel
async def fetch_logs(client, channel, limit=100000000, before=None,
                     after=None, around=None):
    print('fetching logs...')
    message_log = [msg async for msg in client.logs_from(channel, limit=limit)]
    print('got logs.')
    return message_log


async def send_logs(client, author, message):
    channel = message.channel
    filename = message.server.name + '_' + channel.name + '.txt'
    message_log = await fetch_logs(client, channel)
    # has the side effect of creating a file with the logs in it
    await log_messages(message_log, filename)
    await client.send_file(channel, filename)
    os.remove(filename)
