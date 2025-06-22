from cigre_19bus import grid
from ieee_1547.curves import ieee_1547_voltvar
from stability.analyse import get_slope_matrix, get_grid_matrix, find_lambda
import numpy as np
from matplotlib import pyplot as plt
from os import path, getcwd

"""
Plot IEEE 1547 volt/VAr curve used to show instability
"""


def plot_voltvar_cuves():
    """
    Plot IEEE1547 curves
    :return: Save resulting plot to .../results/IEEE_1547.pdf
    """
    vltg: np.ndarray = np.arange(0.85, 1.15, 0.01)
    qinj: np.ndarray = np.zeros_like(vltg)
    q_max: float = 1.
    for i, v in enumerate(vltg):
        qinj[i] = ieee_1547_voltvar(v, q_max)
    plt.plot(vltg, qinj)
    plt.xticks([0.9, 1.0, 1.1])
    plt.xlabel(r"$v_h$ (p.u.)")
    plt.yticks([-1, 0, 1])
    plt.ylabel(r"$\frac{q_h}{q_h^\mathrm{max}}$ (p.u.)")
    plt.title("IEEE 1547 volt/VAr curves")
    plt.grid()
    plt.tight_layout()
    assert getcwd().endswith("code"), "script run from wrong path"
    plt.savefig(path.join("..", "results", "IEEE_1547.pdf"))


print("Plotting IEEE 1547 Volt/Var curves...")
plot_voltvar_cuves()
print("Plot saved to ../results/IEEE_1547.pdf \n")

"""
Stability analysis

By computing matrices b_mat and X, the stability of IEEE 1547 standard
(for lambda = 1) is investigated.
"""
# Create CIGRE benchmark grid
print("Generating CIGRE 19 bus benchmark grid...")
net = grid.create_cigre_19bus()
NODE_CNT: int = len(net.bus)  # Number of nodes in network
assert NODE_CNT == 19
P_PV_MAX = 50.e-3  # Active power injection limit of PV modules
Q_PV_MAX = 41.5e-3  # Reactive power injection limit of PV modules

# Assess closed loop stability analysis
print("Initialising stability analysis...")
b_mat = get_slope_matrix(ieee_1547_voltvar,
                         grid.PV_ALLOC,
                         Q_PV_MAX * np.ones(4))
x_mat = get_grid_matrix(net, grid.PV_ALLOC)
lambda_max = find_lambda(x_mat, b_mat)
if lambda_max >= 1:
    print("Closed loop is always stable")
else:
    print("lambda_max = " + str(lambda_max) + " < 1.0")
    print("=> Closed loop unstable for some operating points")
print("Stability analysis complete.\n")


"""
Demonstrate instability for one example operating point

Closed loop dynamic is simulated over a few time steps
The reactive power injection of PV modules is updated in every iteration
All other power injections are kept constant
"""

# Find some unstable operating point using educated trial and error
# Both 'q_inject_ss' and 'p_inject_ss' are steady state
# But reactive power of pv modules 'q_pv_mvar' is updated in every time step
q_inject_ss = -39.e-3 * np.ones(NODE_CNT)  # Reactive power injection in MVAr
p_inject_ss = - 12.e-3 * np.ones(NODE_CNT)  # Active power dissipation in MW
p_inject_ss[-3:] = 18.e-3  # Some active power injection at end of branch
p_inject_ss[grid.PV_ALLOC] += P_PV_MAX / 2
p_inject_ss[-4] = 12.9e-3

duration: int = 10  # Number of time steps to be simulated
q_pv_mvar = np.nan * np.ones((4, duration))  # PV module setpoint over time
q_pv_setp = np.zeros(NODE_CNT)  # react power setpoint from previous iteration
q_pv_setp[grid.PV_ALLOC] = [-39.e-3, 29.7e-3, 6.6e-3, -24.3e-3]  # random init
v_pv_pu = np.nan * np.ones((4, duration))  # PV module voltage over time

# Simulate closed loop system for a few time steps
print("Starting closed loop simulations...")
for time in range(duration):

    # Simulate voltage magnitude for given power flow
    v_pu = grid.set_power_inject(net, q_inject_ss + q_pv_setp, p_inject_ss)

    # Save reactive power setpoint and voltage magnitudes for plot
    q_pv_mvar[:, time] = q_pv_setp[grid.PV_ALLOC]
    v_pv_pu[:, time] = v_pu[grid.PV_ALLOC]

    # Update reactive power setpoint of PV modules
    for pv_nd in grid.PV_ALLOC:
        q_pv_setp[pv_nd] = ieee_1547_voltvar(v_pu[pv_nd], Q_PV_MAX)


def plot_q_pv(q_pv_mvar: np.ndarray, q_pv_max: float, pv_alloc: list):
    """
    Plot reactive power injection of PV modules
    :param q_pv_mvar: PV injection of all nodes over time
    :param q_pv_max: PV module reactive power limit
    :param pv_alloc: List of nodes with PV injection
    :return: Save resulting plot to .../results/IEEE_1547.pdf
    """
    plt.cla()  # clear any existing plots
    plt.imshow(q_pv_mvar/q_pv_max, vmin=-1, vmax=1)
    plt.yticks(range(len(pv_alloc)))
    plt.ylim(-.5, 3.5)
    plt.ylabel(r"Node $h \in N$")
    plt.xlabel(r"Time $t$")
    cbar = plt.colorbar(ticks=[-1, 0, 1])
    cbar.set_label(r"Reactive power injection "
                   r"$\frac{q_h}{q_h^\mathrm{max}}$")
    plt.tight_layout()
    assert getcwd().endswith("code"), "script run from wrong path"
    plt.savefig(path.join("..", "results", "Q_PV_inject.pdf"))


print("Closed loop simulated, plotting results...")
plot_q_pv(q_pv_mvar, Q_PV_MAX, grid.PV_ALLOC)
print("Done - Result files will appear in the timeline.")
