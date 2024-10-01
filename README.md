# GGXXACPR Replay Analyzer

This interactive GUI app analyzes information gathered from *Guilty Gear XX Accent Core Plus R* replays, and plots said information onto graphs.

## How to Use

### Required Downloads

Python is needed to run the script, install here: https://www.python.org/downloads/

Matplotlib is needed to render the graphs, install here: https://matplotlib.org/stable/install/index.html

The only file that has to be downloaded from this repo is [replay_analyzer.py](replay_analyzer.py). This script does not have to be in the same folder as the replays.

### Setup

Simply enter your username, select the folder with the replays (the app should go to the correct one by default), and click either of the buttons at the bottom. Optionally, enter a second player’s name to filter for replays only between you and them.

Selecting a folder is not necessary unless your replays are not in the default folder (On Windows: C:\Users\\(your username)\Documents\ARC SYSTEM WORKS\GGXXAC\Replays\\), but opening the folder selector and closing it without selecting anything will yield an empty path as the selected folder, and the program will prompt the user to select a folder.

If a file does not have the proper heading for a +R replay, it will be marked as corrupt and skipped. The program will warn the user of any corrupt replays before converting the non-corrupt replays to JSONs/analyzing the non-corrupt replays.

### JSONs

The “JSON-ify Replays” button will make a JSON out of every file in the replay folder, outputting to a new folder called “JSONs” located where the script is. When making the JSONs, there is a checkbox that determines whether the program preserves folder structure, or dumps everything into one folder. **Note that you do not need to make the JSONs before viewing the graphs.**

### Replay Analysis

The “Analyze Replays” button opens a second window showing a scatter plot for a given character (defaults to Sol). Select your character with the dropdown at the top left. If any characters are missing from a graph, that’s because there are no replays with the selected character against that character/those characters.

Hovering over any point on the scatter plot will display further details about matchup win rates and number of matches played.

The “Switch View” button will switch between the scatter plot of matchup win rates and matches played, a bar graph of matchup win rates, and a bar graph of matches played, all for the selected character.

The “Toggle Sorting” button will switch between sorting the bar graphs by character and by amount (highest to lowest), with the average always at the bottom.

The two sliders show the range of online ranks for you (first slider) and your opponent (second slider). The radio buttons at the bottom filter between offline replays, online replays, and both.

## CLI Scripts

The original CLI Scripts (courtesy of @joefish. and @izyb on Discord) can be found in the [CLI Scripts](CLI%20Scripts) folder. usingOrganizeReplaysMetaData.docx and howToUseReplayStats.txt have been converted to Markdown and combined into a single [README.md](CLI%20Scripts/README.md) file, whereas the Python scripts are unaltered.

## Contributing

If you would like to contribute, please feel free to fork this project. Additionally, please message me on Discord (@objectscountries) about bugs, potential new features, etc. Alternatively, open up an issue in this repo for bug reports.

## To Do

- [ ] Integrate with https://acpr.frameone.net/
  - [ ] Add download feature (ensure duplicates are not downloaded)
  - [ ] Add upload feature (with feedback telling user how many were already uploaded, failed to upload, etc.)
