#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config file for AeroCom PhaseIII optical properties experiment
"""
import os
import logging

from pyaerocom.aeroval import EvalSetup, ExperimentProcessor

logger = logging.getLogger(__name__)

### Some info on available classification codes in EEA-NRT (should be the same as in GHOST theoretically)

# EEA-NRT area codes (key: area_classification): 'rural', 'rural-nearcity',
# 'rural-regional', 'rural-remote', 'suburban', 'urban'
# EEA-NRT station codes (key: station_classification):'background', 'industrial', 'traffic'

### Define filters for the obs subsets

# BASE FILTERS
ALTITUDE_FILTER = {
    'altitude': [0, 1000]
}

# Setup for models used in analysis
MODELS = {
    'NorESM': dict(
        # model_id='jang.test', ),
        model_id='NorESM2.5-hybrid.20240822', ),
    'MODISTerra': dict(
        model_id='MODIS6.1terra', ),
    # 'webname': dict(
    #     model_id='model_name_from_files', ),

}

# Setup for available ground based observations (ungridded)

VAR_OUTLIER_RANGES = {
    'concpm10': [-1, 5000],  # ug m-3
    'concpm25': [-1, 5000],  # ug m-3
    'vmrno2': [-1, 5000],  # ppb
    'vmro3': [-1, 5000]  # ppb
}

AERONET_SITE_FILTER = dict(station_name='DRAGON*', negate='station_name')
OBS_GROUNDBASED = {

    'Aeronet': dict(obs_id='AeronetSunV3Lev2.daily',
                           obs_vars=['od550aer', ],
                           obs_vert_type='Column',
                           obs_filters={**ALTITUDE_FILTER,
                                        **AERONET_SITE_FILTER},
                           min_num_obs={'monthly': {'daily': 3}},
                           ),
    'EBAS': dict(obs_id='EBASMC',
                           obs_vars=['concso2', 'concso4t'],
                           obs_vert_type='Surface',
                           obs_filters={**ALTITUDE_FILTER,
                                        },
                           ),

}

# Setup for supported satellite evaluations
OBS_SAT = {}

OBS_CFG = {
    **OBS_GROUNDBASED,
    **OBS_SAT
}

# DEFAULT_RESAMPLE_CONSTRAINTS = dict(
#     monthly=dict(daily=21),
#     daily=dict(hourly=18)
# )

CFG = dict(

    model_cfg=MODELS,
    obs_cfg=OBS_CFG,

    json_basedir=os.path.abspath("/nird/home/jang/data/aeroval/data"),
    coldata_basedir=os.path.abspath("/nird/home/jang/data/aeroval/coldata"),
    io_aux_file=os.path.abspath("/nird/home/jang/data/aeroval/pyaeroval_config/eval_py/gridded_io_aux.py"),
    var_scale_colmap_file=os.path.abspath(
            "/nird/home/jang/data/aeroval/pyaeroval_config/config_files/var_scale_colmap.ini"
        ),

    # if True, existing colocated data files will be deleted
    reanalyse_existing=True,
    only_json=False,
    add_model_maps=True,
    only_model_maps=False,

    # clear_existing_json=False,
    clear_existing_json=True,

    # if True, the analysis will stop whenever an error occurs (else, errors that
    # occurred will be written into the logfiles)
    raise_exceptions=False,

    # Regional filter for analysis
    filter_name='ALL-wMOUNTAINS',

    # colocation frequency (no statistics in higher resolution can be computed)
    ts_type='monthly',

    map_zoom='World',

    freqs=['monthly'],
    # periods=['2020-2021', '2021'],
    periods=['2010'],
    main_freq='monthly',
    # stats_main_freq = 'daily',
    zeros_to_nan=False,
    # add_trends=True,
    # trends_min_yrs=3,

    # min_num_obs=DEFAULT_RESAMPLE_CONSTRAINTS,
    colocate_time=False,

    obs_remove_outliers=True,
    model_remove_outliers=False,
    harmonise_units=True,
    # regions_how='htap',
    # regions_how='default',

    annual_stats_constrained=False,

    proj_id='nird_test',
    exp_id = 'NorESM_Nird',
    exp_name='testing analysis for running on NIRD',
    exp_descr=('some testing analysis for nird'),
    exp_pi='Jan Griesfeller (jan.griesfeller@met.no)',

    public=True,
    # directory where colocated data files are supposed to be stored
    weighted_stats=True,
)


if __name__ == '__main__':

    import matplotlib.pyplot as plt

    from pyaerocom import change_verbosity
    change_verbosity(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    plt.close('all')
    stp = EvalSetup(**CFG)

    ana = ExperimentProcessor(stp)
    print(stp)

    # ana.exp_output.delete_experiment_data()
    # res=ana.exp_output._results_summary()
    # ana.update_interface()
    ana.exp_output.delete_experiment_data()

    # data = ana.read_model_data('AEROCOM-MEDIAN', 'od550gt1aer')
    res = ana.run()
