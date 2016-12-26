"""
This module handles the updating of the streams currently live.
As well as the catching of new streams, and generating messages to send
in that case
"""
# for timing the alerter
import asyncio
import discord
# Database functions
from Stream_Link_DB.DB_Manipulation import (fetchenabledservers,
                                            fetchserverinfo,
                                            updatestreamlists)


# This gets called periodically in main, feeding it old streams,
# it finds streams that are new since then, a dictionary of messages to send
# and a list of
def alert_generator():
    # constructs an alert message based on a stream dictionary
    def stream_embed(stream):
        Embed = discord.Embed(description="", colour=0x9e42f4)
        Embed.set_author(name=stream["display_name"] + " is now live!",
                         url=stream['URL'])
        Embed.set_thumbnail(url=stream['logo'])
        Embed.add_field(name='Game:', value=stream['game'])
        Embed.add_field(name='Status:', value=stream['status'])
        return Embed

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
            old_statuses = [stream['status'] for stream in old_streams_c]
            # print(old_statuses)
            # we filter out streams that aren't new, or haven't changed
            new_streams = [stream for stream in streams
                           if stream['status'] not in old_statuses]
            for stream in new_streams:
                Embed = stream_embed(stream)
                # the channel is an id to send to, the embed is the message
                message = {'embed': Embed, 'channel': channel}
                alert['messages'].append(message)
        print(alert['messages'])
        yield alert


# The routine for stream alerts, the current interval is 60s
async def alerts(client, interval):
    # this block executes only once
    await updatestreamlists()
    alerter = alert_generator()
    alerts = next(alerter)
    old_streams = alerts['streams']
    while True:
        await asyncio.sleep(interval)
        await updatestreamlists()
        next(alerter)
        alerts = alerter.send(old_streams)
        old_streams = alerts['streams']
        # ~1/300 messages fail to send, this catches that to avoid a crash
        try:
            for message in alerts['messages']:
                channel = client.get_channel(message['channel'])
                await client.send_message(channel, embed=message['embed'])
        except:
            print("message failed to send...")
