#!/usr/bin/env python

from enum import Enum
from io import BufferedReader
from json import dump
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.container import BarContainer
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider
from os import getlogin, mkdir, path, scandir
from platform import system
from tkinter import (
    Button,
    Entry,
    Label,
    OptionMenu,
    # PhotoImage,
    StringVar,
    Tk,
    Toplevel,
    filedialog,
)
from typing import Any

sliders: list[RangeSlider] = []

ranks: list[str] = [
    "Civilian",
    "Cadet",
    "Bodyguard",
    "Enlistee",
    "Low-ranking Soldier",
    "High-ranking Soldier",
    "Novice Squadsman",
    "Squadsman",
    "Senior Squadsman",
    "Platoon Leader",
    "Battalion Leader",
    "Champion",
    "Master",
    "Holy Knight",
    "Holy Knight Commander",
    "Master Swordsman",
    "Dragon Hunter",
    "Titan",
    "Hero",
    "War God",
    "Legend",
]


def updateUserRanks(
    values: tuple[float, float],
    replays: list[dict[str, Any]],
    character_array: list[str],
    name: str,
    character: str,
    ax: Axes,
    canvas: FigureCanvasTkAgg,
    opponent_lower: int,
    opponent_higher: int,
) -> None:
    lower: int = int(values[0])
    higher: int = int(values[1])
    data: dict[str, list[tuple[str, float, int]]] = filterRanks(
        replays, character_array, name, lower, higher, opponent_lower, opponent_higher
    )
    route(character, data, ax, canvas, False, False)


def updateOpponentRanks(
    values: tuple[float, float],
    replays: list[dict[str, Any]],
    character_array: list[str],
    name: str,
    character: str,
    ax: Axes,
    canvas: FigureCanvasTkAgg,
    user_lower: int,
    user_higher: int,
) -> None:
    lower: int = int(values[0])
    higher: int = int(values[1])
    data: dict[str, list[tuple[str, float, int]]] = filterRanks(
        replays, character_array, name, user_lower, user_higher, lower, higher
    )
    route(character, data, ax, canvas, False, False)


class View(Enum):
    SCATTER = (0,)
    MATCHUPS = (1,)
    MATCHUPS_SORTED = (2,)
    AMOUNTS = (3,)
    AMOUNTS_SORTED = (4,)


folder: str = ""
match system():
    case "Windows":
        folder = (
            f"C:\\Users\\{getlogin()}\\Documents\\ARC SYSTEM WORKS\\GGXXAC\\Replays\\"
        )
    case "Darwin":  # Mac
        folder = f"/Users/{getlogin()}/Documents/ARC SYSTEM WORKS/GGXXAC/Replays/"
    case _:  # Linux, FreeBSD, etc.
        folder = f"/home/{getlogin()}/Documents/ARC SYSTEM WORKS/GGXXAC/Replays/"
is_sorted: bool = False
view_type: View = View.SCATTER


def analyzeCharacter(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    ax.clear()
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_title(f"Matchup Spread for {character}", fontsize=20)
    _ = ax.set_xlabel("Win Rate")
    _ = ax.set_ylabel("Number of Matches")
    characters: list[str] = []
    winrates: list[float] = []
    gameAmounts: list[int] = []
    for char_tuple in data[character]:
        if char_tuple[2] != 0:
            characters.append(char_tuple[0])
            winrates.append(char_tuple[1])
            gameAmounts.append(char_tuple[2])
            _ = ax.annotate(
                text=char_tuple[0],
                xy=(char_tuple[1], char_tuple[2]),
                xytext=(5, 5),
                textcoords="offset points",
            )
    _ = ax.scatter(x=winrates, y=gameAmounts, s=7)
    canvas.draw()


def barGraph(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    characters: list[str] = []
    winrates: list[float] = []
    for char_tuple in data[character]:
        if char_tuple[2] != 0:
            characters.append(char_tuple[0])
            winrates.append(char_tuple[1])
    if len(winrates) != 0:
        characters.append("Average")
        winrates.append(sum(winrates) / len(winrates))
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(characters)), winrates, tick_label=characters
    )
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_title(f"Matchup Win Rates as {character}", fontsize=20)
    _ = ax.set_ylabel("Character")
    _ = ax.set_xlabel("Win Rate")
    _ = ax.bar_label(bars, fmt=lambda x: f"{x:.1f}:{(10-x):.1f}", padding=2)
    ax.invert_yaxis()
    canvas.draw()


