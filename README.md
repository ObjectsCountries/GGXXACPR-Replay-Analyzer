# GGXXACPR Replay Analyzer

This simple GUI app displays information gathered from *Guilty Gear XX Accent Core Plus R* replays, and plots said information onto graphs.

## How to Use

Matplotlib is required, install here: https://matplotlib.org/stable/install/index.html

The only script required is [\_\_main__.py](__main__.py).

Simply enter your username, select the folder with the replays (the app should go to the correct one by default), and click either of the buttons at the bottom.

Selecting a folder is not necessary unless your replays are not in the default folder (On Windows: C:\Users\\(your username)\Documents\ARC SYSTEM WORKS\GGXXAC\Replays\\).

The “JSON-ify Replays” button will make a JSON out of every file in the replay folder, and the “Analyze Replays” button opens a window showing the aforementioned graphs. **Note that you do not need to make the JSONs before viewing the graphs.** If a file does not have the proper heading for a +R replay, it will be marked as corrupt and skipped. The program will warn the user of any corrupt replays before converting the non-corrupt replays to JSONs/analyzing the non-corrupt replays.

Once the second window has opened, select your character with the dropdown at the top left. The “Switch View” button will switch between a scatter plot of both matchup win rates and matches played, a bar graph of matchup win rates, and a bar graph of matches played, all for the selected character. Hovering over any point on the scatter plot will display further details about matchup win rates and number of matches played. The “Sort View” button will sort the bar graphs from highest to lowest, with the average always at the bottom. The two sliders show the range of online ranks for you (first slider) and your opponent (second slider). The radio buttons at the bottom filter between offline replays, online replays, and both.

## CLI Scripts

The original CLI Scripts (courtesy of @joefish. and @izyb on Discord) can be found in the [CLI Scripts](CLI%20Scripts) folder. [usingOrganizeReplaysMetaData.docx](CLI%20Scripts/usingOrganizeReplaysMetaData.docx?raw=1) and [howToUseReplayStats.txt](CLI%20Scripts/howToUseReplayStats.txt) have been converted to Markdown and combined into a single [README.md](CLI%20Scripts/README.md) file, whereas the Python scripts are unaltered.

## Contributing

If you would like to contribute, please feel free to fork this project. Additionally, please message me on Discord (@objectscountries) about bugs, potential new features, etc. Alternatively, open up an issue in this repo for bug reports.

## To Do

- [ ] Integrate with https://acpr.frameone.net/
  - [ ] Add download feature (ensure duplicates are not downloaded)
  - [ ] Add upload feature (with feedback telling user how many were already uploaded, failed to upload, etc.)
- [ ] Add feature to filter replays by opponent
