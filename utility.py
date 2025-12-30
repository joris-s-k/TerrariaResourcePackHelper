import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from init import TERRARIA_CONFIG_PATH, TERRARIA_CONFIG_DIR


@dataclass
class InactivePack:
    name: str
    type: str
    dir: str


def conf_load_as_json() -> dict:
    if not TERRARIA_CONFIG_PATH.exists():
        raise FileNotFoundError(f'ERROR: Config file not found at {TERRARIA_CONFIG_PATH}')

    with TERRARIA_CONFIG_PATH.open('r') as config_fp:
        return json.load(config_fp)


def json_dump_to_conf(json_data: dict) -> None:
    with TERRARIA_CONFIG_PATH.open('w') as config:
        json.dump(json_data, config, indent=4)


def conf_backup():
    os.popen(f'copy \"{TERRARIA_CONFIG_PATH}\" \"{TERRARIA_CONFIG_DIR / 'config.json.bckp'}\"')
    if not os.path.exists('conf.json'):
        open('conf.json', 'w').write('{}')


def print_err(error: str):
    print('\033[31mERROR:\033[0m', error)


def get_safe_file(path: Path) -> str:
    with path.open('r', encoding='utf-8-sig') as unsafe_file:
        file_stub = []
        for line in unsafe_file:
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


def compute_max_sort_index(json_data: dict) -> int:
    return max((pack['SortingOrder'] for pack in json_data['ResourcePacks']), default=0)


def strip_color_codes(string: str) -> str:
    return re.sub(r'\[c\/[0-9a-fA-F]{6}:([^\]]+)\]', r'\1', string)
