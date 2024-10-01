#!/usr/bin/env python3

from enum import Enum
from glob import glob
from io import BufferedReader
from json import dump
from os import getlogin, mkdir, path
from platform import system
from tkinter import (
    DISABLED,
    NORMAL,
    Button,
    Checkbutton,
    Entry,
    Frame,
    IntVar,
    Label,
    OptionMenu,
    StringVar,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
)
from typing import Any

try:
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import MouseEvent
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.collections import PathCollection
    from matplotlib.container import BarContainer
    from matplotlib.pyplot import subplots
    from matplotlib.text import Annotation
    from matplotlib.widgets import RadioButtons, RangeSlider
except ImportError:
    mpl_command: str = "py -m pip install matplotlib" if system() == "Windows" else "python3 -m pip install matplotlib"
    _ = messagebox.showerror(
        "Matplotlib Missing",
        f"Matplotlib, the backend used to render the graphs, is not installed; please install it with the instructions here:\nhttps://matplotlib.org/stable/install/index.html\nAlternatively, run “{mpl_command}” from the command line.",
    )
    exit(1)

sliders: list[RangeSlider] = []

annot: Annotation

replay_type_selection: RadioButtons

one_folder_dump_status: IntVar

sort_button: Button

opponent: Entry

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

colors: list[str] = [
    "#b34230",
    "#3c5685",
    "#ff8c2c",
    "#ecc966",
    "#bc283c",
    "#836448",
    "#586060",
    "#474040",
    "#f35460",
    "#b9764c",
    "#302838",
    "#d73c38",
    "#263c68",
    "#181818",
    "#0d55c7",
    "#486880",
    "#8c3c00",
    "#e03048",
    "#4a4a4a",
    "#3b64c7",
    "#538681",
    "#a6390e",
    "#64271e",
    "#cda583",
    "#128cd0",
]


def update_replays(
    _: str | None,
    replays: list[dict[str, Any]],
    character_array: list[str],
    name: str,
    opponent_name: str,
    character: str,
    ax: Axes,
    canvas: FigureCanvasTkAgg,
    replay_type: str,
    user_lower: int,
    user_higher: int,
    opponent_lower: int,
    opponent_higher: int,
) -> None:
    data: dict[str, list[tuple[str, float, int]]] = filter_replays(
        replays,
        character_array,
        name,
        opponent_name,
        replay_type,
        user_lower,
        user_higher,
        opponent_lower,
        opponent_higher,
    )
    determine_view(character, data, ax, canvas, False, False)


def hover(
    event: MouseEvent,
    canvas: FigureCanvasTkAgg,
    ax: Axes,
    sc: PathCollection,
    winrates: list[float],
    games: list[int],
    colors: list[str],
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
):
    global annot
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind, sc, winrates, games, colors, character, data)
            annot.set_visible(True)
            canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                canvas.draw_idle()


def update_annot(
    ind: dict[str, list[int]],
    sc: PathCollection,
    winrates: list[float],
    games: list[int],
    colors: list[str],
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
):
    global annot
    pos: tuple[float, float] = sc.get_offsets()[ind["ind"][0]]
    shared_points: list[str] = [
        value[0]
        for value in data[character]
        if value[1] == winrates[ind["ind"][0]] and value[2] == games[ind["ind"][0]]
    ]
    annot.xy = pos
    text = "{}\n{}:{}\n{} {}".format(
        f"{', '.join(shared_points) if len(shared_points) > 1 else shared_points[0]}",
        f"{winrates[ind['ind'][0]]:.1f}",
        f"{(10 - winrates[ind['ind'][0]]):.1f}",
        games[ind["ind"][0]],
        "Match" if games[ind["ind"][0]] == 1 else "Matches",
    )
    _ = annot.set(text=text)
    _ = annot.get_bbox_patch().set(alpha=0.6, color=colors[ind["ind"][0]])


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
corrupt_replays: list[str] = []


