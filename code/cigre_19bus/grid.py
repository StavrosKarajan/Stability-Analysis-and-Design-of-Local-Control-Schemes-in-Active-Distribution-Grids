import pandapower as pp
from pandapower import create_transformer_from_parameters as make_trafo
from pandapower import create_line_from_parameters as make_line
from enum import Enum, auto
import numpy as np
from copy import deepcopy


# Constants declared for this demo topology
PV_ALLOC = np.array([12, 16, 17, 19]) - 1  # index of nodes with PV injection


def create_cigre_19bus() -> pp.auxiliary.pandapowerNet:
    """
    Reconstruct CIGRE 19 bus benchmark grid
    for a typical european distribution grid
    in single phase representation
    :return: pp net object
    """

    # create empty net
    net = pp.create_empty_network(f_hz=50.0)

    # create buses
    b0 = pp.create_bus(net, vn_kv=20., name="Node 0")
    b1 = pp.create_bus(net, vn_kv=0.4, name="Node 1")
    b2 = pp.create_bus(net, vn_kv=0.4, name="Node 2")
    b3 = pp.create_bus(net, vn_kv=0.4, name="Node 3")
    b4 = pp.create_bus(net, vn_kv=0.4, name="Node 4")
    b5 = pp.create_bus(net, vn_kv=0.4, name="Node 5")
    b6 = pp.create_bus(net, vn_kv=0.4, name="Node 6")
    b7 = pp.create_bus(net, vn_kv=0.4, name="Node 7")
    b8 = pp.create_bus(net, vn_kv=0.4, name="Node 8")
    b9 = pp.create_bus(net, vn_kv=0.4, name="Node 9")
    b10 = pp.create_bus(net, vn_kv=0.4, name="Node 10")
    b11 = pp.create_bus(net, vn_kv=0.4, name="Node 11")
    b12 = pp.create_bus(net, vn_kv=0.4, name="Node 12")
    b13 = pp.create_bus(net, vn_kv=0.4, name="Node 13")
    b14 = pp.create_bus(net, vn_kv=0.4, name="Node 14")
    b15 = pp.create_bus(net, vn_kv=0.4, name="Node 15")
    b16 = pp.create_bus(net, vn_kv=0.4, name="Node 16")
    b17 = pp.create_bus(net, vn_kv=0.4, name="Node 17")
    b18 = pp.create_bus(net, vn_kv=0.4, name="Node 18")

    # slack bus
    pp.create_ext_grid(net, bus=b0, vm_pu=1.0, name="Grid Connection")

    # create transformer
    hv_bus: int = b0  # high voltage bus
    lv_bus: int = b1  # low voltage bus
    sn_mva: float = 0.500  # rated power in MVA
    vn_hv_kv: float = 20.  # rated voltage on high voltage side in kV
    vn_lv_kv: float = 0.4  # rated voltage on low voltage side in kV
    z_lv: complex = complex(0.0032, 0.0128)  # trafo impedance, v2 side, Ohm
    i_rated: float = sn_mva / vn_lv_kv  # rated current, lv side, kA
    v_sh_lv: complex = z_lv * i_rated  # short circuit voltage at i_rate, kV
    vkr_percent: float = v_sh_lv.real / vn_lv_kv * 100  # real part of v_sh_lv
    vk_percent: float = abs(v_sh_lv) / vn_lv_kv * 100  # rel short circuit vlt
    pfe_kw: float = 0.  # TODO: iron losses in kW, not specified in Cigre???
    i0_percent: float = 0.  # TODO: open loop losses in % of rated current?
    make_trafo(net, hv_bus, lv_bus, sn_mva, vn_hv_kv, vn_lv_kv,
               vkr_percent, vk_percent, pfe_kw, pfe_kw, i0_percent,
               tap_phase_shifter=False, in_service=True, name="Trafo")

    # add all branches
    add_branch(net, CableType.UG1, 35e-3, b1, b2)
    add_branch(net, CableType.UG1, 35e-3, b2, b3)
    add_branch(net, CableType.UG1, 35e-3, b3, b4)
    add_branch(net, CableType.UG1, 35e-3, b4, b5)
    add_branch(net, CableType.UG1, 35e-3, b5, b6)
    add_branch(net, CableType.UG1, 35e-3, b6, b7)
    add_branch(net, CableType.UG1, 35e-3, b7, b8)
    add_branch(net, CableType.UG1, 35e-3, b8, b9)
    add_branch(net, CableType.UG1, 35e-3, b9, b10)
    add_branch(net, CableType.UG3, 30e-3, b3, b11)
    add_branch(net, CableType.UG3, 35e-3, b4, b12)
    add_branch(net, CableType.UG3, 35e-3, b12, b13)
    add_branch(net, CableType.UG3, 35e-3, b13, b14)
    add_branch(net, CableType.UG3, 30e-3, b14, b15)
    add_branch(net, CableType.UG3, 30e-3, b6, b16)
    add_branch(net, CableType.UG3, 30e-3, b9, b17)
    add_branch(net, CableType.UG3, 30e-3, b10, b18)

    return net


