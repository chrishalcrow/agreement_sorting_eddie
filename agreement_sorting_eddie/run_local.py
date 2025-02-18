import sys
import os
from Elrond.Helpers.upload_download import get_session_names, chronologize_paths, get_chronologized_recording_paths

from preprocess import run_preprocess
from sort import run_sort

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

    args = parser.parse_args()

    mouse = args.mouse
    day = args.day
    protocol = args.protocol
    project_path = args.project_path

    print(f"Doing mouse {mouse}, day {day}...")

    data_path = project_path + f"data/"

    chronologized_recording_paths = get_chronologized_recording_paths(data_path, mouse, day)
    print(f"Found recordings: {chronologized_recording_paths}")
    session_names = get_session_names(chronologized_recording_paths)

    print(f"...which contains sessions: {session_names}")

    run_preprocess(mouse, day, protocol, project_path)


