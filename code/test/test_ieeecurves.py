"""
This file contains test functions for 'pytest' in 'make.sh'
"""

import pytest
from ieee_1547.curves import ieee_1547_voltvar


def test_curve_interp1d():
    """
    Test if the curve given in IEEE1547 are interpolated correctly
    :return:
    """
    Q_MAX = 2.  # Dummy inverter injects up to 2 kVAr
    assert ieee_1547_voltvar(0.85, Q_MAX) == Q_MAX
    assert ieee_1547_voltvar(0.91, Q_MAX) == Q_MAX / 2.
    assert ieee_1547_voltvar(1.00, Q_MAX) == 0
    assert ieee_1547_voltvar(1.09, Q_MAX) == - Q_MAX / 2.
    assert ieee_1547_voltvar(1.11, Q_MAX) == - Q_MAX

    # Test if assertion is thrown for unrealistic voltages
    for vlt_in in [0.7, 1.3]:  # test voltage in p.u. outside of [0.8, 1.2]
        with pytest.raises(AssertionError) as excinfo:
            ieee_1547_voltvar(vlt_in, Q_MAX)
            assert "voltage out of bounds" in str(excinfo.value)
