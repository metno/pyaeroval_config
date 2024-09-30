#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config file for AeroCom PhaseIII test project
"""
from pyaerocom.io.aux_read_cubes import (
    add_cubes,
    subtract_cubes,
    divide_cubes,
    multiply_cubes,
    compute_angstrom_coeff_cubes,
    mmr_to_vmr_cube,
)
from pyaerocom.molmasses import get_molmass

# ToDo: migrate these methods into pyaerocom.io.aux_read_cubes and harmonise
# (e,g, molmasses and units handling, etc...)

M_N = 14.006
M_O = 15.999
M_H = 1.007


def mmr_from_vmr(cube):
    """
    Convvert gas volume/mole mixing ratios into mass mixing ratios.

    Parameters
    ----------
    cube : iris.cube.Cube
        A cube containing gas vmr data to be converted into mmr.
    Returns
    -------
    cube_out : iris.cube.Cube
        Cube containing mmr data.
    """
    var_name = cube.var_name
    M_dry_air = get_molmass("air_dry")
    M_variable = get_molmass(var_name)

    cube_out = (M_variable / M_dry_air) * cube
    return cube_out


def conc_from_vmr_STP(cube):
    R = 287.058  # R for dry air

    standard_T = 293
    standard_P = 101300

    mmr_cube = mmr_from_vmr(cube)
    rho = R * standard_T / standard_P

    cube_out = rho * mmr_cube
    return cube_out


def calc_concnh3(vmrnh3):
    if vmrnh3.units == "1e-9":
        vmrnh3.units = "ppb"
    assert vmrnh3.units == "ppb"

    in_ts_type = vmrnh3.ts_type

    concnh3 = conc_from_vmr_STP(vmrnh3.cube)
    concnh3.units = "ug/m3"
    concnh3 *= M_N / (M_N + M_H * 3)
    concnh3.units = "ug N m-3"

    concnh3.attributes["ts_type"] = in_ts_type

    return concnh3


def calc_concnh4(concnh4):
    if concnh4.units == "ug m-3" or concnh4.units == "ug/m**3":
        concnh4.units = "ug/m3"
    assert concnh4.units == "ug/m3"

    in_ts_type = concnh4.ts_type
    concnh4 = concnh4.cube
    concnh4 *= M_N / (M_N + M_H * 4)
    concnh4.units = "ug N m-3"

    concnh4.attributes["ts_type"] = in_ts_type

    return concnh4


def calc_conchno3(vmrhno3):
    if vmrhno3.units == "1e-9":
        vmrhno3.units = "ppb"
    assert vmrhno3.units == "ppb"

    in_ts_type = vmrhno3.ts_type
    conchno3 = conc_from_vmr_STP(vmrhno3.cube)
    conchno3.units = "ug/m3"
    conchno3 *= M_N / (M_H + M_N + M_O * 3)
    conchno3.attributes["ts_type"] = in_ts_type
    conchno3.units = "ug N m-3"

    return conchno3


def calc_fine_concno310(concno3f):
    return calc_concno310(concno3f=concno3f, concno3c=None)


def calc_concno310(concno3c, concno3f):
    if concno3c != None:
        if concno3c.units == "ug m-3" or concno3c.units == "ug/m**3":
            concno3c.units = "ug/m3"
        assert concno3c.units == "ug/m3"
    assert concno3f.units == "ug/m3"

    in_ts_type = concno3f.ts_type
    if concno3c != None:
        concno310 = add_cubes(concno3f.cube, concno3c.cube)
    else:
        concno310 = concno3f.cube

    concno310 *= M_N / (M_N + M_O * 3)
    concno310.attributes["ts_type"] = in_ts_type
    concno310.units = "ug N m-3"
    return concno310


def calc_ratpm10pm25(pm10, pm25):

    in_ts_type = pm10.ts_type
    if pm25 != None:
        ratpm10pm25 = divide_cubes(pm10.cube, pm25.cube)
    else:
        ratpm10pm25 = pm10.cube

    ratpm10pm25.attributes["ts_type"] = in_ts_type
    ratpm10pm25.units = "1"
    return ratpm10pm25


def calc_concno325(concno3f):
    assert concno3f.units == "ug/m3"
    in_ts_type = concno3f.ts_type
    concno325 = concno3f.cube
    concno325 *= M_N / (M_N + M_O * 3)

    concno325.attributes["ts_type"] = in_ts_type
    concno325.units = "ug N m-3"
    return concno325


def calc_fine_conctno3(concno3f, vmrhno3):
    return calc_conctno3(concno3f=concno3f, concno3c=None, vmrhno3=vmrhno3)


def calc_conctno3(concno3c, concno3f, vmrhno3):
    if concno3c != None:
        if concno3c.units == "ug m-3" or concno3c.units == "ug/m**3":
            concno3c.units = "ug/m3"
        assert concno3c.units == "ug/m3"

    if vmrhno3.units == "1e-9":
        vmrhno3.units == "ppb"
    assert concno3f.units == "ug/m3"
    assert vmrhno3.units == "ppb"

    in_ts_type = vmrhno3.ts_type
    if concno3c != None:
        concno3 = add_cubes(concno3f.cube, concno3c.cube)
    else:
        concno3 = concno3f.cube

    conchno3 = conc_from_vmr_STP(vmrhno3.cube)
    conchno3.units = "ug/m3"
    concno3 *= M_N / (M_N + M_O * 3)
    conchno3 *= M_N / (M_H + M_N + M_O * 3)
    conctno3 = add_cubes(concno3, conchno3)
    conctno3.attributes["ts_type"] = in_ts_type
    conctno3.units = "ug N m-3"
    return conctno3


def calc_conctnh(concnh4, vmrnh3):
    if concnh4.units == "ug m-3" or concnh4.units == "ug/m**3":
        concnh4.units = "ug/m3"
    if vmrnh3.units == "1e-9":
        vmrnh3.units = "ppb"
    assert concnh4.units == "ug/m3"
    assert vmrnh3.units == "ppb"

    concnh3 = conc_from_vmr_STP(vmrnh3.cube)
    concnh3.units = "ug/m3"
    concnh3 *= M_N / (M_N + M_H * 3)
    in_ts_type = concnh4.ts_type
    concnh4 = concnh4.cube
    concnh4 *= M_N / (M_N + M_H * 4)
    conctnh = add_cubes(concnh3, concnh4)
    conctnh.attributes["ts_type"] = in_ts_type
    conctnh.units = "ug N m-3"
    return conctnh


def calc_aod_from_species_contributions(*gridded_objects):

    data = gridded_objects[0].cube

    assert str(data.units) == "1"

    for obj in gridded_objects[1:]:
        assert str(obj.units) == "1"
        data = add_cubes(data, obj.cube)

    return data


FUNS = {
    "add_cubes": add_cubes,
    "subtract_cubes": subtract_cubes,
    "divide_cubes": divide_cubes,
    "multiply_cubes": multiply_cubes,
    "calc_ae": compute_angstrom_coeff_cubes,
    "calc_ratpm10pm25": calc_ratpm10pm25,
    "calc_conctno3": calc_conctno3,
    "calc_fine_conctno3": calc_fine_conctno3,
    "calc_conctnh": calc_conctnh,
    "calc_concnh3": calc_concnh3,
    "calc_concnh4": calc_concnh4,
    "calc_conchno3": calc_conchno3,
    "calc_concno310": calc_concno310,
    "calc_fine_concno310": calc_fine_concno310,
    "calc_concno325": calc_concno325,
    "calc_aod_from_species_contributions": calc_aod_from_species_contributions,
    "mmr_to_vmr": mmr_to_vmr_cube,
}
