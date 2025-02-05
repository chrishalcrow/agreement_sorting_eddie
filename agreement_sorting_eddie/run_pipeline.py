import sys
import os
from Elrond.Helpers.create_eddie_scripts import stagein_data, run_python_script, run_stageout_script, get_filepaths_on_datastore
from Elrond.Helpers.upload_download import get_session_names, chronologize_paths
from pathlib import Path
import numpy as np
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("mouse", help="Mouse number, e.g. 20", type=int)
parser.add_argument("day", help="Day number, e.g. 14", type=int)
parser.add_argument("protocol", help="Which sorter protocol to use. Find the details in defaults.py")
parser.add_argument("project_path", help="Folder containing 'data' and 'derivative' folders")

args = parser.parse_args()

mouse = args.mouse
day = args.day
protocol = args.protocol
project_path = args.project_path

print(f"Doing mouse {mouse}, day {day}...")

data_path = project_path + f"data/M{mouse}_D{day}"
Path(data_path).mkdir(exist_ok=True)

# Get the filenames from datastore.
filenames_path = project_path + f"data/M{mouse}_D{day}/data_folder_names.txt"

if Path(filenames_path).exists() is False:
    get_filepaths_on_datastore(mouse, day, project_path)

while Path(filenames_path).exists() is False:
    time.sleep(5)

paths_on_datastore = []
with open(filenames_path) as f:
    paths_on_datastore = f.read().splitlines()

session_names = get_session_names(chronologize_paths(paths_on_datastore))

print(f"...which contains sessions: {session_names}")

stagein_job_name = f"M{mouse}_{day}_in_"

raw_recording_paths = []
for a, (session_name, path_on_datastore) in enumerate(zip(session_names, paths_on_datastore)):
    raw_recording_paths.append(stagein_data(mouse, day, project_path, path_on_datastore, job_name = stagein_job_name + session_name))

