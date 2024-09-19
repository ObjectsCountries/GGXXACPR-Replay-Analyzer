import os
import sys
import shutil
import re

#Ensure this filepath is correct.
file_path = 'C:\\Users\\' + os.getlogin() + '\\Documents\\ARC SYSTEM WORKS\\GGXXAC\\Replays'


#this program organizes places your most recent replay into a seperate folder (Starred Matches)for ease of access later.

replay_list = [] #need to create a storage list to sift through the folders in the file path.
replay_files = os.listdir(file_path) #get a list of replay files

for file in replay_files: #do the following to each file
	if 'ggr' in file.lower(): #ensure its a replay file
		replay_list.append(file)

if (len(replay_list) > 0): #make sure theres a replay to star.
	star_file_path = file_path+"\\Starred Matches" #ensure the Starred Matches folder exists.
	if not(os.path.exists(star_file_path)):
		os.mkdir(star_file_path)
	shutil.move(file_path+"\\"+replay_list.pop(),star_file_path) #move the most recent replay there. 

	print("Replay Starred!")
else:
	print("you have no replays")