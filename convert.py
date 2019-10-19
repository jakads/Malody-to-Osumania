import os
import json
import sys
import zipfile
from shutil import rmtree
from msvcrt import getch
import requests
import webbrowser
from tqdm import tqdm
import string
import random

version = "1.3"
date = "October 20th, 2019"

if getattr(sys, 'frozen', False):
    os.chdir(os.path.split(sys.executable)[0])
    #https://codeday.me/ko/qa/20190316/78831.html
    
print(f"Malody to osu!mania Converter v{version}")
print(date)
print("by Jakads\n\n")

def choose():
    choice = getch().decode()
    while choice not in 'yYnN':
        choice = getch().decode()
    
    if choice in 'nN':
        return 0
    
    else:
        return 1

if '--:update' in sys.argv: #added ":" to disallow user to view this message by dragging in files
    print(f"[O] Successfully updated to v{version}! :D\n[!] Would you like to check out the changelog? (Y/N)\n")
    if choose():
        webbrowser.open('https://github.com/jakads/Malody-to-Osumania#changelog')
    sys.argv.remove('--:update')

print("(i) Checking new updates . . .")
try:
    latest = requests.get('https://github.com/jakads/Malody-to-Osumania/raw/master/version.txt')
    latest.raise_for_status()
    print(f"\n(i) Latest Version = v{latest.text}")

    if latest.text != version:
        print("\n[!] New update is available! Would you like to download? (Y/N)")
        if not choose():
            print("(i) Skipping the update.\n\n")

        else:
            print("(i) Downloading . . .")
            exe = requests.get("https://github.com/jakads/Malody-to-Osumania/raw/master/convert.exe", stream=True)
            exe.raise_for_status()
            total = int(exe.headers.get('content-length'))
            progress = tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024, ncols=80) #https://github.com/tqdm/tqdm/wiki/How-to-make-a-great-Progress-Bar
            rand=''.join(random.choice(string.ascii_letters + string.digits) for i in range(16)) #https://pynative.com/python-generate-random-string/
            filename=os.path.split(sys.executable)[1]
            with open(f"{rand}.exe", 'wb') as f: #https://stackoverflow.com/questions/37573483
                for chunk in exe.iter_content(chunk_size=4096):
                    if chunk:
                        progress.update(4096)
                        f.write(chunk)
            with open(f'{rand}.bat', 'w') as f:
                f.write('\n'.join(['@echo off',
                                   'echo (i) Restarting . . .',
                                   "echo (i) All the files you've dragged in will be converted very soon!",
                                   'timeout /t 5 /nobreak >nul',
                                   f'del {filename}',
                                   f'rename {rand}.exe {filename}',
                                   f'start {filename} --:update {" ".join(sys.argv[1:]) if len(sys.argv)>1 else ""}',
                                   f'del {rand}.bat']))
            os.startfile(f'{rand}.bat')
            sys.exit()
            
    else:
        print("\n[O] Your program is as good as new! We're good to go.\n\n")
except Exception as e:
    print("\n[!] Fatal Error while connecting:", e)
    print("\n[!] Connection to GitHub failed. Will just continue...\n\n")
    
def recursive_file_gen(mydir):
    for root, dirs, files in os.walk(mydir):
        for file in files:
            yield os.path.join(root, file)
            #https://stackoverflow.com/questions/2865278

