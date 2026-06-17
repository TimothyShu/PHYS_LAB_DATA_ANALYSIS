"""
Model library for fit_lab_data.py.

Each model is one entry in the MODELS registry. To add a model, define its
function (signature `f(x, *params)`) and register it with MODELS.register(...).
Old models stay here forever -- you select which one to use at runtime with
    python fit_lab_data.py data.csv --model exponential
and never have to delete or overwrite a working model to try a new one.

A registered model bundles the things that must stay consistent:
  - func         : the callable curve_fit will fit, f(x, *params)
  - param_names  : names in the SAME order as func's parameters (for printing)
  - p0           : optional initial guess (helps nonlinear fits converge)
  - derived      : optional fn(params) -> {label: ufloat} for derived quantities,
                   where `params` are correlated ufloats (errors auto-propagated)
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

import numpy as np


@dataclass
class Model:
    func: Callable
    param_names: Sequence[str]
    p0: Optional[Sequence[float]] = None
    derived: Optional[Callable] = None            # fn(correlated_params) -> dict
    description: str = ""


class _Registry(dict):
    """A dict of name -> Model with a small decorator helper for registration."""
    def register(self, name, **kwargs):
        self[name] = Model(**kwargs)
        return self[name]


MODELS = _Registry()


# ----------------------------------------------------------------------------
# Built-in models. Add your own below -- they accumulate, nothing is lost.
# ----------------------------------------------------------------------------

# --- linear: y = m*x + b ---
def _linear(x, m, b):
    return m * x + b

def _linear_derived(params):
    m, b = params
    return {"x_intercept = -b/m": -b / m}

MODELS.register(
    "linear",
    func=_linear,
    param_names=["m", "b"],
    derived=_linear_derived,
    description="straight line y = m*x + b",
)


# --- proportional: y = m*x (through the origin) ---
def _proportional(x, m):
    return m * x

MODELS.register(
    "proportional",
    func=_proportional,
    param_names=["m"],
    description="line through the origin y = m*x",
)


# --- exponential decay: y = A * exp(-x / tau) ---
def _exp_decay(x, A, tau):
    return A * np.exp(-x / tau)

def _exp_decay_derived(params):
    A, tau = params
    return {
        "half-life = tau*ln2": tau * np.log(2),
        "decay rate = 1/tau": 1.0 / tau,
    }

MODELS.register(
    "exponential",
    func=_exp_decay,
    param_names=["A", "tau"],
    p0=[1.0, 1.0],                                # exp fits usually need a guess
    derived=_exp_decay_derived,
    description="exponential decay y = A*exp(-x/tau)",
)


# --- gaussian: y = A * exp(-(x - mu)^2 / (2 sigma^2)) ---
def _gaussian(x, A, mu, sigma):
    return A * np.exp(-((x - mu) ** 2) / (2.0 * sigma ** 2))

def _gaussian_derived(params):
    A, mu, sigma = params
    return {"FWHM = 2.3548*sigma": 2.0 * np.sqrt(2.0 * np.log(2.0)) * sigma}

MODELS.register(
    "gaussian",
    func=_gaussian,
    param_names=["A", "mu", "sigma"],
    p0=[1.0, 0.0, 1.0],
    derived=_gaussian_derived,
    description="gaussian peak y = A*exp(-(x-mu)^2 / 2 sigma^2)",
)


# --- TEMPLATE: copy this block to add your own model -------------------------
# def _my_model(x, a, b, c):
#     return a * x**2 + b * x + c
#
# MODELS.register(
#     "my_model",
#     func=_my_model,
#     param_names=["a", "b", "c"],
#     p0=[1.0, 1.0, 1.0],
#     derived=lambda p: {"vertex_x = -b/2a": -p[1] / (2 * p[0])},
#     description="quadratic a*x^2 + b*x + c",
# )
