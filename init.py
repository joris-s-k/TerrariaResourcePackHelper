import itertools
import json
import os
from dataclasses import dataclass
from pathlib import Path
from sys import exit
from typing import Optional

from presets import managePresets

# Pfade könnten auch als Path objekte implementiert werden
terraria_config_dir = Path('C:\\Users\\Joris\\Documents\\My games\\Terraria\\')
steam_workshop_dir = Path('H:\\SteamLibrary\\steamapps\\workshop\\content\\105600')
conf_path = terraria_config_dir / 'config.json'


# Data Class, decorator sorgt für die nötigen standardfunktionen (constructor, compare, etc.)
@dataclass
class InactivePack:
    name: str
    type: str
    dir: str


def print_err(error: str):
    print('\033[31mERROR:\033[0m', error)


def conf_load_as_json() -> dict:
    if not conf_path.exists():
        raise FileNotFoundError(f'ERROR: Config file not found at {conf_path}')

    with conf_path.open('r') as config_fp:
        return json.load(config_fp)


def json_dump_to_conf(json_data: dict) -> None:
    with conf_path.open('w') as config:
        json.dump(json_data, config, indent=4)


def conf_backup():
    os.popen(f'copy \"{conf_path}\" \"{terraria_config_dir / 'config.json.bckp'}\"')
    if not os.path.exists('conf.json'):
        open('conf.json', 'w').write('{}')


def get_safe_file(path: Path) -> str:
    with path.open('r', encoding='utf-8-sig') as unsafeFile:
        file_stub = []
        for line in unsafeFile:
            file_stub.append(line)
            if 'Name' in line:
                break
        return ''.join(file_stub) + '"Dummy": ""}'


def get_pack_json_path(pack_path: Path) -> Optional[Path]:
    pack_file_path = pack_path / 'pack.json'
    if not pack_file_path.exists():
        pack_file_path = pack_path / 'Pack.json'
    if not pack_file_path.exists():
        return None
    return pack_file_path


def pack_list_active(active: bool):
    json_data = conf_load_as_json()

    print('Printing Active Packs')
    print(f'Order\t- ID      \t- Name')

    for pack in sorted(json_data['ResourcePacks'], key=lambda x: x['SortingOrder']):
        error = None
        if pack['Enabled'] is not active:
            continue
        directory_name = pack['FileName']
        pack_name = pack['FileName']
        steam_dir = steam_workshop_dir / directory_name
        local_dir = terraria_config_dir / 'ResourcePacks' / directory_name
        pack_dir = None
        path_type = pack_name
        if steam_dir.exists():
            pack_dir = steam_dir
        elif local_dir.exists():
            pack_dir = local_dir
            path_type = "LOCAL"

        if pack_dir is not None:
            pack_file_path = get_pack_json_path(pack_dir)
            if pack_file_path is None:
                error = f'pack.json for {pack_name} not found.'
            else:
                try:
                    fixedFile = get_safe_file(pack_file_path)
                    pack_name = json.loads(fixedFile)['Name']
                except:
                    error = f'Name of pack {pack_name} could not be read.'
        else:
            error = f'{directory_name} not found on disk'

        print(f'#{pack['SortingOrder']:>3} - {path_type:<10} - {pack_name}')
        if error is not None:
            print_err(error)


def compute_max_sort_index(json_data: dict) -> int:
    return max((pack['SortingOrder'] for pack in json_data['ResourcePacks']), default=0)


def pack_reorder():
    pack_list_active(True)
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

    json_data = conf_load_as_json()

    for pack in json_data['ResourcePacks']:
        if not pack['Enabled']:
            continue
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
        print(f'Was at {x:>3} moved to {val:>3} - {pack['FileName']}')
    json_dump_to_conf(json_data)


def pack_deactivate():
    print('')
    print('# to deactivate: ')
    deactivate_index = int(input())

    json_data = conf_load_as_json()

    for pack in json_data['ResourcePacks']:
        if pack['SortingOrder'] == deactivate_index:
            pack['Enabled'] = False
            break

    json_dump_to_conf(json_data)


def pack_activate(inactive_packs: list[InactivePack]):
    print('')
    print('# to activate: ')
    inactive_index = int(input())

    json_data = conf_load_as_json()
    next_pack_index = compute_max_sort_index(json_data) + 1

    pack_body = {
        'FileName': inactive_packs[inactive_index].dir,
        'Enabled': True,
        'SortingOrder': next_pack_index
    }

    json_data['ResourcePacks'].append(pack_body)
    json_dump_to_conf(json_data)


def pack_list_inactive() -> list[InactivePack]:
    config_json = conf_load_as_json()

    # enabled_packs = set()
    # for pack in config_json['ResourcePacks']:
    #    if not pack['Enabled']:
    #        continue
    #    enabled_packs.add(pack['FileName'])
    # stattdessen Set Comprehension, (geht auch mit Listen und Dicts)
    enabled_packs = {pack['FileName'] for pack in config_json['ResourcePacks'] if pack['Enabled']}

    pack_dirs_entries = itertools.chain(steam_workshop_dir.iterdir(),
                                        terraria_config_dir.joinpath('ResourcePacks').iterdir())
    inactive_packs = []
    for entry in pack_dirs_entries:
        if entry.name in enabled_packs:
            continue

        if entry.is_file():
            if entry.suffix == '.zip':
                inactive_packs.append(InactivePack(entry.name, 'LOCAL ZIP', entry.name))
            continue

        pack_path = get_pack_json_path(entry)
        if pack_path is not None:
            try:
                safe_file_stub = get_safe_file(pack_path)
                pack_name = json.loads(safe_file_stub)['Name']

            except:
                print_err(f'Name of pack {entry.name} could not be read.')
                continue

            pack_type = 'LOCAL'
            if pack_path.is_relative_to(steam_workshop_dir):
                pack_type = 'STEAM'

            inactive_packs.append(InactivePack(pack_name, pack_type, entry.name))
        else:
            print_err(f'pack.json for {entry.name} does not exist.')

    name_length = 0
    type_length = 0
    dir_length = 0
    for pack in inactive_packs:
        name_length = max(len(pack.name), name_length)
        type_length = max(len(pack.type), type_length)
        dir_length = max(len(pack.dir), dir_length)

    inactive_packs.sort(key=lambda x: x.name)
    for i, pack in enumerate(inactive_packs):
        print(f'#{i:>3} - {pack.type:<{type_length}} - {pack.dir:<{dir_length}}\t- {pack.name:<{name_length}}')
    return inactive_packs


def start():
    conf_backup()
    pack_list_active(True)
    while True:
        print('Welcome to TRPH!')
        print(
            '[a] => Activate Pack\n'
            '[d] => Deactivate Pack\n'
            '[l] => List Active Packs\n'
            '[i] => List Inactive Packs\n'
            '[m] => Move Pack\n'
            '[p] => Manage Presets\n'
            '[exit] => EXIT\n'
        )

        prompt = input('> ')
        if prompt == 'l':
            pack_list_active(True)
        elif prompt == 'm':
            pack_reorder()
        elif prompt == 'd':
            pack_list_active(True)
            pack_deactivate()
        elif prompt == 'i':
            pack_list_inactive()
        elif prompt == 'a':
            inactive_packs = pack_list_inactive()
            pack_activate(inactive_packs)
        elif prompt == 'exit':
            exit()
        elif prompt == 'p':
            managePresets()
        else:
            print_err('Invalid option passed, exiting.')


start()
