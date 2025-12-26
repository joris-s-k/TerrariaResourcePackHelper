import os
import json
import config

terrariaConfigDir = 'C:\\Users\\Joris\\Documents\\My games\\Terraria\\'
confPath = os.path.join(terrariaConfigDir, 'config.json')


def loadPreset():
    with open('conf.json','r') as c:
        js = json.load(c)
        for index,preset in enumerate(js):
            print(f'#{index:4} - {preset}')
        print('Choose Preset Index')
        preset_index = int(input('> '))
        l_preset = js[list(js)[preset_index]]
        config_fp = open(confPath, 'r')
        jsonData = json.load(config_fp)
        config_fp.close()
        jsonData.update({'ResourcePacks': l_preset})
        config_fp = open(confPath, 'w')
        json.dump(jsonData,config_fp,indent=4)
        config_fp.close()
    return

def savePreset():
    print('Name of Preset:')
    preset_name = input()
    config_fp = open(confPath, 'r')
    preset = json.load(config_fp)['ResourcePacks']
    config_fp.close()
    config.setSetting(preset_name,preset)

def listPresets():
    with open('conf.json','r') as c:
        js = json.load(c)
        for key in js.keys():
            print(key)
    return

def managePresets():
    while True:
        print('Preset Management')
        print('[1] => Load Preset\n[2] => Save Preset\n[3] => List Presets\n[4] => EXIT')
        prompt = input('> ')
        if prompt == '1':
            loadPreset()
        elif prompt == '2':
            savePreset()
        elif prompt == '3':
            listPresets()
        elif prompt == '4':
            return