def sortedBarGraph(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    pairs: dict[str, float] = {}
    for char_tuple in data[character]:
        if char_tuple[2] != 0:
            pairs[char_tuple[0]] = char_tuple[1]
    pairs = dict(sorted(pairs.items(), key=lambda item: item[1], reverse=True))
    if len(pairs) != 0:
        pairs["Average"] = sum(pairs.values()) / len(pairs)
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(pairs)), list(pairs.values()), tick_label=list(pairs.keys())
    )
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_title(f"Matchup Win Rates as {character}", fontsize=20)
    _ = ax.set_ylabel("Character")
    _ = ax.set_xlabel("Win Rate")
    _ = ax.bar_label(bars, fmt=lambda x: f"{x:.1f}:{(10-x):.1f}", padding=2)
    ax.invert_yaxis()
    canvas.draw()


def numberOfMatches(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    characters: list[str] = []
    gameAmounts: list[int] = []
    for char_tuple in data[character]:
        if char_tuple[2] != 0:
            characters.append(char_tuple[0])
            gameAmounts.append(char_tuple[2])
    if len(gameAmounts) != 0:
        characters.append("Average")
        gameAmounts.append(int(sum(gameAmounts) / len(gameAmounts)))
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(characters)), gameAmounts, tick_label=characters
    )
    _ = ax.set_title(f"Number of Matches as {character}", fontsize=20)
    _ = ax.set_ylabel("Character")
    _ = ax.set_xlabel("Win Rate")
    _ = ax.bar_label(bars, padding=2)
    ax.invert_yaxis()
    canvas.draw()


def sortedNumberOfMatches(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    pairs: dict[str, float] = {}
    for char_tuple in data[character]:
        if char_tuple[2] != 0:
            pairs[char_tuple[0]] = char_tuple[2]
    pairs = dict(sorted(pairs.items(), key=lambda item: item[1], reverse=True))
    if len(pairs) != 0:
        pairs["Average"] = int(sum(pairs.values()) / len(pairs))
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(pairs)), list(pairs.values()), tick_label=list(pairs.keys())
    )
    _ = ax.set_title(f"Number of Matches as {character}", fontsize=20)
    _ = ax.set_ylabel("Character")
    _ = ax.set_xlabel("Win Rate")
    _ = ax.bar_label(bars, padding=2)
    ax.invert_yaxis()
    canvas.draw()


def filterRanks(
    replays: list[dict[str, Any]],
    character_array: list[str],
    name: str,
    lower_bound: int = 0,
    higher_bound: int = 20,
    opponent_lower_bound: int = 0,
    opponent_higher_bound: int = 20,
) -> dict[str, list[tuple[str, float, int]]]:
    global ranks
    data: dict[str, list[tuple[str, float, int]]] = {}
    for char in character_array:
        data[char] = []
        for char2 in character_array:
            data[char].append((char2, 0, 0))
    for replay in replays:
        if (
            replay["p1_rank"] is not None
            and replay["p2_rank"] is not None
            and (
                (
                    replay["p1_name"] == name
                    and (
                        ranks.index(replay["p1_rank"])
                        not in range(lower_bound, higher_bound)
                        or ranks.index(replay["p2_rank"])
                        not in range(opponent_lower_bound, opponent_higher_bound)
                    )
                )
                or (
                    replay["p2_name"] == name
                    and (
                        ranks.index(replay["p1_rank"])
                        not in range(opponent_lower_bound, opponent_higher_bound)
                        or ranks.index(replay["p2_rank"])
                        not in range(lower_bound, higher_bound)
                    )
                )
            )
        ):
            continue
        if replay["p1_name"] == name and replay["winner"] == 1:
            _, wins, games = data[replay["p1_char"]][
                character_array.index(replay["p2_char"])
            ]
            data[replay["p1_char"]][character_array.index(replay["p2_char"])] = (
                replay["p2_char"],
                wins + 1,
                games + 1,
            )
        elif replay["p1_name"] == name and replay["winner"] != 1:
            _, wins, games = data[replay["p1_char"]][
                character_array.index(replay["p2_char"])
            ]
            data[replay["p1_char"]][character_array.index(replay["p2_char"])] = (
                replay["p2_char"],
                wins,
                games + 1,
            )
        elif replay["p2_name"] == name and replay["winner"] == 2:
            _, wins, games = data[replay["p2_char"]][
                character_array.index(replay["p1_char"])
            ]
            data[replay["p2_char"]][character_array.index(replay["p1_char"])] = (
                replay["p1_char"],
                wins + 1,
                games + 1,
            )
        elif replay["p2_name"] == name and replay["winner"] != 2:
            _, wins, games = data[replay["p2_char"]][
                character_array.index(replay["p1_char"])
            ]
            data[replay["p2_char"]][character_array.index(replay["p1_char"])] = (
                replay["p1_char"],
                wins,
                games + 1,
            )
    for i in range(len(data)):
        for j in range(len(data[character_array[i]])):
            char, wins, games = data[character_array[i]][j]
            if games != 0:
                data[character_array[i]][j] = (char, 10 * wins / games, games)
    return data


