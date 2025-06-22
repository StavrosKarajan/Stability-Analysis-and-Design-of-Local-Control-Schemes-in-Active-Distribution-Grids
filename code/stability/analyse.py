from ieee_1547.curves import V_MIN, V_MAX
from cigre_19bus.grid import set_power_inject
import typing
import numpy as np
import pandapower as pp


def get_slope_matrix(volt_var_curve: typing.Callable[[float, float], float],
                     pv_alloc: np.array,
                     q_max: np.ndarray) -> np.ndarray:
    """
    The slope matrix 'b_mat' contains the steepnes of all volt/VAr curves
    in its diagonal.
    :param volt_var_curve: function mapping from (same for all PV modules)
    :param pv_alloc: node index of all PV module location
    :param q_max: reactive power injection limit of all PV modules, MVAr
    :return: Slope matrix, entries in (MVAr / p.u.)
    """
    # Sanity checks
    assert len(pv_alloc) == len(q_max), "Wrong vector lengths"

    # Numerically find steepest section within the (normalised) Volt/VAr
    # curves. IEEE 1547 uses the same shape of the Volt/VAr curve, which
    # is then multiplied by the individual 'q_max' for every PV module
    delta_vlt = (V_MAX - V_MIN) / 1000  # distance between two entries
    vlt_vec = np.arange(V_MIN, V_MAX, delta_vlt)  # 1000 voltage points
    slope_matrix = np.zeros((len(pv_alloc), len(pv_alloc)))

    # find max slope for every PV module
    for n_idx, _ in enumerate(pv_alloc):

        # sample Volt/VAr curve
        q_inj_vec = np.nan * np.ones_like(vlt_vec)  # reactive power inj,
        for v_idx, vlt in enumerate(vlt_vec):
            q_inj_vec[v_idx] = volt_var_curve(vlt, q_max[n_idx])

        # Compute maximum slope between sampling values
        delta_q_inj = np.diff(q_inj_vec)
        assert (delta_q_inj <= 0).all(), "Volt/VAr non-monotonicly decreasing"
        delta_q_inj = np.abs(delta_q_inj)
        slope = np.max(delta_q_inj / delta_vlt)
        slope_matrix[n_idx, n_idx] = slope  # fill diagonal entries

    return slope_matrix


def get_grid_matrix(net: pp.auxiliary.pandapowerNet, pv_alloc) -> np.ndarray:
    """
    Compute grid sensitivity matrix 'X'. Entries in X correspond to the
    sensitivity from reactive power injection (MVAr) to voltage magnitude (p.u)
    :param net: existing network
    :param pv_alloc: node index of all PV module location
    :return: grid matrix
    """
    node_cnt: int = len(net.bus)  # Number of nodes in network
    assert len(pv_alloc) <= node_cnt, "more PV modules than normal loads"

    # Numerically disturb the network by a small reactive power injection
    # around a nominal steady state operating point of 0 MVAr
    dist: float = 1.e-3  # size of disturbance in MVAr
    x_matrix = np.nan * np.ones((len(pv_alloc), len(pv_alloc)))
    for sidx, sender in enumerate(pv_alloc):
        for ridx, receiver in enumerate(pv_alloc):
            q_inj_mvar = np.zeros(node_cnt)
            q_inj_mvar[sender] = dist
            vlt_pu = set_power_inject(net, q_inj_mvar)  # simulate network
            vlt_pu -= 1.  # subtract steady state voltage
            x_matrix[ridx, sidx] = vlt_pu[receiver] / dist
    return x_matrix


def find_lambda(grid_mat: np.ndarray, slope_mat: np.ndarray) -> float:
    """
    Find low pass filter parameter lambda, such that closed loop is
    on the edge of stability
    :param grid_mat: matrix X, sensitivity q -> v
    :param slope_mat: matrix B, slope of Volt/VAr curves
    :return: lambda max
    """
    x = grid_mat
    b = slope_mat
    assert x.shape == b.shape, "X and B must be square"
    assert (x > 0).all(), "All entries in X must be > 0"
    assert (b >= 0).all(), "All entries in B must be >= 0"
    lambda_i, _ = np.linalg.eig(np.matmul(b, x))
    assert np.min(lambda_i) > 0, "invalid eigenvalues"
    assert (np.imag(lambda_i) == 0).all(), "Threephase network not implemented"

    if np.max(lambda_i) < 1.0:
        # lambda = 1.0 would already be stable. No need for additional low pass
        return 1.0
    else:
        # The result below holds for balanced networks only
        # For three phase system the values in lambda_i may be complex numbers.
        # A binary search of lambda_max over the interval [0, 1] quickly
        # yields a suitable lambda_max such that the complex expression
        # || (1-lambda_max)*eye - lambda_max*B^.5*X*B^.5 || <= 1
        return 2 / (1 + np.max(lambda_i))
