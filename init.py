import os, sys, io
import json
from sys import exit
terrariaConfigDir = '/home/joris/.local/share/Terraria/'
steamWorkshopDir = '/home/joris/.steam/debian-installation/steamapps/workshop/content/105600/'
confDir = os.path.join(terrariaConfigDir, 'config.json')

def getSafeFile(file) -> str:
    fileStub = []
    for line in file:
        fileStub.append(line)
        if 'Name' in line:
            break
    return ''.join(fileStub)+'"Dummy": ""}'
    

def listPacks(active):
    print('Printing Active Packs')
    if os.path.exists(confDir):
        config_fp = open(confDir, 'r')
        jsonData = json.load(config_fp)
        config_fp.close()
        #print(jsonData['ResourcePacks'])
        for pack in jsonData['ResourcePacks']:
            if pack['Enabled'] is active:
                name = pack['FileName']
                packName = name
                jsonName = 'pack.json' if os.path.exists(os.path.join(steamWorkshopDir,name,'pack.json')) else 'Pack.json'
                steamDir = os.path.join(steamWorkshopDir,name,jsonName)
                localDir = os.path.join(terrariaConfigDir, 'ResourcePacks', name)
                if os.path.exists(steamDir):
                    #print(steamDir)
                    #packName = json.load(open(steamDir, 'r'))['Name']
                    fixedFile = getSafeFile(io.open(steamDir, 'r', encoding='utf-8-sig'))
                    packName = json.loads(fixedFile)['Name']
                    #packName = json.load(io.open(steamDir, 'r', encoding='utf-8-sig'),strict=False)['Name']
                elif os.path.exists(localDir):
                    jsonName = 'pack.json' if os.path.exists(os.path.join(localDir,'pack.json')) else 'Pack.json'
                    if os.path.exists(os.path.join(localDir,jsonName)):
                        fixedFile = getSafeFile(io.open(os.path.join(localDir,jsonName), 'r', encoding='utf-8-sig'))
                        packName = json.loads(fixedFile)['Name']
                        #packName = json.load(io.open(os.path.join(terrariaConfigDir,'ResourcePacks',name,jsonName), 'r', encoding='utf-8-sig'),strict=False)['Name']                
                else:
                    print(f'(ERROR): {name} not found on disk')
                print(f'#{pack['SortingOrder']}\t- {packName}')

def packReorder():
    listPacks(True)
    print('')
    print('Current position: ')
    old = int(input())
    print('New position: ')
    new = int(input())
    #if old > new
    #    if x < old and x >= new -> x=x+1
    #if old < new
    #    if x > old and x <= new -> x=x-1
    if old == new:
        return
    if os.path.exists(confDir):
        config_fp = open(confDir, 'r')
        jsonData = json.load(config_fp)
        config_fp.close()
        for pack in jsonData['ResourcePacks']:
            if pack['Enabled'] is True:
                x = pack['SortingOrder']
                if old > new:
                    if x == old:
                        val = new
                    elif old > x >= new:
                        val = x+1
                    else: continue
                else: #if old < new
                    if x == old:
                        val = new
                    elif old < x <= new:
                        val = x - 1
                    else: continue
                pack.update({'SortingOrder': val})
                print(f'Was at {x}\tmoved to {val}\t- {pack['FileName']}')
        config_fp = open(confDir, 'w')
        json.dump(jsonData,config_fp,indent=4)
        config_fp.close()
    return

def packDeactivate():
    return

def packActivate():
    return

def backup_config():
    os.popen(f"cp {confDir} {os.path.join(terrariaConfigDir,'config.json.bckp')}")

def start():
    backup_config()
    while True:
        print('Welcome to TRPH!')
        #print('[1] => List Active Packs\n[2] => Reorder Pack\n[3] => Deactivate Pack\n[4] => List Inactive Packs\n[5] => Activate Pack\n[6] => Exit')
        print('[1] => List Active Packs\n[2] => Reorder Pack\n[4] => List Inactive Packs\n[6] => Exit')
        prompt = input('> ')
        if prompt == '1':
            listPacks(True)
        elif prompt == '2':
            packReorder()
        elif prompt == '3':
            packDeactivate()
        elif prompt == '4':
            listPacks(False)
        elif prompt == '5':
            packActivate()
        elif prompt == '6':
            exit()
        else:
            print('(ERROR) Invalid option passed, exiting.')
            exit()
start()