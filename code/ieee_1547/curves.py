import numpy as np
from scipy.interpolate import interp1d


# Voltage levels within Volt/VAr curves may be be evaluated
# For lower/higher voltage levels, any Volt/VAr curve is assumed constant
V_MIN: float = 0.75  # lower voltage boundary, p.u.
V_MAX: float = 1.25  # upper voltage boundary, p.u.


def ieee_1547_voltvar(volt_pu: float, qmax_mvar: float) -> float:
    """
    IEEE volt/VAr curves
    :param volt_pu: voltage magnitude in p.u.
    :param qmax_mvar: reactive power limit
    :return: reactive power injection in MVAr
    """
    assert V_MIN <= volt_pu <= V_MAX, "voltage out of bounds"
    x = np.array([V_MIN, 0.90, 0.92, 1.08, 1.1,  V_MAX])  # voltages p.u.
    y = np.array([1.,      1.,   0.,   0.,  -1.,  -1.])  # react inj p.u.
    y *= qmax_mvar  # reactive power injection curve in MVAr
    funct: interp1d = interp1d(x, y, kind="linear")  # interp1d object
    return funct(volt_pu)