def set_power_inject(net: pp.auxiliary.pandapowerNet,
                     q_bus: np.ndarray,
                     p_bus: np.ndarray = None) -> np.ndarray:
    """
    For a given power injection, calculate resulting steady state voltage
    :param net: existing net
    :param q_bus: reactive power injection for every bus, MVAr
    :param p_bus: active power injection for every bus, MW
    :return: voltage magnitude in p.u.
    """
    # sanity checks
    assert len(net.bus) == len(q_bus), "Reactive power vector invalid length"
    if p_bus is not None:
        assert len(net.bus) == len(p_bus), "Active power vector invalid length"

    # copy net, in order not to make the loads added below permanent
    net = deepcopy(net)

    # set power flow for every bus
    for bus, q_mvar in enumerate(q_bus):
        if p_bus is not None:
            p_mw: float = p_bus[bus]
        else:
            p_mw: float = 0
        # power injection is modelled as negative load power
        pp.create_load(net, bus=bus, p_mw=-p_mw, q_mvar=-q_mvar)

    # simulate grid, return voltage magnitude
    pp.runpp(net, numba=False, max_iteration=100)
    return net.res_bus.vm_pu


class CableType(Enum):
    """
    The benchmark grid is made up of three different cable types
    http://kmiwire.com/products/lv-power-cables/aluminium-cables/1069-na2xy-sni-iec.html
    """
    UG1 = auto()  # NA2XY 4 x 240 mm2
    UG2 = auto()  # NA2XY 4 x 150 mm2
    UG3 = auto()  # NA2XY 4 x  50 mm2


def add_branch(net: pp.auxiliary.pandapowerNet,
               cable: CableType,
               length_km: float,
               from_bus: np.int64,
               to_bus: np.int64) -> None:
    """
    Add a line/cable/branch to the existing net
    :param net: existing net
    :param cable: cable type
    :param length_km: cable length in km
    :param from_bus: bus from
    :param to_bus: bus to
    :return: None
    """
    c_nf_per_km = 0.  # neglect parasitic capacitance

    assert cable in list(CableType), "Invalid cable type"
    if cable == CableType.UG1:
        r_ohm_per_km = 0.162  # resistance of NA2XY 4 x 240 mm2, ohms/km
        x_ohm_per_km = 0.0823  # inductance, Ohm/km, 2*pi*f*L
        max_i_ka = 0.454  # max current carrying capacity, kA
    elif cable == CableType.UG2:
        r_ohm_per_km = 0.455  # resistance of NA2XY 4 x 150 mm2, ohms/km
        x_ohm_per_km = 0.2044  # inductance, Ohm/km
        max_i_ka = 0.344  # max current carrying capacity, kA
    elif cable == CableType.UG3:
        r_ohm_per_km = 0.822  # resistance of NA2XY 4 x 50 mm2, ohms/km
        x_ohm_per_km = 0.0847  # inductance, Ohm/km
        max_i_ka = 0.183  # max current carrying capacity, kA
    else:
        NotImplementedError("Unknown cable type:" + str(cable))

    # add line to 'net'
    make_line(net, from_bus, to_bus, length_km, r_ohm_per_km, x_ohm_per_km,
              c_nf_per_km, max_i_ka, name=None)
    return
