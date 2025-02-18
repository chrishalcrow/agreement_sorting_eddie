import sys
import os
from Elrond.Helpers.upload_download import get_session_names, chronologize_paths, get_chronologized_recording_paths

from preprocess import run_preprocess
from sort import run_sort
from defaults import return_protocols

from pathlib import Path
import numpy as np
import argparse
import time
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("mouse", help="Mouse number, e.g. 20", type=int)
    parser.add_argument("day", help="Day number, e.g. 14", type=int)
    parser.add_argument("protocol", help="Protocol for preprocessing: e.g. 3. Protocols can be found in defaults.py")
    parser.add_argument("project_path", help="Folder containing 'data' and 'derivative' folders")
    parser.add_argument("--sorter_name", help="If you want to run a specific sorter for this protocol, e.g. kilosort4")
    parser.add_argument("--do_preprocessing", help="Skip the preprocessing?", default=True, type=bool)

    args = parser.parse_args()

    mouse = int(args.mouse)
    day = int(args.day)
    protocol = int(args.protocol)
    project_path = args.project_path
    sorter_name = args.sorter_name

    if args.sorter_name:
        sorter_name = args.sorter_name
    else:
        sorter_name = None



    protocols = return_protocols()
    this_protocol = protocols[int(protocol)]

    print(f"Doing mouse {mouse}, day {day}...")

    data_path = project_path + f"data/"

    chronologized_recording_paths = get_chronologized_recording_paths(data_path, mouse, day)
    print(f"Found recordings: {chronologized_recording_paths}")
    session_names = get_session_names(chronologized_recording_paths)

    print(f"...which contains sessions: {session_names}")

    if sorter_name is None:
        sorter_names = this_protocol['sorters'].keys()
    else:
        sorter_names = [sorter_name]



    if args.do_preprocessing
        print("Doing preprocessing")
        run_preprocess(mouse, day, protocol, project_path)

    print(f"Going to sort with {sorter_names}")

    for sorter_name in sorter_names:
        run_sort(mouse, day, protocol, project_path, sorter_name)

