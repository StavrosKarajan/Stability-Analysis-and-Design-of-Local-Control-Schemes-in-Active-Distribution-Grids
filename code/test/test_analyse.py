"""
This file contains test functions for 'pytest' in 'make.sh'
"""

from ieee_1547.curves import ieee_1547_voltvar
from cigre_19bus.grid import create_cigre_19bus, PV_ALLOC
from stability.analyse import get_slope_matrix, get_grid_matrix


def test_get_slope_matrix():
    q_max = 42.  # random reactive power injection limit of PV modules
    b_mat = get_slope_matrix(ieee_1547_voltvar, [0], [q_max])
    assert b_mat.shape == (1, 1)
    exact_slope = q_max / (.92 - .9)
    assert abs(b_mat[0, 0] - exact_slope) < exact_slope / 1e3

    fac: float = 3.2  # scale reactive power inj capability -> Scales slope
    b_mat = get_slope_matrix(ieee_1547_voltvar, [0, 1], [q_max, fac * q_max])
    assert b_mat.shape == (2, 2)
    exact_slope = fac * q_max / (.92 - .9)
    assert abs(b_mat[1, 1] - exact_slope) < exact_slope / 1e3


def test_get_grid_matrix():
    net = create_cigre_19bus()
    x = get_grid_matrix(net, PV_ALLOC)
    assert x.shape == (len(PV_ALLOC), len(PV_ALLOC)), "X wrong size"

    # Sensitivity of injection at slack bus is zero
    x = get_grid_matrix(net, [0])  # Node 0 = slack bus
    assert x.shape == (1, 1)
    assert x[0, 0] == 0.
