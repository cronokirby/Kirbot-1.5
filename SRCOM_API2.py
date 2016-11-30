import json
import isodate
from urllib.request import urlopen


def fetchname(userurl):
    Data = json.loads(urlopen(userurl).read().decode('utf-8'))
    name = Data["data"]["names"]["international"]
    return name


def fetchabbreviation(name):
    Words = str(name).split(" ")
    U = 'http://www.speedrun.com/api/v1/games?name='
    for word in Words:
        if word != Words[-1]:
            U += "{}%20".format(word)
        else:
            U += word
    Data = json.loads(urlopen(U).read().decode('utf-8'))["data"]
    if len(Data) == 0:
        return "Invalid game name"
    else:
        return Data[0]["abbreviation"]


def fetchcategories(game):
    try:
        url = 'http://www.speedrun.com/api/v1/games/{}/categories'.format(
            str(game))
        Data = json.loads(urlopen(url).read().decode('utf-8'))
        Dictionary = {}
        for category in Data["data"]:
            v_url = category["links"][2]["uri"]
            VariableData = json.loads(urlopen(v_url).read().decode('utf-8'))
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


def fetchtime(game, category, rank):
    Link = fetchcategories(str(game))[str(category)]
    Data = json.loads(urlopen(Link[0]).read().decode('utf-8'))
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
            Name = fetchname(run["run"]["players"][0]["uri"])
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
