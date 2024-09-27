# GGXXACPR Replay Analyzer

This simple GUI app displays information gathered from *Guilty Gear XX Accent Core Plus R* replays, and plots the information onto graphs.

## How To Use

Matplotlib is required, download here: https://matplotlib.org/stable/install/index.html

The only script required to download is \_\_main__.py.

Simply enter your username, select the folder with the replays (the app should go to the correct one by default), and click either of the buttons at the bottom.

Selecting a folder is not necessary unless your replays are not in the default folder (On Windows: C:\Users\\(your username)\Documents\ARC SYSTEM WORKS\GGXXAC\Replays).

The left button will make a JSON out of every file in the replay folder, and the right button opens a window showing the aforementioned graphs. **Note that you do not need to make the JSONs before viewing the graphs.**

Once the second window has opened, select your character with the dropdown on the left. The “Switch View” button will switch between a scatter plot, a bar graph of matchup win rates, and a bar graph of matches played, all for the selected character. The “Sort View” button will sort the bar graphs from highest to lowest, with the average always at the bottom. The two sliders show the range of online ranks of you (first slider) and your opponent (second slider).