def scatter_plot(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    global colors, annot, opponent
    ax.clear()
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_title(
        f"Matchup Spread for {character if opponent.get() == '' else character + '\nAgainst ' + opponent.get()}",
        fontsize=26 if opponent.get() == "" else 14,
    )
    _ = ax.set_xlabel("Win Rate", fontsize=18)
    _ = ax.set_ylabel("Number of Matches", fontsize=18)
    characters: list[str] = []
    winrates: list[float] = []
    game_amounts: list[int] = []
    colors_visible: list[str] = []
    for i in range(len(data[character])):
        char_tuple: tuple[str, float, int] = data[character][i]
        if char_tuple[2] != 0:
            characters.append(char_tuple[0])
            winrates.append(char_tuple[1])
            game_amounts.append(char_tuple[2])
            _ = ax.annotate(
                text=char_tuple[0],
                xy=(char_tuple[1], char_tuple[2]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=13,
            )
            colors_visible.append(colors[i])
    annot = ax.annotate(
        text="",
        xy=(0, 0),
        xytext=(-70, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        fontsize=15,
    )
    scatter: PathCollection = ax.scatter(
        x=winrates, y=game_amounts, s=20, color=colors_visible
    )
    _ = canvas.mpl_connect(
        "motion_notify_event",
        lambda e: hover(
            e,
            canvas,
            ax,
            scatter,
            winrates,
            game_amounts,
            colors_visible,
            character,
            data,
        ),
    )
    canvas.draw()


def matchups_bar_graph(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    global colors, opponent
    characters: list[str] = []
    winrates: list[float] = []
    colors_visible: list[str] = []
    for i in range(len(data[character])):
        char_tuple: tuple[str, float, int] = data[character][i]
        if char_tuple[2] != 0:
            characters.append(char_tuple[0])
            winrates.append(char_tuple[1])
            colors_visible.append(colors[i])
    if len(winrates) != 0:
        characters.append("Average")
        winrates.append(sum(winrates) / len(winrates))
        colors_visible.append("#1f7bb4")
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(characters)), winrates, tick_label=characters, color=colors_visible
    )
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_title(
        f"Matchup Win Rates as {character if opponent.get() == '' else character + '\nAgainst ' + opponent.get()}",
        fontsize=26 if opponent.get() == "" else 14,
    )
    _ = ax.set_ylabel("Character", fontsize=18)
    _ = ax.set_xlabel("Win Rate", fontsize=18)
    _ = ax.bar_label(bars, fmt=lambda x: f"{x:.1f}:{(10-x):.1f}", padding=2)
    ax.invert_yaxis()
    canvas.draw()


def matchups_bar_graph_sorted(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    global colors, opponent
    pairs: dict[str, float] = {}
    color_pairs: dict[str, str] = {}
    for i in range(len(data[character])):
        char_tuple: tuple[str, float, int] = data[character][i]
        if char_tuple[2] != 0:
            pairs[char_tuple[0]] = char_tuple[1]
            color_pairs[data[character][i][0]] = colors[i]
    color_list: list[str] = [
        color_pairs[k]
        for k, _ in sorted(pairs.items(), key=lambda item: item[1], reverse=True)
    ]
    pairs = dict(sorted(pairs.items(), key=lambda item: item[1], reverse=True))
    if len(pairs) != 0:
        pairs["Average"] = sum(pairs.values()) / len(pairs)
        color_list.append("#1f7bb4")
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(pairs)),
        list(pairs.values()),
        tick_label=list(pairs.keys()),
        color=color_list,
    )
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_title(
        f"Matchup Win Rates as {character if opponent.get() == '' else character + '\nAgainst ' + opponent.get()}",
        fontsize=26 if opponent.get() == "" else 14,
    )
    _ = ax.set_ylabel("Character", fontsize=18)
    _ = ax.set_xlabel("Win Rate", fontsize=18)
    _ = ax.bar_label(bars, fmt=lambda x: f"{x:.1f}:{(10-x):.1f}", padding=2)
    ax.invert_yaxis()
    canvas.draw()


def no_of_matches_bar_graph(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    global colors, opponent
    characters: list[str] = []
    gameAmounts: list[int] = []
    colors_visible: list[str] = []
    for i in range(len(data[character])):
        char_tuple: tuple[str, float, int] = data[character][i]
        if char_tuple[2] != 0:
            characters.append(char_tuple[0])
            gameAmounts.append(char_tuple[2])
            colors_visible.append(colors[i])
    if len(gameAmounts) != 0:
        characters.append("Average")
        gameAmounts.append(round(sum(gameAmounts) / len(gameAmounts)))
        colors_visible.append("#1f7bb4")
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(characters)), gameAmounts, tick_label=characters, color=colors_visible
    )
    _ = ax.set_title(
        f"Number of Matches as {character if opponent.get() == '' else character + '\nAgainst ' + opponent.get()}",
        fontsize=26 if opponent.get() == "" else 14,
    )
    _ = ax.set_ylabel("Character", fontsize=18)
    _ = ax.set_xlabel("Win Rate", fontsize=18)
    _ = ax.bar_label(bars, padding=2)
    ax.invert_yaxis()
    canvas.draw()


