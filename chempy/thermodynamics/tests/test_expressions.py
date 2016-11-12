# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import math

from chempy.util._expr import Expr
from chempy.util.testing import requires
from chempy.units import allclose, units_library, Backend, default_units as du, default_constants as dc

from ..expressions import GibbsEqConst


def test_GibbsEqConst():
    R, T = 8.314, 298.15
    dH, dS = -4e3, 16
    gee = GibbsEqConst([dH/R, dS/R])
    ref = math.exp(-(dH - T*dS)/(R*T))
    assert abs((gee({'temperature': T}) - ref)/ref) < 1e-14

    dCp = 123.45
    Tref = 242
    gee2 = GibbsEqConst([dH/R, dS/R, dCp/R, Tref])
    dH2 = dH + dCp*(T - Tref)
    dS2 = dS + dCp*math.log(T/Tref)
    ref2 = math.exp(-(dH2 - T*dS2)/(R*T))
    assert abs((gee2({'temperature': T}) - ref2)/ref2) < 1e-14


def test_GibbsEqConst__unique_keys():
    R, T = 8.314, 298.15
    dH, dS = -4e3, 16
    gee = GibbsEqConst(unique_keys=('dH1', 'dS1'))
    ref = math.exp(-(dH - T*dS)/(R*T))
    assert abs((gee({'temperature': T, 'dH1': dH/R, 'dS1': dS/R}) - ref)/ref) < 1e-14


@requires('sympy')
def test_GibbsEqConst__latex():
    import sympy
    DH, DS, R, T = sympy.symbols('\Delta\ H \Delta\ S R T')
    gee = GibbsEqConst([DH/R, DS/R])
    res = gee({'temperature': T}, backend=sympy)
    ref = sympy.exp(-(DH - T*DS)/(R*T))
    assert (res - ref).simplify() == 0


@requires(units_library)
def test_GibbsEqConst__units():
    R, T = dc.molar_gas_constant, 298.15*du.K
    DH = -4e3 * du.J/du.mol
    DS = 16 * du.J/du.K/du.mol
    be = Backend()
    gee = GibbsEqConst([DH/R, DS/R])
    res = gee({'temperature': T}, backend=be)
    ref = be.exp(-(DH - T*DS)/(R*T))
    assert allclose(res, ref)


@requires(units_library)
def test_GibbsEqConst__nested():

    class TExpr(Expr):
        argument_names = ('heat_capacity',)
        parameter_keys = ('energy',)

        def __call__(self, variables, backend=None):
            heat_capacity, = self.all_args(variables, backend=backend)
            energy, = self.all_params(variables, backend=backend)
            return energy/heat_capacity

    R = 8.314 * du.J/du.K/du.mol
    T = TExpr([10.0 * du.J/du.K])
    dH, dS = -4e3 * du.J/du.mol, 16 * du.J/du.K/du.mol
    gee = GibbsEqConst([dH/R, dS/R])
    be = Backend()
    Tref = 298.15 * du.K
    ref = be.exp(-(dH - Tref*dS)/(R*Tref))
    assert be.abs((gee({'energy': 2981.5 * du.J, 'temperature': T}, backend=be) - ref)/ref) < 1e-14
