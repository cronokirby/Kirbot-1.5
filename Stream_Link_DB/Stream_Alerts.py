"""
This module handles the updating of the streams currently live.
As well as the catching of new streams, and generating messages to send
in that case
"""
# For storing sent messages
import pickle

# for timing the alerter
import asyncio
import discord
# Database functions
from Stream_Link_DB.DB_Manipulation import (fetchenabledservers,
                                            fetchserverinfo,
                                            updatestreamlists)
# Embed formatting
from Stream_Link_DB.Alert_Embeds import stream_embed, offline_embed

# This gets called periodically in main, feeding it old streams,
# it finds streams that are new since then, a dictionary of messages to send
# and a list of
def alert_generator():
    def get_live_streams():
        new_streams = {}
        for server in fetchenabledservers():
            info = fetchserverinfo(server)
            channel_id = info['channel']
            new_streams[channel_id] = info['live_streams']
        return new_streams
    # this block only runs the first time the generator is called
    live_streams = get_live_streams()
    alert = {'streams': live_streams, 'messages': []}
    yield alert
    # this block is called every other time
    while True:
        # the streams we yield at the end will be recieved here 60s later
        old_streams = yield
        live_streams = get_live_streams()
        alert = {'streams': live_streams, 'messages': []}
        # we group the messages that need to be created by channel
        for channel, streams in live_streams.items():
            old_streams_c = old_streams[channel]
            old_names = [stream['display_name'] for stream in old_streams_c]
            # print(old_statuses)
            # we filter out streams that aren't new, or haven't changed
            new_streams = [stream for stream in streams
                           if stream['display_name'] not in old_names]
            for stream in new_streams:
                Embed = stream_embed(stream)
                # the channel is an id to send to, the embed is the message
                message = {'embed': Embed,
                           'channel': channel,
                           'stream': stream}
                alert['messages'].append(message)
        print(alert['messages'])
        yield alert


async def edit_offline(client, sent_messages, live_streams):
    live_names = []
    live_statuses = []
    for stream in live_streams:
        live_names.append(stream['display_name'])
        live_statuses.append(stream['status'])

    still_live = []
    for message in sent_messages:
        msg_object = message['object']
        stream_info = message['stream_info']
        if stream_info['display_name'] in live_names:
            still_live.append(message)
            if stream_info['status'] not in live_statuses:
                try:
                    await client.edit_message(msg_object, embed=stream_embed(stream_info))
                except discord.HTTPException:
                    print(f"couldn't edit status for {stream_info['display_name']}")
        else:
            print (f"{stream_info['display_name']} went offline")
            Embed = offline_embed(stream_info)
            try:
                await client.edit_message(msg_object, embed=Embed)
            except discord.HTTPException:
                print(f"couldn't alert offline msg for {stream_info['display_name']}")

    with open('sent_messages.p', 'wb') as fp:
        pickle.dump(still_live, fp)

    return still_live

# The routine for stream alerts, the current interval is 60s
async def alerts(client, interval):
    # this block executes only once
    await updatestreamlists()
    # This is to keep track of alerts sent, to edit them later
    with open('sent_messages.p', 'rb') as fp:
        sent_alerts = pickle.load(fp)

    alerter = alert_generator()
    alerts = next(alerter)
    old_streams = alerts['streams']
    while True:
        await asyncio.sleep(interval)
        try:
            full_streams = await updatestreamlists()
            next(alerter)
            alerts = alerter.send(old_streams)
            old_streams = alerts['streams']
            # ~1/300 messages fail to send, this catches that to avoid a crash
            try:
                for message in alerts['messages']:
                    channel = client.get_channel(message['channel'])
                    # we need to store this object to edit it later
                    sent_message = await client.send_message(channel,
                                                        embed=message['embed'])
                    stream = message['stream']
                    sent_alerts.append({'display_name': stream['display_name'],
                                        'stream_info': stream,
                                        'object': sent_message})
            except Exception as e:
                print(f'streams failed to update because {e}')

            sent_alerts = await edit_offline(client, sent_alerts, full_streams)
        except Exception as e:
            print(f"streams failed to update because {e}")