def convert(i, bgtmp, soundtmp):
    try:
        with open(f'{i}',encoding='utf-8') as mc:
            mcFile = json.loads(mc.read())
        mcFile['meta']['mode']
    except:
        print(f"[!] FileWarning: {os.path.split(i)[1]} is not a valid .mc file. Ignoring...")
        return 1

    if not mcFile['meta']['mode'] == 0:
        print(f"[!] KeyWarning: {os.path.split(i)[1]} is not a Key difficulty. Ignoring...")
        return 1
        
    line = mcFile['time']
    meta = mcFile['meta']
    note = mcFile['note']
    soundnote = {}

    keys = meta["mode_ext"]["column"]

    for x in note:
        if x.get('type',0):
            soundnote = x

    bpm = [line[0]['bpm']]
    bpmoffset = [-soundnote["offset"]]

    if len(line)>1:
        j=0
        lastbeat=line[0]['beat']
        for x in line[1:]:
            bpm.append(x['bpm'])
            bpmoffset.append(ms(beat(x['beat'])-beat(lastbeat),line[j]['bpm'],bpmoffset[j]))
            j+=1
            lastbeat=x['beat']

    global title, artist #I know using global is a bad practice but c'mon
    title = meta["song"]["title"]
    artist = meta["song"]["artist"]

    offset = note[-1].get('offset',0)
    preview = meta.get('preview',-1)
    titleorg = meta['song'].get('titleorg',title)
    artistorg = meta['song'].get('artistorg',artist)

    background = meta["background"]
    if not background=="": bgtmp.append(f'{os.path.split(i)[0]}\\{background}')
    sound = soundnote["sound"]
    if not sound=="": soundtmp.append(f'{os.path.split(i)[0]}\\{sound}')
    creator = meta["creator"]
    version = meta["version"]

    with open(f'{os.path.splitext(i)[0]}.osu',mode='w',encoding='utf-8') as osu:
        osuformat = ['osu file format v14',
                     '',
                     '[General]',
                     f'AudioFilename: {sound}',
                     'AudioLeadIn: 0',
                     f'PreviewTime: {preview}',
                     'Countdown: 0',
                     'SampleSet: Soft',
                     'StackLeniency: 0.7',
                     'Mode: 3',
                     'LetterboxInBreaks: 0',
                     'SpecialStyle: 0',
                     'WidescreenStoryboard: 0',
                     '',
                     '[Editor]',
                     'DistanceSpacing: 1.2',
                     'BeatDivisor: 4',
                     'GridSize: 8',
                     'TimelineZoom: 2.4',
                     '',
                     '[Metadata]',
                     f'Title:{title}',
                     f'TitleUnicode:{titleorg}',
                     f'Artist:{artist}',
                     f'ArtistUnicode:{artistorg}',
                     f'Creator:{creator}',
                     f'Version:{version}',
                     'Source:Malody',
                     'Tags:Malody Convert by Jakads',
                     'BeatmapID:0',
                     'BeatmapSetID:-1',
                     '',
                     '[Difficulty]',
                     'HPDrainRate:8',
                     f'CircleSize:{keys}',
                     'OverallDifficulty:8',
                     'ApproachRate:5',
                     'SliderMultiplier:1.4',
                     'SliderTickRate:1',
                     '',
                     '[Events]',
                     '//Background and Video events',
                     f'0,0,\"{background}\",0,0',
                     '',
                     '[TimingPoints]\n']
        osu.write('\n'.join(osuformat))
        #https://thrillfighter.tistory.com/310

        bpmcount = len(bpm)
        for x in range(bpmcount):
            osu.write(f'{bpmoffset[x]},{60000/bpm[x]},{int(line[x].get("sign",4))},1,0,0,1,0\n')

        osu.write('\n\n[HitObjects]\n')

        for n in note:
            if n.get('type',0):
                continue
            
            j=0
            k=0

            for b in line:
                if beat(b['beat']) > beat(n['beat']):
                    j+=1
                else:
                    continue

            if not n.get('endbeat') == None:
                for b in line:
                    if beat(b['beat']) > beat(n['endbeat']):
                        k+=1
                    else:
                        continue

            j=bpmcount-j-1
            k=bpmcount-k-1

            if int(ms(beat(n["beat"]), bpm[j], bpmoffset[j])) >= 0:
                if n.get('endbeat') == None:  #Regular Note
                    osu.write(f'{col(n["column"], keys)},192,{int(ms(beat(n["beat"])-beat(line[j]["beat"]), bpm[j], bpmoffset[j]))},1,0\n')
                else:  #Long Note
                    osu.write(f'{col(n["column"], keys)},192,{int(ms(beat(n["beat"])-beat(line[j]["beat"]), bpm[j], bpmoffset[j]))},128,0,{int(ms(beat(n["endbeat"])-beat(line[k]["beat"]), bpm[k], bpmoffset[k]))}\n')
    return 0

def ms(beats, bpm, offset): 
    return 1000*(60/bpm)*beats+offset

def beat(beat): #beats = [measure, nth beat, divisor]
    return beat[0] + beat[1]/beat[2]

def col(column, keys):
    return int(512*(2*column+1)/(2*keys))

def compress(compressname, name, bglist, soundlist):
    osz = zipfile.ZipFile(f'{compressname}.osz','w')

    for i in name:
        osz.write(f'{os.path.splitext(i)[0]}.osu')
        os.remove(f'{os.path.splitext(i)[0]}.osu')
        print(f'[O] Compressed: {os.path.split(i)[1]}.osu')
    if not len(bglist)==0:
        for i in bglist:
            if os.path.isfile(i):
                osz.write(f'{i}')
                print(f'[O] Compressed: {os.path.split(i)[1]}')
            else:
                print(f'[!] {os.path.split(i)[1]} is not found and thus not compressed.')
    if not len(soundlist)==0:
        for i in soundlist:
            if os.path.isfile(i):
                osz.write(f'{i}')
                print(f'[O] Compressed: {os.path.split(i)[1]}\n')
            else:
                print(f'[!] {os.path.split(i)[1]} is not found and thus not compressed.')
    osz.close()
    oszname.append(f'{compressname}.osz')

