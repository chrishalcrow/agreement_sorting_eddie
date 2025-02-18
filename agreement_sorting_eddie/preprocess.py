import numpy as np
import spikeinterface.full as si
from Elrond.Helpers import get_chronologized_recording_paths, get_session_names
import sys
from defaults import return_protocols
from pathlib import Path

from spikeinterface.preprocessing.inter_session_alignment.session_alignment import (
    get_estimate_histogram_kwargs,
    align_sessions,
)



# mouse = sys.argv[1]
# day = sys.argv[2]
# protocol = int(sys.argv[3])
# project_path = sys.argv[4]

def run_preprocess(mouse, day, protocol, project_path, n_jobs=8):

    protocols = return_protocols()
    this_protocol = protocols[int(protocol)]
    presets = {0: "nonrigid_fast_and_accurate", 1: "nonrigid_fast_and_accurate", 2: "dredge_fast", 3:"nonrigid_fast_and_accurate"}

    deriv_folder = project_path + f"derivatives/M{mouse}/D{day}"
    Path(deriv_folder).mkdir(exist_ok=True, parents=True)

    si.set_global_job_kwargs(n_jobs=n_jobs, pool_engine="process")

    mouse = int(mouse)
    day = int(day)

    data_folder = project_path + "data/"
    rec_paths = get_chronologized_recording_paths(data_folder, mouse, day)
    session_names = get_session_names(rec_paths)

    if mouse <= 21:
        raw_recordings_list = [si.read_zarr(rec_path + '/recording.zarr') for rec_path in rec_paths]
    else:
        raw_recordings_list = [si.read_openephys(rec_path) for rec_path in rec_paths]

    groups = np.unique(np.array(raw_recordings_list[0].get_property('group')))

    bad_channels = []
    for raw_recording in raw_recordings_list:
        recs_by_group = raw_recording.split_by('group')
        for rec_group in recs_by_group.values():
            bad_channels_one_rec, _ = si.detect_bad_channels(rec_group)
            bad_channels.extend(bad_channels_one_rec)

    bad_channels = list(set(bad_channels))
    print('bad chans: ', bad_channels)

    raw_recordings_list = [raw.remove_channels(remove_channel_ids = bad_channels) for raw in raw_recordings_list]

    recs_per_group={}
    for group in groups:
            
        recs_group = [rec.channel_slice(channel_ids=rec.channel_ids[rec.get_property('group')==group]) for rec in raw_recordings_list]
        pp_recs = [si.whiten(si.bandpass_filter(si.phase_shift(rec_group)),dtype="float32", mode="local") for rec_group in recs_group]
            
        if protocol == 3:

            concatenated_recs = si.concatenate_recordings( [pp_rec for pp_rec in pp_recs] )
            rec_and_motion = si.correct_motion(concatenated_recs, preset=presets[0], output_motion=True, output_motion_info=True)
            recs_per_group[group] = rec_and_motion[0]

            si.plot_drift_raster_map(
                peaks = rec_and_motion[2]['peaks'],
                peak_locations = rec_and_motion[2]['peak_locations'],
                sampling_frequency=30_000
            ).figure.savefig(deriv_folder + f"/drift_raster_P{protocol}_G{group}.png")

        else:

            # motion correction per shank
            recs_and_motions = [si.correct_motion(rec, preset=presets[protocol], output_motion=True, output_motion_info=True) for rec in pp_recs]
            
            peaks_list = [ rec_and_motion[2]['peaks'] for rec_and_motion in recs_and_motions]
            peak_locations_list = [ rec_and_motion[2]['peak_locations'] for rec_and_motion in recs_and_motions]
                
            estimate_histogram_kwargs = get_estimate_histogram_kwargs()
            estimate_histogram_kwargs["histogram_type"] = "activity_2d"  # TODO: RENAME

            if protocol == 0:
                recs_to_correct = [pp_rec for pp_rec in pp_recs]

            if protocol == 1:

                intersected_channels = set(recs_and_motions[0][0].channel_ids)
                for cm_rec in recs_and_motions[1:]:
                    intersected_channels = intersected_channels.intersection(cm_rec[0].channel_ids)
                intersected_channels = list(intersected_channels)
                
                recs_to_correct = [cm_rec[0].channel_slice(channel_ids=list(intersected_channels)) for cm_rec in recs_and_motions]
                    
            corrected_recordings_list, extra_info = align_sessions(
                recs_to_correct,
                peaks_list,
                peak_locations_list,
                estimate_histogram_kwargs=estimate_histogram_kwargs
            )

            recs_per_group[group] = si.concatenate_recordings(corrected_recordings_list)

    full_rec = si.aggregate_channels(list(recs_per_group.values()))
    full_rec.save_to_folder(f"{deriv_folder}/full/rec_preprocessing_whitened_corrected_{protocol}", overwrite=True)

if __name__ == "__main__":
    run_preprocess(mouse, day, protocol, project_path)