def analyzeReplays(
    replay_folder_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
    name: str,
    root: Tk,
) -> None:
    """
    Opens a new window to graph replays.
    """
    global view_type, is_sorted, sliders
    replays: list[dict[str, Any]] = []
    slash: str = "/"
    if system() == "Windows":
        slash = "\\"
    for filename in scandir(replay_folder_path):
        if filename.name[-4:] == ".ggr":
            replays.append(
                PartialParseMetadata(
                    replay_folder_path + slash + filename.name,
                    character_array,
                    metadata_dictionary,
                )
            )
    analysis: Toplevel = Toplevel(root)
    character: StringVar = StringVar()
    character.set("Sol")
    fig, ax = plt.subplots()
    ax.clear()
    fig.set_figheight(7)
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_label(f"Matchup Spread for {character}")
    _ = ax.set_xlabel("Win Rate")
    _ = ax.set_ylabel("Number of Matches")
    canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(fig, master=analysis)
    canvas.get_tk_widget().grid(row=1, column=0, columnspan=3)
    user_rank_axes: Axes = fig.add_axes([0.2, 0.96, 0.6, 0.03])
    user_rank: RangeSlider = RangeSlider(
        user_rank_axes,
        "Your Rank",
        0,
        20,
        valstep=1,
        valinit=(0, 20),
    )
    sliders.append(user_rank)
    opponent_rank_axes: Axes = fig.add_axes([0.2, 0.935, 0.6, 0.03])
    opponent_rank: RangeSlider = RangeSlider(
        opponent_rank_axes,
        "Opponent's Rank",
        0,
        20,
        valstep=1,
        valinit=(0, 20),
    )
    sliders.append(opponent_rank)
    _ = user_rank.on_changed(
        lambda x: updateUserRanks(
            x,
            replays,
            character_array,
            name,
            character.get(),
            ax,
            canvas,
            int(opponent_rank.val[0]),
            int(opponent_rank.val[1]),
        )
    )
    _ = opponent_rank.on_changed(
        lambda x: updateOpponentRanks(
            x,
            replays,
            character_array,
            name,
            character.get(),
            ax,
            canvas,
            int(user_rank.val[0]),
            int(user_rank.val[1]),
        )
    )
    analyzeCharacter(
        "Sol",
        filterRanks(
            replays,
            character_array,
            name,
            int(user_rank.val[0]),
            int(user_rank.val[1]),
            int(opponent_rank.val[0]),
            int(opponent_rank.val[1]),
        ),
        ax,
        canvas,
    )
    dropdown: OptionMenu = OptionMenu(
        analysis,
        character,
        *character_array,
        command=lambda x: route(
            x,
            filterRanks(
                replays,
                character_array,
                name,
                int(user_rank.val[0]),
                int(user_rank.val[1]),
                int(opponent_rank.val[0]),
                int(opponent_rank.val[1]),
            ),
            ax,
            canvas,
            False,
            False,
        ),
    )
    dropdown.grid(row=0, column=0)
    switchButton: Button = Button(
        analysis,
        text="Switch View",
        command=lambda: route(
            character.get(),
            filterRanks(
                replays,
                character_array,
                name,
                int(user_rank.val[0]),
                int(user_rank.val[1]),
                int(opponent_rank.val[0]),
                int(opponent_rank.val[1]),
            ),
            ax,
            canvas,
            True,
            False,
        ),
    )
    switchButton.grid(row=0, column=1)
    sortButton: Button = Button(
        analysis,
        text="Sort View",
        command=lambda: route(
            character.get(),
            filterRanks(
                replays,
                character_array,
                name,
                int(user_rank.val[0]),
                int(user_rank.val[1]),
                int(opponent_rank.val[0]),
                int(opponent_rank.val[1]),
            ),
            ax,
            canvas,
            False,
            True,
        ),
    )
    sortButton.grid(row=0, column=2)
    analysis.protocol("WM_DELETE_WINDOW", analysis.destroy)


