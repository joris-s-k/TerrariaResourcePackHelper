import os, sys, io
import json
from sys import exit
terrariaConfigDir = '/home/joris/.local/share/Terraria/'
steamWorkshopDir = '/home/joris/.steam/debian-installation/steamapps/workshop/content/105600/'
confDir = os.path.join(terrariaConfigDir, 'config_tmp.json')

def listPacks(active):
    print('Printing Active Packs')
    if os.path.exists(confDir):
        jsonData = json.load(open(confDir, 'r'))
        #print(jsonData['ResourcePacks'])
        for pack in jsonData['ResourcePacks']:
            if pack['Enabled'] is active:
                name = pack['FileName']
                #print(name)
                jsonName = 'pack.json' if os.path.exists(os.path.join(steamWorkshopDir,name,'pack.json')) else 'Pack.json'
                steamDir = os.path.join(steamWorkshopDir,name,jsonName)
                localDir = os.path.join(terrariaConfigDir, 'ResourcePacks', name)
                if os.path.exists(steamDir):
                    #print(steamDir)
                    #packName = json.load(open(steamDir, 'r'))['Name']
                    fileStub = io.open(steamDir, 'r', encoding='utf-8-sig').readlines(2)
                    fixedFile = ''.join(fileStub)+'"Dummy": ""}'
                    packName = json.loads(fixedFile)['Name']
                    #packName = json.load(io.open(steamDir, 'r', encoding='utf-8-sig'),strict=False)['Name']
                elif os.path.exists(localDir):
                    jsonName = 'pack.json' if os.path.exists(os.path.join(localDir,'pack.json')) else 'Pack.json'
                    fileStub = io.open(os.path.join(localDir,jsonName), 'r', encoding='utf-8-sig').readlines(2)
                    fixedFile = ''.join(fileStub) + '"Dummy": ""}'
                    packName = json.loads(fixedFile)['Name']
                    #packName = json.load(io.open(os.path.join(terrariaConfigDir,'ResourcePacks',name,jsonName), 'r', encoding='utf-8-sig'),strict=False)['Name']
                else:
                    print(f'(ERROR): {name} not found on disk')
                print(f'#{pack['SortingOrder']}\t- {packName}')

def packReorder():
    print('Input current position: ')
    old = int(input())
    print('Input new position: ')
    new = int(input())
    #if old > new
    #    if x < old and x >= new -> x=x+1
    #if old < new
    #    if x > old and x <= new -> x=x-1
    if old == new:
        return
    #elif old > new:
    #    func = moveDown()
    #elif old < new:
    #    func = moveUp()
    if os.path.exists(confDir):
        jsonData = json.load(open(confDir, 'r'))
        if old > new:
            for pack in jsonData['ResourcePacks']:
                if pack['Enabled'] is True:
                    x = pack['SortingOrder']
                    if x == old:
                        val = new
                    elif old > x >= new:
                        val = x+1
                    else: continue
                    pack.update({'SortingOrder': val})
                    print(f'Was at {x}\tmoved to {val}\t- {pack['FileName']}')
        elif old < new:
            for pack in jsonData['ResourcePacks']:
                if pack['Enabled'] is True:
                    x = pack['SortingOrder']
                    if x == old:
                        val = new
                    elif old < x <= new:
                        val = x-1
                    else: continue
                    pack.update({'SortingOrder': val})
                    print(f'Was at {x}\tmoved to {val}\t- {pack['FileName']}')
        tmpDir = os.path.join(terrariaConfigDir, 'config_tmp.json')
        fd = open(tmpDir, 'w')
        json.dump(jsonData,open(confDir, 'w'),indent=4)
    return

def packDeactivate():
    return

def packActivate():
    return

def start():
    while True:
        print('Welcome to TRPH!')
        print('[1] => List Active Packs\n[2] => Reorder Pack\n[3] => Deactivate Pack\n[4] => List Inactive Packs\n[5] => Activate Pack\n[6] => Exit')
        prompt = input('> ')
        if prompt == '1':
            listPacks(True)
        elif prompt == '2':
            packReorder()
            break
        elif prompt == '3':
            packDeactivate()
            break
        elif prompt == '4':
            listPacks(False)
        elif prompt == '5':
            packActivate()
            break
        elif prompt == '5':
            exit()
        else:
            print('(ERROR) Invalid option passed, exiting.')
            exit()
start()