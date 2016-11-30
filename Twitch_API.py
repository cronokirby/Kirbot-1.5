import json
from urllib.request import urlopen
from datetime import datetime


# Check if a stream exists, returns 'Live', 'Offline', 'False': doesn't exist.
def findstream(name):
    try:
        URL = ("https://api.twitch.tv/kraken/streams/{}"
               "?client_id=5jpipg7isa4syna5k9jyzmfxi4xtlj9").format(name)
        Data = json.loads(urlopen(URL).read().decode('utf-8'))
        # This will fail if the stream does not exist.
        if Data['stream']:
            return 'Live'
        # Data['stream'] is None when the streamer is offline
        else:
            return 'Offline'
    except:
        return False


def fetchstreaminfo(name):
    # try will fail if the url is bad, which means the name is incorrect
    try:
        URL = ("https://api.twitch.tv/kraken/streams/{}"
               "?client_id=5jpipg7isa4syna5k9jyzmfxi4xtlj9").format(name)
        StreamLink = "http://twitch.tv/{}".format(name)
        Data = json.loads(urlopen(URL).read().decode('utf-8'))
        if Data["stream"] is None:
            # Online will be used to check the online status of a stream
            Info = {
                'online': False,
                'URL': StreamLink}
        else:
            # Time in UTC, because creation_datetime is in UTC
            Current_Time = datetime.utcnow()
            creation_datetime = Data["stream"]["created_at"]
            creation_datetime = datetime.strptime(creation_datetime,
                                                  '%Y-%m-%dT%H:%M:%SZ')
            # This returns a datetime.timedelta() object
            ElapsedTime = Current_Time - creation_datetime
            Hours, Remainder = divmod(ElapsedTime.total_seconds(), 3600)
            Minutes = divmod(Remainder, 60)
            Seconds = Minutes[1]
            Uptime = {
                'Hours': int(Hours),
                'Minutes': int(Minutes[0]),
                'Seconds': int(Seconds)}

            Info = {
                'uptime': Uptime,
                'online': True,
                'URL': StreamLink,
                'game': Data["stream"]["game"],
                'viewers': Data["stream"]["viewers"],
                'preview': Data["stream"]["preview"]["medium"],
                'display_name': Data["stream"]["channel"]["display_name"],
                'status': Data["stream"]["channel"]["status"],
                'logo' : Data["stream"]["channel"]["logo"]}

        return Info
    except:
        # I could use False instead, but this is clearer later
        return "bad name"
