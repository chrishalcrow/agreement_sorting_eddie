import spikeinterface.full as si
from Elrond.Helpers import get_chronologized_recording_paths, get_session_names

from spikeinterface.preprocessing.inter_session_alignment.session_alignment import (
    get_estimate_histogram_kwargs,
    align_sessions,
    )

import sys

mouse = sys.argv[1]
day = sys.argv[2]
protocol = sys.argv[3]
project_path = sys.argv[4]

deriv_folder = project_path + f"derivatives/M{mouse}/D{day}"

si.set_global_job_kwargs(n_jobs=8, pool_engine="process")

mouse = int(mouse)
day = int(day)

data_folder = project_path + "data/"

rec_paths = get_chronologized_recording_paths(data_folder, mouse, day)
session_names = get_session_names(rec_paths)

if mouse <= 21:
    raw_recordings_list = [si.read_zarr(rec_path + '/recording.zarr') for rec_path in rec_paths]
else:
    raw_recordings_list = [si.read_openephys(rec_path) for rec_path in rec_paths]

bad_channels = []

for raw in raw_recordings_list:
    bad_channels_one_rec, _ = si.detect_bad_channels(raw)
    bad_channels.extend(bad_channels_one_rec)

bad_channels = list(set(bad_channels))

print("Removing bad channels: ", bad_channels)

raw_recordings_list = [raw.remove_channels(remove_channel_ids = bad_channels) for raw in raw_recordings_list]

recordings_list = [ si.whiten(si.bandpass_filter(si.phase_shift(raw)),dtype="float32") for raw in raw_recordings_list ]

recs_and_motions = [si.correct_motion(rec, preset="nonrigid_fast_and_accurate", output_motion=True, output_motion_info=True) for a, rec in enumerate(recordings_list)]

intersected_channels = set(recs_and_motions[0][0].channel_ids)
for cm_rec in recs_and_motions[1:]:
    intersected_channels = intersected_channels.intersection(cm_rec[0].channel_ids)
intersected_channels = list(intersected_channels)

all_cm_recs_intersect = [cm_rec[0].channel_slice(channel_ids=list(intersected_channels)) for cm_rec in recs_and_motions]

peaks_list = [ rec_and_motion[2]['peaks'] for rec_and_motion in recs_and_motions]
peak_locations_list = [ rec_and_motion[2]['peak_locations'] for rec_and_motion in recs_and_motions]

estimate_histogram_kwargs = get_estimate_histogram_kwargs()
estimate_histogram_kwargs["histogram_type"] = "activity_2d"  # TODO: RENAME

corrected_recordings_list, extra_info = align_sessions(
    all_cm_recs_intersect,
    peaks_list,
    peak_locations_list,
    estimate_histogram_kwargs=estimate_histogram_kwargs
)

print("shifts: ", extra_info)

rec = si.concatenate_recordings(corrected_recordings_list)
rec.save_to_folder(f"{deriv_folder}/full/rec_preprocessing_whitened_corrected_{protocol}")