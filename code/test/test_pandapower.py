"""
This file contains test functions for 'pytest' in 'make.sh'
"""

import pytest
import numpy as np
from cigre_19bus import grid


# def test_pandapow_install():
#     """
#     Verify if pandapower is correctly installed
#     This test takes up to a few minutes to complete
#     :return:
#     """
#     import pandapower as pp
#     pp.test.run_all_tests()  # official tests provided by pandapower


def test_flat_vltg():
    """
    Simulate the CIGRE grid without any load power flow
    The voltages of all nodes should stay at 1.0 p.u.
    :return:
    """
    net = grid.create_cigre_19bus()
    vm_pu = grid.set_power_inject(net,
                                  q_bus=np.zeros(19),
                                  p_bus=np.zeros(19))
    # assert if voltage deviates from 1.0 p.u. for all nodes
    assert np.max(np.abs(vm_pu - np.ones(19))) < 1e-4

    # TODO: Test every assertion in the code for full test coverage
    # Test assertion if wrong vector length for reactive power injection
    with pytest.raises(AssertionError) as excinfo:
        number_of_nodes = 13  # something other than 19
        grid.set_power_inject(net, q_bus=np.zeros(number_of_nodes))
        assert "vector invalid length" in str(excinfo.value)
    return
