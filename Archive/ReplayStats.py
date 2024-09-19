#!/usr/bin/env python
import fnmatch
import io
import os
import sys
from collections.abc import Any, Iterable

# Ensure this filepath is correct.
file_path: str = './Test Replays/'

# label: (file_offset, num_type)
metadata_dictionary: dict[str, tuple[int, int | str]] = {
    "year": (0x1a, 16), "month": (0x1c, 8), "day": (0x1d, 8),
    "hour": (0x1e, 8), "minute": (0x1f, 8), "second": (0x20, 8),
    "p1 steam id": (0x22, 64), "p2 steam id": (0x2a, 64),
    "p1 name": (0x32, 'c'), "p2 name": (0x52, 'c'),
    "p1 char": (0x72, 8), "p2 char": (0x73, 8), "ex chars?": (0x74, 8),
    "single or team": (0x75, 8), "+R or AC": (0x76, 8),
    "recording location timezone bias against GMT": (0x77, 32),
    "p1 rounds": (0x7B, 8), "p2 rounds": (0x7C, 8),
    "unfinished match, disconnect, desync bitmask": (0x7D, 8),
    "ping": (0x7E, 8), "match duration in frames": (0x7F, 32),
    "p1 score": (0x83, 8), "p2 score": (0x84, 8), "p1 rank": (0x85, 8),
    "p2 rank": (0x86, 8), "winner side": (0x87, 8)
}

# 1-25
# SO KY MA MI AX PO CH ED BA FA TE JA AN JO VE DI SL IN ZA BR RO AB OS KL JU
character_array: list[str] = ['Sol', 'Ky', 'May', 'Millia', 'Axl', 'Potemkin',
                              'Chipp', 'Eddie', 'Baiken', 'Faust', 'Testament',
                              'Jam', 'Anji', 'Johnny', 'Venom', 'Dizzy',
                              'Slayer', 'I-No', 'Zappa', 'Bridget', 'Robo-Ky',
                              'A.B.A', 'Order Sol', 'Kliff', 'Justice']


def ParseMetadata(replay_file_path: str) -> dict[str, int]:
    """
    Parses the replay metadata into a readable format.
    """
    parsedDict: dict[str, str | int] = {}
    replay: io.TextIOWrapper = open(replay_file_path, 'rb')
    for label, data in metadata_dictionary.items():
        replay.seek(data[0], 0)
        if data[1] != 'c':
            parsedDict[label]: int = int.from_bytes(
                (replay.read(int(data[1]/8))), "little")
        else:
            try:
                temp: str = replay.read(32).decode()
            except:
                replay.seek(-32, 1)
                temp: str = replay.read(32).decode("utf-16")
            finally:
                temp = temp.replace("\x00", "", -1)
                parsedDict[label] = temp
    parsedDict['p1 char'] = character_array[(parsedDict['p1 char'] - 1)]
    parsedDict['p2 char'] = character_array[(parsedDict['p2 char'] - 1)]
    return parsedDict


def PartialParseMetadata(replay_file_path: str) -> dict[str, int]:
    """
    Parse only the relevant replay data for efficiency.
    """
    parsedDict: dict[str, str | int] = {}
    replay: io.BufferedReader = open(replay_file_path, 'rb')

    _ = replay.seek(metadata_dictionary['p1 name'][0], 0)
    try:
        temp = replay.read(32).decode()
    except UnicodeDecodeError:
        _ = replay.seek(-32, 1)
        temp: str = replay.read(32).decode("utf-16")
    finally:
        temp = temp.replace("\x00", "", -1)
        parsedDict['p1 name'] = temp

    replay.seek(metadata_dictionary['p2 name'][0], 0)
    try:
        temp = replay.read(32).decode()
    except UnicodeDecodeError:
        replay.seek(-32, 1)
        temp = replay.read(32).decode("utf-16")
    finally:
        temp = temp.replace("\x00", "", -1)
        parsedDict['p2 name'] = temp

    replay.seek(metadata_dictionary['p1 char'][0], 0)
    parsedDict['p1 char'] = int.from_bytes(
        (replay.read(int(metadata_dictionary['p1 char'][1]/8))), "little")
    parsedDict['p1 char'] = character_array[(parsedDict['p1 char'] - 1)]

    replay.seek(metadata_dictionary['p2 char'][0], 0)
    parsedDict['p2 char'] = int.from_bytes(
        (replay.read(int(metadata_dictionary['p2 char'][1]/8))), "little")
    parsedDict['p2 char'] = character_array[(parsedDict['p2 char'] - 1)]

    replay.seek(metadata_dictionary['p1 steam id'][0], 0)
    parsedDict['p1 steam id'] = int.from_bytes(
        (replay.read(int(metadata_dictionary['p1 steam id'][1]/8))), "little")

    replay.seek(metadata_dictionary['p2 steam id'][0], 0)
    parsedDict['p2 steam id'] = int.from_bytes(
        (replay.read(int(metadata_dictionary['p2 steam id'][1]/8))), "little")

    replay.seek(metadata_dictionary['p1 rounds'][0], 0)
    parsedDict['p1 rounds'] = int.from_bytes(
        (replay.read(int(metadata_dictionary['p1 rounds'][1]/8))), "little")

    replay.seek(metadata_dictionary['p2 rounds'][0], 0)
    parsedDict['p2 rounds'] = int.from_bytes(
        (replay.read(int(metadata_dictionary['p2 rounds'][1]/8))), "little")

    return parsedDict


