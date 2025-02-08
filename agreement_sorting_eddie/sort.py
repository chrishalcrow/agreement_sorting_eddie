import sys
import spikeinterface.full as si
from defaults import return_protocols

mouse = int(sys.argv[1])
day = int(sys.argv[2])
protocol = int(sys.argv[3])
project_path = sys.argv[4]
sorter_name = sys.argv[5]

protocols = return_protocols()
this_protocol = protocols[int(protocol)]

sorter_kwargs = this_protocol['sorters'][sorter_name]
extensions_to_compute = this_protocol['extensions']

deriv_folder = project_path + f"derivatives/M{mouse}/D{day}"
rec_folder = f"{deriv_folder}/full/rec_preprocessing_whitened_corrected_{protocol}"

sort_folder = f"{deriv_folder}/full/{sorter_name}_sort_{protocol}"

rec = si.read_binary_folder(rec_folder)

si.set_global_job_kwargs(n_jobs=8)

sort=None
if sorter_name == "mountainsort5":
    si.set_global_job_kwargs(n_jobs=2)
    import mountainsort5 as ms5
    sort = ms5.sorting_scheme3(
        rec,
        sorting_parameters=ms5.Scheme3SortingParameters(
            block_sorting_parameters=ms5.Scheme2SortingParameters(
                phase1_detect_channel_radius=100,
                detect_channel_radius=50,
                training_duration_sec=25,
                phase1_svd_solver='covariance_eigh',
                training_recording_sampling_mode='uniform'
            ),
            block_duration_sec=10*60
        )
    )
    sort.save(folder=sort_folder, overwrite=True)
else:
    sort = si.run_sorter_by_property(
        recording=rec, 
        sorter_name=sorter_name, 
        folder=sort_folder, 
        remove_existing_folder=True, 
        verbose=True, 
        grouping_property='group',
        **this_protocol['sorters'][sorter_name]
    )

sort = si.si.remove_excess_spikes(sorting = sort, recording=rec)

sa_folder = f"{deriv_folder}/full/{sorter_name}_{protocol}"
sa = si.create_sorting_analyzer(recording=rec, sorting=sort, format="zarr", folder=sa_folder, overwrite=True)

sa.compute(extensions_to_compute)

report_folder = f"{deriv_folder}/full/{sorter_name}_sa_{protocol}_report"
si.export_report(sorting_analyzer=sa, output_folder=report_folder)