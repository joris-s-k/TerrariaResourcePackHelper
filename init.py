import json
import os
from pathlib import Path
from sys import exit
from typing import Optional

from presets import managePresets

# Pfade könnten auch als Path objekte implementiert werden
terrariaConfigDir = 'C:\\Users\\Joris\\Documents\\My games\\Terraria\\'
steamWorkshopDir = 'H:\\SteamLibrary\\steamapps\\workshop\\content\\105600'
confPath = os.path.join(terrariaConfigDir, 'config.json')


def get_safe_file(path: Path) -> str:
    with path.open('r', encoding='utf-8-sig') as unsafeFile:
        fileStub = []
        for line in unsafeFile:
            fileStub.append(line)
            if 'Name' in line:
                break
        return ''.join(fileStub) + '"Dummy": ""}'


def load_conf_as_json() -> dict:
    if not os.path.exists(confPath):
        raise FileNotFoundError(f'ERROR: Config file not found at {confPath}')

    with open(confPath, 'r') as configFp:
        return json.load(configFp)


def list_packs(active: bool):
    jsonData = load_conf_as_json()

    print('Printing Active Packs')
    print(f'Order\t- ID      \t- Name')

    for pack in sorted(jsonData['ResourcePacks'], key=lambda x: x['SortingOrder']):
        error = None
        if pack['Enabled'] is not active:
            continue
        directoryName = pack['FileName']
        packName = pack['FileName']
        steamDir = Path(steamWorkshopDir, directoryName)
        localDir = Path(terrariaConfigDir, 'ResourcePacks', directoryName)
        packDir = None
        pathType = packName
        if steamDir.exists():
            packDir = steamDir
        elif localDir.exists():
            packDir = localDir
            pathType = "LOCAL00000"

        if packDir is not None:
            pack_file_path = get_pack_json_path(packDir)
            if pack_file_path is None:
                error = f'ERROR: pack.json for {packName} not found.'
            else:
                try:
                    fixedFile = get_safe_file(pack_file_path)
                    packName = json.loads(fixedFile)['Name']
                except:
                    error = f'ERROR: Name of pack {packName} could not be read.'
        else:
            error = f'ERROR: {directoryName} not found on disk'

        print(f'#{pack['SortingOrder']}\t- {pathType}\t- {packName}')
        if error is not None:
            print(error)


def get_pack_json_path(pack_path: Path) -> Optional[Path]:
    pack_file_path = pack_path / 'pack.json'
    if not pack_file_path.exists():
        pack_file_path = pack_path / 'Pack.json'
    if not pack_file_path.exists():
        return None
    return pack_file_path


def pack_reorder():
    list_packs(True)
    print('')
    print('Current position: ')
    old = int(input())
    print('New position: ')
    new = int(input())
    # if old > new
    #    if x < old and x >= new -> x=x+1
    # if old < new
    #    if x > old and x <= new -> x=x-1
    if old == new:
        return
    if os.path.exists(confPath):
        config_fp = open(confPath, 'r')
        jsonData = json.load(config_fp)
        config_fp.close()
        for pack in jsonData['ResourcePacks']:
            if pack['Enabled'] is True:
                x = pack['SortingOrder']
                if old > new:
                    if x == old:
                        val = new
                    elif old > x >= new:
                        val = x + 1
                    else:
                        continue
                else:  # if old < new
                    if x == old:
                        val = new
                    elif old < x <= new:
                        val = x - 1
                    else:
                        continue
                pack.update({'SortingOrder': val})
                print(f'Was at {x}\tmoved to {val}\t- {pack['FileName']}')
        with open(confPath, 'w') as config_fp:
            json.dump(jsonData, config_fp, indent=4)
    return


def pack_deactivate():
    return


def pack_activate():
    return


def backup_config():
    os.popen(f'copy \"{confPath}\" \"{os.path.join(terrariaConfigDir, 'config.json.bckp')}\"')
    if not os.path.exists('conf.json'):
        open('conf.json', 'w').write('{}')

def start():
    backup_config()
    list_packs(True)
    while True:
        print('Welcome to TRPH!')
        # print('[1] => List Active Packs\n[2] => Reorder Pack\n[3] => Deactivate Pack\n[4] => List Inactive Packs\n[5] => Activate Pack\n[6] => Exit')
        print(
            '[1] => List Active Packs\n[2] => Reorder Pack\n[4] => List Inactive Packs\n[6] => EXIT\n[7] => Manage Presets')
        prompt = input('> ')
        if prompt == '1':
            list_packs(True)
        elif prompt == '2':
            pack_reorder()
        elif prompt == '3':
            pack_deactivate()
        elif prompt == '4':
            listPacks(False)
        elif prompt == '5':
            pack_activate()
        elif prompt == '6':
            exit()
        elif prompt == '7':
            managePresets()
        else:
            print('(ERROR) Invalid option passed, exiting.')
            exit()


start()