def ReadConfigFile() -> list[str]:
    """
    Reads the config file into a list.
    """
    fileData: list[str] = []
    try:
        with open('replayOrganizerConfig.ini', 'r', encoding='utf-8') as file:
            fileData = file.read().split("\n")
    except OSError:
        print("Config file not found, creating config file.")
        f = open('replayOrganizerConfig.ini', 'w')
        f.close()
    return fileData


def CheckIfExists(x: Any, ls: Iterable[Any]) -> bool:
    """
    Check if something is in something else.
    """
    return x in ls


def LinePrepender(filename: str, line: str) -> None:
    """
    Add a line to the beginning of a file.
    """
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


def FindUserSteamID(username: str) -> int:
    """
    Find a Steam ID that matches a provided name.
    """
    steamID: int = -1
    replay_files: list[str] = os.listdir(file_path)
    for file in replay_files:
        if 'ggr' in file.lower():
            metaData: dict[str, int] = PartialParseMetadata(
                file_path+"\\"+file)
            if metaData['p1 name'] == username:
                steamID = metaData['p1 steam id']
                break
            elif metaData['p2 name'] == username:
                steamID = metaData['p2 steam id']
                break
    return steamID


def DeterminePlayerSide(metaData):
    """
    Determine which side is the user.
    """
    if str(metaData['p1 steam id']) in config_dictionary:
        if config_dictionary[str(metaData['p1 steam id'])] == 'user':
            return ('p1', 'p2')
    if str(metaData['p2 steam id']) in config_dictionary:
        if config_dictionary[str(metaData['p2 steam id'])] == 'user':
            return ('p2', 'p1')
    return ('', '')

# this function is used to check whether or not a steamID already has a
# nickname within the config file.


def CheckConfDict(config_dictionary, steamID):
    """
    Determine if the config file already has a Steam ID.
    """
    return steamID in config_dictionary


player_list: list[str] = []
player_dictionary = {}
player_exclude: bool = False

# if the user passed along a list of nicknames, only check replays with those
# nicknames.
if len(sys.argv) == 2:
    player_list = sys.argv[1].split(",")
    player_InEx = 'In'
elif len(sys.argv) == 3:
    # a third parameter will make it exclude those replay files instead.
    player_list = sys.argv[1].split(",")
    player_exclude = True

config_dictionary = {}

# this loop exists to ensure the program knows who the user is, and creates an
# entry in the config file for the user if there isn't
while (True):
    fileData = ReadConfigFile()
    try:
        tempBool = CheckIfExists('user', fileData[0])
    except:
        tempBool = False

    if not tempBool:
        username = input(
            'running first time set up, enter in your steam username: ')
        steamID = FindUserSteamID(username)

        if (steamID == -1):
            print("could not find username in replay files.")
            steamID = input(
                'please either enter in your steamID manually here, or ensure \
                        you entered your username properly and try again.\n')
            print(f'steamID saved as: {
                  steamID}, if all of your matches are being moved into \
                  \'spectated matches\', you may need to edit the config file \
                  to correct a mistake.')

        LinePrepender('replayOrganizerConfig.ini', f"{steamID}=user")
    else:
        break

# load the config file into a dictionary
for entry in fileData:
    entryList = entry.split("=")
    try:
        config_dictionary[entryList[0]] = entryList[1]
    except:
        break

# run through the player list the user passed
# and try to cross reference it with their config file.
for player in player_list:
    try:
        player_dictionary[list(config_dictionary.keys())[list(
            config_dictionary.values()).index(player)]] = player
    except:
        print("couldn't locate "+player +
              " in your config file, please ensure you spelled \
              their nickname correctly.")


for char in character_array:  # loop through the player side characters
    try:
        temp_path = file_path+'/As '+char
        os.chdir(temp_path)
        print("")
        for opchar in character_array:  # loop through the opponent side chars
            try:
                os.chdir(temp_path+'/Against '+opchar)
                total_matches = 0
                wins = 0

                # gather the replay files
                for path, dirs, files in os.walk('.'):
                    for f in fnmatch.filter(files, '*.ggr'):
                        file = os.path.abspath(os.path.join(path, f))

                        # parse the metadata
                        metaData = PartialParseMetadata(file)
                        player, opponent = DeterminePlayerSide(metaData)

                        # if they added a player list
                        if (len(player_dictionary) > 0):
                            # exclude the player list
                            if (player_exclude):
                                if not CheckConfDict(player_dictionary, str(
                                        metaData[opponent+' steam id'])):
                                    total_matches += 1
                                    if (metaData[player+' rounds'] > metaData[
                                            opponent+' rounds']):
                                        wins += 1
                            # include the player list
                            else:
                                if CheckConfDict(player_dictionary, str(
                                        metaData[opponent+' steam id'])):
                                    total_matches += 1
                                    if (metaData[player+' rounds'] > metaData[
                                            opponent+' rounds']):
                                        wins += 1
                        # if there was no player list,
                        # just include every replay file
                        else:
                            total_matches += 1
                            if (metaData[player+' rounds'] > metaData[
                                    opponent+' rounds']):
                                wins += 1

                # print out the information
                # avoiding divide by 0 errors
                if (wins != 0):
                    matchup = round(((wins/total_matches)*10), 1)
                else:
                    matchup = 0
                if (total_matches != 0):
                    print(char+" "+str(matchup)+":"+str(round(10-matchup, 1)) +
                          " "+opchar +
                          " Based on "+str(total_matches)+" Matches.")
                os.chdir('..')
            except:
                continue
        os.chdir('..')
    except:
        continue


input("Press Enter to continue.")
