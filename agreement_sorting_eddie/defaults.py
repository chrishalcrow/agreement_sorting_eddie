def return_protocols():

    protocols = {
        0: {
            'sorters': {
                'kilosort4': {
                    'do_CAR': False,
                    'do_correction': False,
                    'skip_kilosort_preprocessing': True,
                    'use_binary_file': False,
                },
                'spykingcircus2': {
                    'apply_preprocessing': False,
                    'apply_whitening': False,
                    'cache_preprocessing': {},
                    'apply_motion_correction': False,
                    'job_kwargs': {'n_jobs': 8},
                    'matching': {'method': 'wobble'}
                },
                'mountainsort5': {}
            },
            'extensions': {
                "noise_levels": {},
                "random_spikes": {},
                "waveforms": {},
                "templates": {"operators": ["average", "std"]},
                "correlograms": {},
                "spike_amplitudes": {},
                "spike_locations": {},
                "template_similarity": {},
                "quality_metrics": {},
                "template_metrics": {"include_multi_channel_metrics": True}
            }
        }
    }

    protocols[1] = protocols[0]
    protocols[2] = protocols[0]

    return protocols