import sys
import os
from Elrond.Helpers.create_eddie_scripts import stagein_data, run_python_script, run_stageout_script, get_filepaths_on_datastore
from Elrond.Helpers.upload_download import get_session_names, chronologize_paths
from pathlib import Path
import numpy as np
import argparse
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("mouse", help="Mouse number, e.g. 20", type=int)
parser.add_argument("day", help="Day number, e.g. 14", type=int)
parser.add_argument("protocol", help="Which sorter protocol to use. Find the details in defaults.py")
parser.add_argument("project_path", help="Folder containing 'data' and 'derivative' folders")
parser.add_argument("which_bits", help="Which parts of the pipeline do you want to do? '1111' is all '0011' is sort+copy etc.")

args = parser.parse_args()

mouse = args.mouse
day = args.day
protocol = args.protocol
project_path = args.project_path
which_bits = list(args.which_bits)

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

mouseday_string = f"M{mouse}_{day}"

stagein_job_name = f"{mouseday_string}_in_"

stagein_job_names = ""
for session_name in session_names:
    stagein_job_names += stagein_job_name + session_name + ","
stagein_job_names = stagein_job_names[:-1]

if which_bits[0] == '1':
    for a, (session_name, path_on_datastore) in enumerate(zip(session_names, paths_on_datastore)):
        script_file_path = stagein_job_name + session_name + ".sh"
        stagein_data(mouse, day, project_path, path_on_datastore, 
            job_name = stagein_job_name + session_name,
            script_file_path=script_file_path
        )

scripts_folder = str(Path(sys.argv[0]).parent)

if which_bits[1] == '1':
    pp_job_name = f"{mouseday_string}_pp_{protocol}"
    run_python_script(
        f"{scripts_folder}/preprocess.py {mouse} {day} {protocol} {project_path}",
        hold_jid = stagein_job_names,
        job_name = pp_job_name,
        cores=8,
    )

if which_bits[2] == '1':
    for cores, sorter_name in zip([8,8,2], ['kilosort4', 'spykingcircus2', 'mountainsort5']):
        run_python_script(
            f"{scripts_folder}/sort.py {mouse} {day} {protocol} {project_path} {sorter_name}",
            hold_jid = pp_job_name,
            job_name = f"{mouseday_string}_{sorter_name}_{protocol}",
            cores=cores,
        )