"""
This module is used to interact directly with speedrun.com's API.
It will be accessed by functions in Commands.py
"""
# used to convert durations in the sr.com api
import isodate
import aiohttp


async def fetchname(userurl):
    async with aiohttp.ClientSession() as client:
        async with client.get(url=userurl) as r:
            Data = await r.json()
    name = Data["data"]["names"]["international"]
    return name


async def fetchabbreviation(name):
    Words = str(name).split(" ")
    url = 'http://www.speedrun.com/api/v1/games?name='
    for word in Words:
        if word != Words[-1]:
            url += "{}%20".format(word)
        else:
            url += word
    async with aiohttp.ClientSession() as client:
        async with client.get(url=url) as r:
            Data = await r.json()
    Data = Data['data']
    if len(Data) == 0:
        return "Invalid game name"
    else:
        return Data[0]["abbreviation"]


async def fetchcategories(game):
    try:
        url = 'http://www.speedrun.com/api/v1/games/{}/categories'.format(
            str(game))
        async with aiohttp.ClientSession() as client:
            async with client.get(url=url) as r:
                Data = await r.json()
        Dictionary = {}
        for category in Data["data"]:
            v_url = category["links"][2]["uri"]
            async with aiohttp.ClientSession() as client:
                async with client.get(url=v_url) as r:
                    VariableData = await r.json()
            # checks if a run has variables
            if VariableData["data"] == []:
                Dictionary[category["name"]] = [category["links"][5]["uri"]]
            else:
                data = VariableData["data"][0]["values"]["values"]
                for variable in dict.keys(data):
                    label = data[variable]["label"]
                    name = category["name"] + " - " + label
                    link = category["links"][5]["uri"]
                    Dictionary[name] = [link, variable]
        return Dictionary
    except:
        return "Invalid game name"


async def fetchtime(game, category, rank):
    Link = await fetchcategories(str(game))
    Link = Link[str(category)]
    url = Link[0]
    async with aiohttp.ClientSession() as client:
        async with client.get(url=url) as r:
            Data = await r.json()
    if len(Link) == 1:
        RunData = [run for run in Data["data"]["runs"]]
    else:
        variable = Link[1]
        RunData = []
        for run in Data["data"]["runs"]:
            for k, value in run["run"]["values"].items():
                    if value == variable:
                        RunData.append(run)
    RunCount = len(RunData)
    if not(rank in set(range(-RunCount, RunCount - 1))):
        return "bad rank"
    RunValues = []
    Runs = {}
    for run in RunData:
        Value = run["run"]["times"]["primary_t"]
        Time = isodate.parse_duration(run["run"]["times"]["primary"])
        Player = run["run"]["players"][0]
        if Player["rel"] == "user":
            Name = await fetchname(run["run"]["players"][0]["uri"])
        else:
            Name = Player["name"]
        if run["run"]["videos"] is None:
            Vod = "no vod"
        else:
            Vod = run["run"]["videos"]["links"][0]["uri"]
        Runinfo = {"name": Name, "time": Time, "vod": Vod}
        RunValues.append(Value)
        Runs[Value] = Runinfo
    Key = sorted(RunValues)[rank]
    return Runs[Key]