if len(sys.argv)<=1:
    print("(i) Drag .mc or .mcz/.zip files into this program to convert them to .osu or .osz!")
    print("(i) Press any key to exit.")
    getch()
    sys.exit()

MCDragged = False
MCValid = False
ZIPDragged = False
#FolderDragged = False
mcname = []
zipname = []
foldername = []
oszname = []

mctmp = []
for x in sys.argv[1:]:
    isMCZ = False
    if os.path.isdir(x):
        #zipname.append(os.path.splitext(x)[0])
        #FolderDragged = True
        print(f"[!] FileWarning: {os.path.split(x)[1]} is a directory, not a file. Ignoring...")
    elif not os.path.isfile(x):
        print(f"[!] FileWarning: {os.path.split(x)[1]} is not found. I recommend dragging the file into the program, not with a command prompt. Ignoring...")
    elif os.path.splitext(x)[1].lower() == ".mc":
        mctmp.append(x)
        MCDragged = True
    elif os.path.splitext(x)[1].lower() == (".mcz" or ".zip"):
        if os.path.splitext(x)[1].lower() == ".mcz":
            isMCZ = True
            os.rename(x, f'{os.path.splitext(x)[0]}.zip')
            x = f'{os.path.splitext(x)[0]}.zip'
        mcz = zipfile.ZipFile(x)
        mcz.extractall(os.path.splitext(x)[0])
        mcz.close()
        if isMCZ:
            os.rename(x, f'{os.path.splitext(x)[0]}.mcz')
        zipname.append(os.path.splitext(x)[0])
        ZIPDragged = True
    else:
        print(f"[!] FileWarning: The file type of {os.path.split(x)[1]} is not supported. Ignoring...")
if MCDragged:
    mcname.append(mctmp)

if not MCDragged and not ZIPDragged:
    print("\n[X] FILEERROR: None of the files you've dragged in are supported. This program only accepts .mc, .mcz, .zip files, or folders with them.")
    print("(i) Press any key to exit.")
    getch()
    sys.exit()

title = ""
artist = ""
mctitle = ""
mcartist = ""
bglist = []
soundlist = []

print("\n\n(i) Converting . . .\n")

#Converting to .osu (dragged .mc files)
if MCDragged:
    bgtmp = []
    soundtmp = []
    for i in mcname[0]:
        if not convert(i, bgtmp, soundtmp):
            print(f'[O] Converted: {os.path.split(i)[1]}')
            MCValid = True
    mctitle = title
    mcartist = artist
    bglist.append(bgtmp)
    soundlist.append(soundtmp)


#Converting to .osu (dragged .mcz/.zip files)
if ZIPDragged:
    for folder in zipname:
        print(f'\n(i) Converting {os.path.split(folder)[1]} . . .\n')
        c=0
        bgtmp = []
        soundtmp = []
        mctmp = []
        filelist = list(recursive_file_gen(folder))
        for files in filelist:
            if os.path.splitext(files)[1] == ".mc":
                if not convert(files, bgtmp, soundtmp):
                    print(f'[O] Converted: {os.path.split(files)[1]}')
                    c+=1
                    MCValid = True
                    mctmp.append(files)
        if c>0:
            foldername.append(folder)
            bglist.append(bgtmp)
            soundlist.append(soundtmp)
            mcname.append(mctmp)

if not MCValid:
    print("\n[X] FILEERROR: None of the files you've dragged are supported.")
    print("(i) Press any key to exit.")
    getch()
    sys.exit()

print('\n\n(i) All the supported .mc files have been converted to .osu!\n(i) Either close the program now and move the files manually,\n(i) or press Enter to compress all into .osz.')
getch()

print('\n(i) Compressing  . . .\n')
#Compress to .osz (dragged .mc files as single mapset)
if MCDragged:
    compress(f'{mcartist} - {mctitle}', mcname[0], set(bglist[0]), set(soundlist[0]))

if ZIPDragged:
    i = 1 if MCDragged else 0
    for folder in zipname:
        print(f'\n(i) Compressing {os.path.split(folder)[1]} . . .\n')
        compress(f'{os.path.split(folder)[1]}', mcname[i], set(bglist[i]), set(soundlist[i]))
        i+=1
        rmtree(folder)

print('\n(i) The following .osz files have been created! Run the files to add the maps to osu! automatically.\n')
for i in oszname:
    print(f'* {i}')
print('\n(i) Press any key to exit.')
getch()