def no_of_matches_bar_graph_sorted(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
) -> None:
    global colors, opponent
    pairs: dict[str, float] = {}
    color_pairs: dict[str, str] = {}
    for i in range(len(data[character])):
        char_tuple: tuple[str, float, int] = data[character][i]
        if char_tuple[2] != 0:
            pairs[char_tuple[0]] = char_tuple[2]
            color_pairs[data[character][i][0]] = colors[i]
    color_list: list[str] = [
        color_pairs[k]
        for k, _ in sorted(pairs.items(), key=lambda item: item[1], reverse=True)
    ]
    pairs = dict(sorted(pairs.items(), key=lambda item: item[1], reverse=True))
    if len(pairs) != 0:
        pairs["Average"] = round(sum(pairs.values()) / len(pairs))
        color_list.append("#1f7bb4")
    ax.clear()
    bars: BarContainer = ax.barh(
        range(len(pairs)),
        list(pairs.values()),
        tick_label=list(pairs.keys()),
        color=color_list,
    )
    _ = ax.set_title(
        f"Number of Matches as {character if opponent.get() == '' else character + '\nAgainst ' + opponent.get()}",
        fontsize=26 if opponent.get() == "" else 14,
    )
    _ = ax.set_ylabel("Character", fontsize=18)
    _ = ax.set_xlabel("Win Rate", fontsize=18)
    _ = ax.bar_label(bars, padding=2)
    ax.invert_yaxis()
    canvas.draw()