def route(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
    switch: bool,
    sort: bool,
) -> None:
    global view_type, is_sorted
    if switch:
        match view_type:
            case View.SCATTER:
                if is_sorted:
                    view_type = View.MATCHUPS_SORTED
                    sortedBarGraph(character, data, ax, canvas)
                else:
                    view_type = View.MATCHUPS
                    barGraph(character, data, ax, canvas)
            case View.MATCHUPS:
                view_type = View.AMOUNTS
                numberOfMatches(character, data, ax, canvas)
            case View.MATCHUPS_SORTED:
                view_type = View.AMOUNTS_SORTED
                sortedNumberOfMatches(character, data, ax, canvas)
            case View.AMOUNTS | View.AMOUNTS_SORTED:
                view_type = View.SCATTER
                analyzeCharacter(character, data, ax, canvas)
    elif sort:
        is_sorted = not is_sorted
        match view_type:
            case View.SCATTER:
                return
            case View.MATCHUPS:
                view_type = View.MATCHUPS_SORTED
                sortedBarGraph(character, data, ax, canvas)
            case View.MATCHUPS_SORTED:
                view_type = View.MATCHUPS
                barGraph(character, data, ax, canvas)
            case View.AMOUNTS:
                view_type = View.AMOUNTS_SORTED
                sortedNumberOfMatches(character, data, ax, canvas)
            case View.AMOUNTS_SORTED:
                view_type = View.AMOUNTS
                numberOfMatches(character, data, ax, canvas)
    else:
        match view_type:
            case View.SCATTER:
                analyzeCharacter(character, data, ax, canvas)
            case View.MATCHUPS:
                barGraph(character, data, ax, canvas)
            case View.MATCHUPS_SORTED:
                sortedBarGraph(character, data, ax, canvas)
            case View.AMOUNTS:
                numberOfMatches(character, data, ax, canvas)
            case View.AMOUNTS_SORTED:
                sortedNumberOfMatches(character, data, ax, canvas)


def jsonifyReplays(
    replay_folder_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
) -> None:
    """
    Makes JSONs out of replays.
    """
    slash: str = "/"
    if system() == "Windows":
        slash = "\\"
    for filename in scandir(replay_folder_path):
        if filename.name[-4:] == ".ggr":
            data: dict[str, Any] = ParseMetadata(
                replay_folder_path + slash + filename.name,
                character_array,
                metadata_dictionary,
            )
            if not path.exists(f"Output{slash}"):
                mkdir("Output")
            with open(
                f"Output{slash}{filename.name[:-4]}.json", "w", encoding="utf-8"
            ) as f:
                dump(data, f, ensure_ascii=False, indent=4)


def selectFolder() -> None:
    """
    Selects a folder.
    """
    global folder
    folder = filedialog.askdirectory(
        title="Select the folder with the replays",
        initialdir=folder,
        mustexist=True,
    )


