protocols = {
    1: {
        'sorters': {
            'kilosort4': {
                'do_CAR': False, 
                'do_correction': False,
                'skip_kilosort_preprocessing': True,
                'use_binary_file': False,
                'n_jobs': 8,
            },
            'spykingcircus2': {
                'apply_preprocessing': False, 
                'apply_whitening': False, 
                'cache_preprocessing': {}, 
                'apply_motion_correction': False,
                'n_jobs': 8, 
                'pool_engine': 'process'
            }

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

def return_protocols():
    return protocols
