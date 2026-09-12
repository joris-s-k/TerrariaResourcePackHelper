import json


def set_setting(name, value):
    with open('conf.json', 'r+') as c:
        js = json.load(c)
        js[name] = value
        c.seek(0)
        json.dump(js, c, indent=4)
        c.truncate()


def get_setting(name):
    with open('conf.json', 'r') as c:
        js = json.load(c)
    return js[name]