def PartialParseMetadata(
    replay_file_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
) -> dict[str, Any]:
    """
    Parses only the important replay metadata.
    """
    global ranks

    parsedDict: dict[str, Any] = {
        "p1_name": "",
        "p1_char": "",
        "p1_rank": "",
        "p2_name": "",
        "p2_char": "",
        "p2_rank": "",
        "winner": None,
    }
    replay: BufferedReader = open(replay_file_path, "rb")
    for label, data in metadata_dictionary.items():
        _ = replay.seek(data[0], 0)
        if data[1] == 256:
            number: int = 0
        else:
            number = int.from_bytes((replay.read(int(data[1] / 8))), "little")
        match label:
            case "p1 rank":
                if parsedDict["p2_name"] is None:  # check if the match was offline
                    parsedDict["p1_rank"] = None
                else:
                    parsedDict["p1_rank"] = ranks[number]
            case "p2 rank":
                if parsedDict["p2_name"] is None:
                    parsedDict["p2_rank"] = None
                else:
                    parsedDict["p2_rank"] = ranks[number]
            case "winner side":
                if number == 3:
                    parsedDict["winner"] = None
                else:
                    parsedDict["winner"] = number
            case "p1 name":
                try:
                    temp = replay.read(32).decode()
                except UnicodeDecodeError:
                    _ = replay.seek(-32, 1)
                    temp = replay.read(32).decode("utf-16")
                finally:
                    parsedDict["p1_name"] = temp.replace("\x00", "", -1)
            case "p2 name":
                try:
                    temp = replay.read(32).decode()
                except UnicodeDecodeError:
                    _ = replay.seek(-32, 1)
                    temp = replay.read(32).decode("utf-16")
                finally:
                    parsedDict["p2_name"] = temp.replace("\x00", "", -1)
            case "p1 char":
                parsedDict["p1_char"] = character_array[number - 1]
            case "p2 char":
                parsedDict["p2_char"] = character_array[number - 1]
            case _:
                continue
    replay.close()
    return parsedDict


def ParseMetadata(
    replay_file_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
) -> dict[str, Any]:
    """
    Parses the replay metadata into a readable format.
    """
    global ranks

    parsedDict: dict[str, Any] = {
        "date": "",
        "player_1": {
            "steam_id": "",
            "name": "",
            "character": "",
            "rounds": 0,
            "score": 0,
            "rank": "",
        },
        "player_2": {
            "steam_id": "",
            "name": "",
            "character": "",
            "rounds": 0,
            "score": 0,
            "rank": "",
        },
        "ex_chars": False,
        "team": False,
        "accent_core": False,
        "unfinished": False,
        "disconnect": False,
        "desync": False,
        "ping": 0,
        "duration": 0.0,
        "winner": None,
    }
    replay: BufferedReader = open(replay_file_path, "rb")
    date: str = ""
    for label, data in metadata_dictionary.items():
        _ = replay.seek(data[0], 0)
        if data[1] == 256:
            number: int = 0
        else:
            number = int.from_bytes((replay.read(int(data[1] / 8))), "little")
        match label:
            case "year" | "month":
                date += f"{number:02}-"
            case "day":
                date += f"{number:02}T"
            case "hour" | "minute":
                date += f"{number:02}:"
            case "second":
                date += f"{number:02}"
            case "recording location timezone bias against GMT":
                time_offset: int = int(int(number) / -60)
                if time_offset == 0:
                    date += "Z"
                elif time_offset > 0:
                    date += f"+{(int(time_offset/60)):02}:{(time_offset%60):02}"
                else:
                    date += f"{(int(time_offset/60)):03}:{((-1*time_offset)%60):02}"
                parsedDict["date"] = date
            case "p1 rank":
                if (
                    parsedDict["player_2"]["name"] is None
                ):  # check if the match was offline
                    parsedDict["player_1"]["rank"] = None
                else:
                    parsedDict["player_1"]["rank"] = ranks[number]
            case "p2 rank":
                if (
                    parsedDict["player_2"]["name"] is None
                ):  # same as above, both should be player 2
                    parsedDict["player_2"]["rank"] = None
                else:
                    parsedDict["player_2"]["rank"] = ranks[number]
            case "ex chars?":
                parsedDict["ex_chars"] = number == 1
            case "single or team":
                parsedDict["team"] = number == 2
            case "+R or AC":
                parsedDict["accent_core"] = number == 1
            case "ping":
                parsedDict["ping"] = number
            case "match duration in frames":
                parsedDict["duration"] = number / 60
            case "p1 rounds":
                parsedDict["player_1"]["rounds"] = number
            case "p2 rounds":
                parsedDict["player_2"]["rounds"] = number
            case "p1 score":
                parsedDict["player_1"]["score"] = number
            case "p2 score":
                parsedDict["player_2"]["score"] = number
            case "winner side":
                if number == 1:
                    parsedDict["winner"] = "player_1"
                elif number == 2:
                    parsedDict["winner"] = "player_2"
                else:
                    parsedDict["winner"] = None
            case "p1 steam id":
                parsedDict["player_1"]["steam_id"] = str(number)
            case "p2 steam id":
                if number == 0:
                    parsedDict["player_2"]["steam_id"] = None
                else:
                    parsedDict["player_2"]["steam_id"] = str(number)
            case "p1 name":
                try:
                    temp = replay.read(32).decode()
                except UnicodeDecodeError:
                    _ = replay.seek(-32, 1)
                    temp = replay.read(32).decode("utf-16")
                finally:
                    parsedDict["player_1"]["name"] = temp.replace("\x00", "", -1)
            case "p2 name":
                if parsedDict["player_2"]["steam_id"] is None:
                    parsedDict["player_2"]["name"] = None
                else:
                    try:
                        temp = replay.read(32).decode()
                    except UnicodeDecodeError:
                        _ = replay.seek(-32, 1)
                        temp = replay.read(32).decode("utf-16")
                    finally:
                        parsedDict["player_2"]["name"] = temp.replace("\x00", "", -1)
            case "unfinished match, disconnect, desync bitmask":
                parsedDict["unfinished"] = number % 2 == 1
                parsedDict["disconnect"] = number in [2, 3, 6, 7]
                parsedDict["desync"] = number >= 4
            case "p1 char":
                parsedDict["player_1"]["character"] = character_array[number - 1]
            case "p2 char":
                parsedDict["player_2"]["character"] = character_array[number - 1]
            case _:
                raise ValueError
    replay.close()
    return parsedDict


