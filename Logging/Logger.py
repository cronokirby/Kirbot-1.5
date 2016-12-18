"""
this module is used to construct txt files from a list of messages
"""


# turns a discord message into a loggable format
def format_message(message):
    return "<{}> {}: {}".format(
        str(message.timestamp)[:-7], message.author.name, message.content)


def log_messages(msg_list, filename):
    # need to reverse to get chronological order
    msg_list = [format_message(msg) for msg in list(reversed(msg_list))]
    with open(filename, mode='w', encoding='utf-8') as fp:
        fp.write("\n".join(msg_list))
