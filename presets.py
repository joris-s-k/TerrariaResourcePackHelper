import json
import os

import config

terrariaConfigDir = 'C:\\Users\\Joris\\Documents\\My games\\Terraria\\'
confPath = os.path.join(terrariaConfigDir, 'config.json')


def load_preset():
    with open('conf.json', 'r') as c:
        js = json.load(c)
        for index, preset in enumerate(js):
            print(f'#{index:4} - {preset}')
        print('Choose Preset Index')
        preset_index = int(input('> '))
        l_preset = js[list(js)[preset_index]]
        config_fp = open(confPath, 'r')
        json_data = json.load(config_fp)
        config_fp.close()
        json_data.update({'ResourcePacks': l_preset})
        config_fp = open(confPath, 'w')
        json.dump(json_data, config_fp, indent=4)
        config_fp.close()
    return


def save_preset():
    print('Name of Preset:')
    preset_name = input()
    config_fp = open(confPath, 'r')
    preset = json.load(config_fp)['ResourcePacks']
    config_fp.close()
    config.set_setting(preset_name, preset)


def list_presets():
    with open('conf.json', 'r') as c:
        js = json.load(c)
        for key in js.keys():
            print(key)
    return


def manage_presets():
    while True:
        print('Preset Management')
        print('[1] => Load Preset\n[2] => Save Preset\n[3] => List Presets\n[4] => EXIT')
        prompt = input('> ')
        if prompt == '1':
            load_preset()
        elif prompt == '2':
            save_preset()
        elif prompt == '3':
            list_presets()
        elif prompt == '4':
            return