def main() -> None:
    """
    Main functionality.
    """
    global folder, sliders
    metadata_dictionary: dict[str, tuple[int, int]] = {
        "year": (0x1A, 16),
        "month": (0x1C, 8),
        "day": (0x1D, 8),
        "hour": (0x1E, 8),
        "minute": (0x1F, 8),
        "second": (0x20, 8),
        "p1 steam id": (0x22, 64),
        "p2 steam id": (0x2A, 64),
        "p1 name": (0x32, 256),
        "p2 name": (0x52, 256),
        "p1 char": (0x72, 8),
        "p2 char": (0x73, 8),
        "ex chars?": (0x74, 8),
        "single or team": (0x75, 8),
        "+R or AC": (0x76, 8),
        "recording location timezone bias against GMT": (0x77, 32),
        "p1 rounds": (0x7B, 8),
        "p2 rounds": (0x7C, 8),
        "unfinished match, disconnect, desync bitmask": (0x7D, 8),
        "ping": (0x7E, 8),
        "match duration in frames": (0x7F, 32),
        "p1 score": (0x83, 8),
        "p2 score": (0x84, 8),
        "p1 rank": (0x85, 8),
        "p2 rank": (0x86, 8),
        "winner side": (0x87, 8),
    }

    character_array: list[str] = [
        "Sol",
        "Ky",
        "May",
        "Millia",
        "Axl",
        "Potemkin",
        "Chipp",
        "Eddie",
        "Baiken",
        "Faust",
        "Testament",
        "Jam",
        "Anji",
        "Johnny",
        "Venom",
        "Dizzy",
        "Slayer",
        "I-No",
        "Zappa",
        "Bridget",
        "Robo-Ky",
        "A.B.A",
        "Order Sol",
        "Kliff",
        "Justice",
    ]
    root: Tk = Tk()
    root.title("GGXXACPR Replay Analyzer")
    # icon: PhotoImage = PhotoImage(file="Assets/plusR.png")
    # root.iconphoto(True, icon)
    usernameText: Label = Label(root, text="Please enter your username.")
    usernameText.grid(row=0, column=0, sticky="w")
    username: Entry = Entry(root)
    username.grid(row=0, column=2, sticky="e")
    folderText: Label = Label(root, text="Please select a folder.")
    folderText.grid(row=1, column=0, sticky="w")
    folderButton: Button = Button(root, text="Select Folder", command=selectFolder)
    folderButton.grid(row=1, column=2, sticky="e")
    sortButton: Button = Button(
        root,
        text="JSON-ify Replays",
        command=lambda: jsonifyReplays(folder, character_array, metadata_dictionary),
    )
    sortButton.grid(row=2, column=0)
    analyzeButton: Button = Button(
        root,
        text="Analyze Replays",
        command=lambda: analyzeReplays(
            folder, character_array, metadata_dictionary, username.get(), root
        ),
    )
    analyzeButton.grid(row=2, column=2)
    root.protocol("WM_DELETE_WINDOW", exit)
    root.mainloop()


if __name__ == "__main__":
    main()
