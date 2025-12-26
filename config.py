import json

def setSetting(name, value):
    with open('conf.json','r+') as c:
        js = json.load(c)
        js[name] = value
        c.seek(0)
        json.dump(js,c,indent=4)
        c.truncate()

def getSetting(name):
    with open('conf.json','r') as c:
        js = json.load(c)
    return js[name]