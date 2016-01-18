import os
import sys
import json
import requests

def LoadConfig(filename):
    with open(filename) as file:
        return json.load(file)
    
def SaveConfig(filename, config):
    with open(filename, "w") as file:
        json.dump(config, file, indent=4)

def UrlJson(url):
    print("Req: " + url)
    return requests.get(url).json()

def UrlString(url):
    print("Req: " + url)
    return requests.get(url).text

def DownloadPgn(user, filename, timestamp):
    nb = 10
    while True:
        games = UrlJson("http://en.lichess.org/api/game?username=%s&nb=%d" % (user, nb))["list"]
        if len(games) != nb or any((g["timestamp"] < timestamp for g in games)):
            break
        nb *= 2
    newTimestamp = timestamp
    with open(filename, "wb") as file:
        for g in games:
            if g["timestamp"] > timestamp:
                pgn = UrlString("http://en.lichess.org/game/export/%s.pgn" % g["id"])
                print("Save: " + filename + " " + g["id"])
                file.write((pgn + "\n\n").encode("utf-8"))
            if g["timestamp"] > newTimestamp:
                newTimestamp = g["timestamp"]
    return newTimestamp

def ImportPgn(pgnFilename, scidFilename):
    print("Import: " + pgnFilename + " " + scidFilename)
    os.system("pgnscid %s %s" % (pgnFilename, "temp"))
    try:
        os.remove(scidFilename + ".old.si4")
        os.remove(scidFilename + ".old.sg4")
        os.remove(scidFilename + ".old.sn4")
    except OSError:
        pass
    if os.path.isfile(scidFilename + ".si4"):
        os.rename(scidFilename + ".si4", scidFilename + ".old.si4")
        os.rename(scidFilename + ".sg4", scidFilename + ".old.sg4")
        os.rename(scidFilename + ".sn4", scidFilename + ".old.sn4")
        os.system("scmerge %s %s %s" % (scidFilename, scidFilename + ".old", "temp"))
        os.remove(scidFilename + ".old.si4")
        os.remove(scidFilename + ".old.sg4")
        os.remove(scidFilename + ".old.sn4")
    else:
         os.system("scmerge %s %s" % (scidFilename, "temp"))
    os.remove("temp.si4")
    os.remove("temp.sg4")
    os.remove("temp.sn4")

if __name__ == "__main__":
    config = LoadConfig("config.json")
    config["timestamp"] = DownloadPgn(config["user"], "temp.pgn", config["timestamp"])
    ImportPgn("temp.pgn", config["database"])
    SaveConfig("config.json", config)
    os.remove("temp.pgn")
