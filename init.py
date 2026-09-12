import itertools
from sys import exit

from presets import manage_presets
from utility import *


# Data Class, decorator sorgt für die nötigen standardfunktionen (constructor, compare, etc.)
def pack_list_active(active: bool):
    json_data = conf_load_as_json()

    print('Printing Active Packs')
    print(f'Nr.  - ID         - Name')

    for pack in sorted(json_data['ResourcePacks'], key=lambda x: x['SortingOrder']):
        error = None
        if pack['Enabled'] is not active:
            continue
        directory_name = pack['FileName']
        pack_name = pack['FileName']
        steam_dir = STEAM_WORKSHOP_DIR / directory_name
        local_dir = TERRARIA_CONFIG_DIR / 'ResourcePacks' / directory_name
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
                    fixed_file = get_safe_file(pack_file_path)
                    pack_name = json.loads(fixed_file)['Name']
                except:
                    error = f'Name of pack {pack_name} could not be read.'
        else:
            error = f'{directory_name} not found on disk'

        print_rows(f'#{pack['SortingOrder']:>3} - {path_type:<10} - {strip_color_codes(pack_name):<30}')
        if error is not None:
            print_err(error)


def pack_reorder() -> bool:
    print('')
    old = input_validated_int('Current position: ')
    new = input_validated_int('New position: ')

    # if old > new
    #    if x < old and x >= new -> x=x+1
    # if old < new
    #    if x > old and x <= new -> x=x-1
    if old == new:
        return True

    json_data = conf_load_as_json()

    if old not in {pack['SortingOrder'] for pack in json_data['ResourcePacks']}:
        print_err(f'Index for current position is out of bounds!')
        return False

    if new < 0:
        print_err('Index for new position is invalid!')
        return False

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
    return True


def pack_deactivate():
    print('')
    deactivate_index = input_validated_int('# to deactivate: ')

    json_data = conf_load_as_json()

    for pack in json_data['ResourcePacks']:
        if pack['SortingOrder'] == deactivate_index:
            pack['Enabled'] = False
            break
    
    json_dump_to_conf(json_data)


def pack_activate(inactive_packs: list[InactivePack]):
    print('')
    inactive_index = input_validated_int('# to activate: ')

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

    pack_dirs_entries = itertools.chain(STEAM_WORKSHOP_DIR.iterdir(),
                                        TERRARIA_CONFIG_DIR.joinpath('ResourcePacks').iterdir())
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
            if pack_path.is_relative_to(STEAM_WORKSHOP_DIR):
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
        dir_length = min(max(len(pack.dir), dir_length), 30)

    inactive_packs.sort(key=lambda x: x.name)
    for i, pack in enumerate(inactive_packs):
        print_rows(
            f'#{i:>3} - {pack.type:<{type_length}} - {pack.dir[:30]:<{dir_length}}\t- {strip_color_codes(pack.name):<{name_length}}')
    return inactive_packs


def start():
    conf_backup()
    while True:
        print('Welcome to TRPH!')
        print(
            '1. [l] => List Active Packs\n'
            '2. [i] => List Inactive Packs\n'
            '3. [m] => Move Pack\n'
            '4. [a] => Activate Pack\n'
            '5. [d] => Deactivate Pack\n'
            '6. [p] => Manage Presets\n'
            '7. [exit] => EXIT\n'
        )

        prompt = input('> ')
        if prompt == 'a' or prompt == '4':
            inactive_packs = pack_list_inactive()
            pack_activate(inactive_packs)
        elif prompt == 'd' or prompt == '5':
            pack_list_active(True)
            pack_deactivate()
        elif prompt == 'l' or prompt == '1':
            pack_list_active(True)
        elif prompt == 'i' or prompt == '2':
            pack_list_inactive()
        elif prompt == 'm' or prompt == '3':
            pack_list_active(True)
            # könnte auch in der Funktion mit while error == True: gemacht werden
            while not pack_reorder():
                continue
        elif prompt == 'p' or prompt == '6':
            manage_presets()
        elif prompt == 'exit' or prompt == '7':
            exit()
        else:
            print_err('Invalid option passed!.')


start()