def filter_replays(
    replays: list[dict[str, Any]],
    character_array: list[str],
    name: str,
    opponent_name: str,
    replay_type: str,
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
        if replay_type != "Online Only" and replay["p2_name"] == "":
            if replay["winner"] == 1:
                _, wins, games = data[replay["p1_char"]][
                    character_array.index(replay["p2_char"])
                ]
                data[replay["p1_char"]][character_array.index(replay["p2_char"])] = (
                    replay["p2_char"],
                    wins + 1,
                    games + 1,
                )
                _, wins, games = data[replay["p2_char"]][
                    character_array.index(replay["p1_char"])
                ]
                data[replay["p2_char"]][character_array.index(replay["p1_char"])] = (
                    replay["p1_char"],
                    wins,
                    games + 1,
                )
            elif replay["winner"] == 2:
                _, wins, games = data[replay["p2_char"]][
                    character_array.index(replay["p1_char"])
                ]
                data[replay["p2_char"]][character_array.index(replay["p1_char"])] = (
                    replay["p1_char"],
                    wins + 1,
                    games + 1,
                )
                _, wins, games = data[replay["p1_char"]][
                    character_array.index(replay["p2_char"])
                ]
                data[replay["p1_char"]][character_array.index(replay["p2_char"])] = (
                    replay["p2_char"],
                    wins,
                    games + 1,
                )
        if opponent_name == "":
            if (
                replay_type != "Offline Only"
                and replay["p1_rank"] != ""
                and replay["p2_rank"] != ""
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
            if replay_type != "Offline Only":
                if replay["p1_name"] == name and replay["winner"] == 1:
                    _, wins, games = data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ]
                    data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ] = (
                        replay["p2_char"],
                        wins + 1,
                        games + 1,
                    )
                elif replay["p1_name"] == name and replay["winner"] != 1:
                    _, wins, games = data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ]
                    data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ] = (
                        replay["p2_char"],
                        wins,
                        games + 1,
                    )
                elif replay["p2_name"] == name and replay["winner"] == 2:
                    _, wins, games = data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ]
                    data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ] = (
                        replay["p1_char"],
                        wins + 1,
                        games + 1,
                    )
                elif replay["p2_name"] == name and replay["winner"] != 2:
                    _, wins, games = data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ]
                    data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ] = (
                        replay["p1_char"],
                        wins,
                        games + 1,
                    )
        else:
            if (
                replay_type != "Offline Only"
                and replay["p1_rank"] != ""
                and replay["p2_rank"] != ""
                and (
                    (
                        replay["p1_name"] == name
                        and replay["p2_name"] == opponent_name
                        and (
                            ranks.index(replay["p1_rank"])
                            not in range(lower_bound, higher_bound)
                            or ranks.index(replay["p2_rank"])
                            not in range(opponent_lower_bound, opponent_higher_bound)
                        )
                    )
                    or (
                        replay["p1_name"] == opponent_name
                        and replay["p2_name"] == name
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
            if replay_type != "Offline Only":
                if (
                    replay["p1_name"] == name
                    and replay["p2_name"] == opponent_name
                    and replay["winner"] == 1
                ):
                    _, wins, games = data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ]
                    data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ] = (
                        replay["p2_char"],
                        wins + 1,
                        games + 1,
                    )
                elif (
                    replay["p1_name"] == name
                    and replay["p2_name"] == opponent_name
                    and replay["winner"] != 1
                ):
                    _, wins, games = data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ]
                    data[replay["p1_char"]][
                        character_array.index(replay["p2_char"])
                    ] = (
                        replay["p2_char"],
                        wins,
                        games + 1,
                    )
                elif (
                    replay["p1_name"] == opponent_name
                    and replay["p2_name"] == name
                    and replay["winner"] == 2
                ):
                    _, wins, games = data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ]
                    data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ] = (
                        replay["p1_char"],
                        wins + 1,
                        games + 1,
                    )
                elif (
                    replay["p1_name"] == opponent_name
                    and replay["p2_name"] == name
                    and replay["winner"] != 2
                ):
                    _, wins, games = data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ]
                    data[replay["p2_char"]][
                        character_array.index(replay["p1_char"])
                    ] = (
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


def analyze_replays(
    replay_folder_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
    name: str,
    opponent_name: str,
    root: Tk,
) -> None:
    """
    Opens a new window to graph replays.
    """
    global \
        view_type, \
        is_sorted, \
        sliders, \
        replay_type_selection, \
        sort_button, \
        corrupt_replays
    character_array_copy: list[str] = [
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
    if replay_folder_path == "":
        _ = messagebox.showerror(
            "Select Folder",
            "Please select a folder.",
            parent=root,
        )
        return
    replays: list[dict[str, Any]] = []
    slash: str = "\\" if system() == "Windows" else "/"
    for file in glob(f"{replay_folder_path}{slash}**{slash}*.ggr", recursive=True):
        try:
            replays.append(
                partial_parse_metadata(
                    file,
                    character_array,
                    metadata_dictionary,
                )
            )
        except ValueError as corrupt:
            corrupt_replays.append(str(corrupt))
            continue
    if len(replays) == 0:
        _ = messagebox.showerror(
            "No Replays Found",
            "No replays could be found in the selected folder. Please select a different folder and try again.",
            parent=root,
        )
        return
    excluded_characters: list[str] = []
    if opponent_name == "":
        replays_p1 = [replay for replay in replays if replay["p1_name"] == name]
        replays_p2 = [replay for replay in replays if replay["p2_name"] == name]
        for i in range(len(character_array_copy) - 1, 0, -1):
            if not any(
                replay["p1_char"] == character_array_copy[i] for replay in replays_p1
            ) and not any(
                replay["p2_char"] == character_array_copy[i] for replay in replays_p2
            ):
                excluded_characters.append(character_array_copy.pop(i))
    else:
        replays_p1 = [
            replay
            for replay in replays
            if replay["p1_name"] == name and replay["p2_name"] == opponent_name
        ]
        replays_p2 = [
            replay
            for replay in replays
            if replay["p1_name"] == opponent_name and replay["p2_name"] == name
        ]
        for i in range(len(character_array_copy) - 1, 0, -1):
            if not any(
                replay["p1_char"] == character_array_copy[i] for replay in replays_p1
            ) and not any(
                replay["p2_char"] == character_array_copy[i] for replay in replays_p2
            ):
                excluded_characters.append(character_array_copy.pop(i))
    excluded_characters.reverse()
    if name == "":
        _ = messagebox.showerror(
            "Enter Username",
            "Please enter a username.",
            parent=root,
        )
        return
    if all(
        replay["p1_name"] != name and replay["p2_name"] != name for replay in replays
    ):
        _ = messagebox.showerror(
            "User Not Found in Replays",
            f"A user with the name {name} could not be found in the replays given, please check your spelling and try again.",
            parent=root,
        )
        return
    if len(corrupt_replays) != 0:
        _ = messagebox.showwarning(
            "Corrupt Replays",
            f"The following replays are corrupt:\n{'\n'.join(corrupt_replays)}\nThe non-corrupt replays have successfully been analyzed.",
            parent=root,
        )
    if len(excluded_characters) != 0:
        if opponent_name == "":
            _ = messagebox.showinfo(
                "Excluded Characters",
                f"No replays with {name} as the following characters could be found:\n{', '.join(character for character in excluded_characters)}\nThe rest of the replays have been successfully analyzed.",
                parent=root,
            )
        else:
            _ = messagebox.showinfo(
                "Excluded Characters",
                f"No replays with {name} as the following characters against {opponent_name} could be found:\n{', '.join(character for character in excluded_characters)}\nThe rest of the replays have been successfully analyzed.",
                parent=root,
            )
    analysis: Toplevel = Toplevel(root)
    analysis.resizable(False, False)
    character: StringVar = StringVar()
    character.set(character_array_copy[0])
    fig, ax = subplots()
    ax.clear()
    fig.set_figwidth(9)
    fig.set_figheight(9)
    _ = ax.set_xlim(0.0, 10.0)
    _ = ax.set_label(f"Matchup Spread for {character}")
    _ = ax.set_xlabel("Win Rate", fontsize=18)
    _ = ax.set_ylabel("Number of Matches", fontsize=18)
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
    replay_type_selection_axes: Axes = fig.add_axes([0.03, 0.005, 0.3, 0.075])
    replay_type_selection = RadioButtons(
        replay_type_selection_axes,
        ["Both Online and Offline", "Offline Only", "Online Only"],
    )
    _ = user_rank.on_changed(
        lambda user: update_replays(
            "",
            replays,
            character_array,
            name,
            opponent_name,
            character.get(),
            ax,
            canvas,
            replay_type_selection.value_selected,
            int(user[0]),
            int(user[1]),
            int(opponent_rank.val[0]),
            int(opponent_rank.val[1]),
        )
    )
    _ = opponent_rank.on_changed(
        lambda opponent: update_replays(
            "",
            replays,
            character_array,
            name,
            opponent,
            character.get(),
            ax,
            canvas,
            replay_type_selection.value_selected,
            int(user_rank.val[0]),
            int(user_rank.val[1]),
            int(opponent[0]),
            int(opponent[1]),
        )
    )
    _ = replay_type_selection.on_clicked(
        lambda s: update_replays(
            s,
            replays,
            character_array,
            name,
            opponent_name,
            character.get(),
            ax,
            canvas,
            replay_type_selection.value_selected,
            int(user_rank.val[0]),
            int(user_rank.val[1]),
            int(opponent_rank.val[0]),
            int(opponent_rank.val[1]),
        )
    )
    scatter_plot(
        character_array_copy[0],
        filter_replays(
            replays,
            character_array,
            name,
            opponent_name,
            replay_type_selection.value_selected,
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
        *character_array_copy,
        command=lambda x: determine_view(
            x,
            filter_replays(
                replays,
                character_array,
                name,
                opponent_name,
                replay_type_selection.value_selected,
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
    switch_button: Button = Button(
        analysis,
        text="Switch View",
        command=lambda: determine_view(
            character.get(),
            filter_replays(
                replays,
                character_array,
                name,
                opponent_name,
                replay_type_selection.value_selected,
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
    switch_button.grid(row=0, column=1)
    sort_button = Button(
        analysis,
        text="Toggle Sorting",
        command=lambda: determine_view(
            character.get(),
            filter_replays(
                replays,
                character_array,
                name,
                opponent_name,
                replay_type_selection.value_selected,
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
    sort_button.grid(row=0, column=2)
    sort_button["state"] = DISABLED
    analysis.protocol("WM_DELETE_WINDOW", analysis.destroy)


def determine_view(
    character: str,
    data: dict[str, list[tuple[str, float, int]]],
    ax: Axes,
    canvas: FigureCanvasTkAgg,
    switch: bool,
    sort: bool,
) -> None:
    global view_type, is_sorted, sort_button
    if switch:
        sort_button["state"] = (
            DISABLED
            if view_type == View.AMOUNTS or view_type == View.AMOUNTS_SORTED
            else NORMAL
        )
        match view_type:
            case View.SCATTER:
                if is_sorted:
                    view_type = View.MATCHUPS_SORTED
                    matchups_bar_graph_sorted(character, data, ax, canvas)
                else:
                    view_type = View.MATCHUPS
                    matchups_bar_graph(character, data, ax, canvas)
            case View.MATCHUPS:
                view_type = View.AMOUNTS
                no_of_matches_bar_graph(character, data, ax, canvas)
            case View.MATCHUPS_SORTED:
                view_type = View.AMOUNTS_SORTED
                no_of_matches_bar_graph_sorted(character, data, ax, canvas)
            case View.AMOUNTS | View.AMOUNTS_SORTED:
                view_type = View.SCATTER
                scatter_plot(character, data, ax, canvas)
    elif sort:
        is_sorted = not is_sorted
        match view_type:
            case View.SCATTER:
                return
            case View.MATCHUPS:
                view_type = View.MATCHUPS_SORTED
                matchups_bar_graph_sorted(character, data, ax, canvas)
            case View.MATCHUPS_SORTED:
                view_type = View.MATCHUPS
                matchups_bar_graph(character, data, ax, canvas)
            case View.AMOUNTS:
                view_type = View.AMOUNTS_SORTED
                no_of_matches_bar_graph_sorted(character, data, ax, canvas)
            case View.AMOUNTS_SORTED:
                view_type = View.AMOUNTS
                no_of_matches_bar_graph(character, data, ax, canvas)
    else:
        sort_button["state"] = DISABLED if view_type == View.SCATTER else NORMAL
        match view_type:
            case View.SCATTER:
                scatter_plot(character, data, ax, canvas)
            case View.MATCHUPS:
                matchups_bar_graph(character, data, ax, canvas)
            case View.MATCHUPS_SORTED:
                matchups_bar_graph_sorted(character, data, ax, canvas)
            case View.AMOUNTS:
                no_of_matches_bar_graph(character, data, ax, canvas)
            case View.AMOUNTS_SORTED:
                no_of_matches_bar_graph_sorted(character, data, ax, canvas)


def jsonify_replays(
    replay_folder_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
    root: Tk,
) -> None:
    """
    Makes JSONs out of replays.
    """
    global corrupt_replays, one_folder_dump_status
    if replay_folder_path == "":
        _ = messagebox.showerror(
            "Select Folder",
            "Please select a folder.",
            parent=root,
        )
        return
    slash: str = "\\" if system() == "Windows" else "/"
    if not path.exists(f"JSONs{slash}"):
        mkdir("JSONs")
    for file in glob(f"{replay_folder_path}{slash}**{slash}*.ggr", recursive=True):
        try:
            data = parse_metadata(
                file,
                character_array,
                metadata_dictionary,
            )
        except ValueError as corrupt:
            corrupt_replays.append(str(corrupt))
            continue
        else:
            subdirectory: str = file[len(replay_folder_path) + 1 : file.rfind(slash)]
            if one_folder_dump_status.get() == 0:
                if not path.exists("JSONs" + slash + subdirectory + slash):
                    mkdir("JSONs" + slash + subdirectory)
                with open(
                    f"JSONs{slash}{file[len(replay_folder_path) + 1:-4]}.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    dump(data, f, ensure_ascii=False, indent=4)
            else:
                if not path.exists("JSONs" + slash):
                    mkdir("JSONs")
                with open(
                    f"JSONs{slash}{file[len(replay_folder_path) + len(subdirectory) + 1:-4]}.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    dump(data, f, ensure_ascii=False, indent=4)
    if len(corrupt_replays) != 0:
        _ = messagebox.showwarning(
            "Corrupt Replays",
            f"The following replays are corrupt:\n{'\n'.join(corrupt_replays)}\nThe non-corrupt replays have successfully been made into JSONs.",
            parent=root,
        )


def select_folder() -> None:
    """
    Selects a folder.
    """
    global folder
    folder = filedialog.askdirectory(
        title="Please select the folder with the replays.",
        initialdir=folder,
        mustexist=True,
    )


def partial_parse_metadata(
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
    _ = replay.seek(0, 0)
    if (
        replay.read(12) != b"\x47\x47\x52\x02\x51\xad\xee\x77\x45\xd7\x48\xcd"
    ):  # Check if .ggr file has the correct header (GGR[\x02]Q[\xAD]îwE×HÍ)
        raise ValueError(replay_file_path[len(folder) + 1 :])
    for label, data in metadata_dictionary.items():
        _ = replay.seek(data[0], 0)
        if data[1] == 256:
            number: int = 0
        else:
            number = int.from_bytes((replay.read(int(data[1] / 8))), "little")
        match label:
            case "p1 rank":
                if parsedDict["p2_name"] == "":  # check if the match was offline
                    parsedDict["p1_rank"] = ""
                else:
                    parsedDict["p1_rank"] = ranks[number]
            case "p2 rank":
                if parsedDict["p2_name"] == "":
                    parsedDict["p2_rank"] = ""
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


def parse_metadata(
    replay_file_path: str,
    character_array: list[str],
    metadata_dictionary: dict[str, tuple[int, int]],
) -> dict[str, Any]:
    """
    Parses the replay metadata into a readable format.
    """
    global ranks
    parsed_dict: dict[str, Any] = {
        "date": "",
        "player1": {
            "steamID": "",
            "name": "",
            "character": "",
            "rounds": 0,
            "score": 0,
            "rank": "",
        },
        "player2": {
            "steamID": "",
            "name": "",
            "character": "",
            "rounds": 0,
            "score": 0,
            "rank": "",
        },
        "EXchars": False,
        "team": False,
        "accentCore": False,
        "unfinished": False,
        "disconnect": False,
        "desync": False,
        "ping": 0,
        "duration": 0.0,
        "winner": None,
    }
    replay: BufferedReader = open(replay_file_path, "rb")
    date: str = ""
    _ = replay.seek(0, 0)
    if (
        replay.read(12) != b"\x47\x47\x52\x02\x51\xad\xee\x77\x45\xd7\x48\xcd"
    ):  # Check if .ggr file has the correct header (GGR[\x02]Q[\xAD]îwE×HÍ)
        raise ValueError(replay_file_path[len(folder) + 1 :])
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
                parsed_dict["date"] = date
            case "p1 rank":
                if (
                    parsed_dict["player2"]["name"] == ""
                ):  # check if the match was offline
                    parsed_dict["player1"]["rank"] = ""
                else:
                    parsed_dict["player1"]["rank"] = ranks[number]
            case "p2 rank":
                if (
                    parsed_dict["player2"]["name"] == ""
                ):  # same as above, both should be player 2
                    parsed_dict["player2"]["rank"] = ""
                else:
                    parsed_dict["player2"]["rank"] = ranks[number]
            case "ex chars?":
                parsed_dict["EXchars"] = number == 1
            case "single or team":
                parsed_dict["team"] = number == 2
            case "+R or AC":
                parsed_dict["accentCore"] = number == 1
            case "ping":
                parsed_dict["ping"] = number
            case "match duration in frames":
                parsed_dict["duration"] = number / 60
            case "p1 rounds":
                parsed_dict["player1"]["rounds"] = number
            case "p2 rounds":
                parsed_dict["player2"]["rounds"] = number
            case "p1 score":
                parsed_dict["player1"]["score"] = number
            case "p2 score":
                parsed_dict["player2"]["score"] = number
            case "winner side":
                if number == 1:
                    parsed_dict["winner"] = "player_1"
                elif number == 2:
                    parsed_dict["winner"] = "player_2"
                else:
                    parsed_dict["winner"] = None
            case "p1 steam id":
                parsed_dict["player1"]["steamID"] = str(number)
            case "p2 steam id":
                if number == 0:
                    parsed_dict["player2"]["steamID"] = None
                else:
                    parsed_dict["player2"]["steamID"] = str(number)
            case "p1 name":
                try:
                    temp = replay.read(32).decode()
                except UnicodeDecodeError:
                    _ = replay.seek(-32, 1)
                    temp = replay.read(32).decode("utf-16")
                finally:
                    parsed_dict["player1"]["name"] = temp.replace("\x00", "", -1)
            case "p2 name":
                if parsed_dict["player2"]["steamID"] is None:
                    parsed_dict["player2"]["name"] = None
                else:
                    try:
                        temp = replay.read(32).decode()
                    except UnicodeDecodeError:
                        _ = replay.seek(-32, 1)
                        temp = replay.read(32).decode("utf-16")
                    finally:
                        parsed_dict["player2"]["name"] = temp.replace("\x00", "", -1)
            case "unfinished match, disconnect, desync bitmask":
                parsed_dict["unfinished"] = number % 2 == 1
                parsed_dict["disconnect"] = number in [2, 3, 6, 7]
                parsed_dict["desync"] = number >= 4
            case "p1 char":
                parsed_dict["player1"]["character"] = character_array[number - 1]
            case "p2 char":
                parsed_dict["player2"]["character"] = character_array[number - 1]
            case _:
                continue
    replay.close()
    return parsed_dict


def main() -> None:
    """
    Main functionality.
    """
    global folder, sliders, one_folder_dump_status, opponent
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
    root.resizable(False, False)
    username_text: Label = Label(root, text="Please enter your username.")
    username_text.grid(row=0, column=0, sticky="we", padx=(15, 5))
    username: Entry = Entry(root)
    username.grid(row=0, column=1, sticky="we", padx=(0, 15), pady=(15, 0))
    opponent_text: Label = Label(
        root, text="Please enter an opponent's\nusername (optional)."
    )
    opponent_text.grid(row=1, column=0, sticky="we")
    opponent = Entry(root)
    opponent.grid(row=1, column=1, sticky="we", padx=(0, 15), pady=(15, 0))
    folder_text: Label = Label(root, text="Please select a folder.")
    folder_text.grid(row=2, column=0, sticky="we")
    folder_button: Button = Button(root, text="Select Folder", command=select_folder)
    folder_button.grid(row=2, column=1, sticky="we", padx=(0, 15), pady=(15, 0))
    one_folder_dump_status = IntVar()
    one_folder_dump: Checkbutton = Checkbutton(
        root,
        text="Dump all JSONs into one folder",
        variable=one_folder_dump_status,
        onvalue=1,
        offvalue=0,
    )
    one_folder_dump.grid(row=3, column=0, columnspan=2, pady=15)
    button_frame: Frame = Frame(root)
    button_frame.grid(row=4, column=0, columnspan=2)
    jsonify_button: Button = Button(
        button_frame,
        text="JSON-ify Replays",
        command=lambda: jsonify_replays(
            folder, character_array, metadata_dictionary, root
        ),
    )
    jsonify_button.grid(row=0, column=0, padx=(0, 40), pady=(0, 10))
    analyze_button: Button = Button(
        button_frame,
        text="Analyze Replays",
        command=lambda: analyze_replays(
            folder,
            character_array,
            metadata_dictionary,
            username.get(),
            opponent.get(),
            root,
        ),
    )
    analyze_button.grid(row=0, column=1, padx=(40, 0), pady=(0, 10))
    root.protocol("WM_DELETE_WINDOW", exit)
    root.mainloop()


if __name__ == "__main__":
    main()
