"""
Physics lab data: curve fit + uncertainty propagation + residuals plot.

Pipeline:
  1. Load (x, y, y_err)  -- swap in your file/format in load_data()
  2. Define the fit model -- swap in your function in `model`
  3. Fit with scipy.optimize.curve_fit (sigma=y_err, absolute_sigma=True)
  4. Parameter uncertainties from the covariance matrix
  5. Reduced chi-square goodness-of-fit
  6. Propagate fitted params into derived quantities via `uncertainties`
  7. Plot: errorbar data + best-fit curve, with a residuals subplot below

Swap points are marked with  # <<< EDIT
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from uncertainties import ufloat
from uncertainties import unumpy as unp   # vectorised ufloat math, if you need it


# ----------------------------------------------------------------------------
# 1. LOAD DATA                                                          # <<< EDIT
# ----------------------------------------------------------------------------
def load_data(path=None):
    """
    Return (x, y, y_err) as 1-D numpy arrays.

    Default expects a CSV with a header row and columns named x, y, y_err.
    For a plain whitespace-delimited file, use the np.loadtxt branch instead.
    If `path` is None, generate synthetic data so the script runs as-is.
    """
    if path is None:
        # --- synthetic demo data (delete once you have real data) ---
        rng = np.random.default_rng(0)
        x = np.linspace(0.0, 10.0, 15)
        true_m, true_b = 2.3, 1.1
        y_err = np.full_like(x, 0.5)              # constant 0.5 measurement error
        y = true_m * x + true_b + rng.normal(0.0, y_err)
        return x, y, y_err

    # --- CSV / messy data: use pandas ---
    import pandas as pd
    df = pd.read_csv(path)                        # adjust sep=, skiprows=, etc.
    x = df["x"].to_numpy(float)
    y = df["y"].to_numpy(float)
    y_err = df["y_err"].to_numpy(float)
    return x, y, y_err

    # --- clean numeric text file alternative ---
    # x, y, y_err = np.loadtxt(path, unpack=True, skiprows=1)
    # return x, y, y_err


# ----------------------------------------------------------------------------
# 2. FIT MODEL                                                          # <<< EDIT
# ----------------------------------------------------------------------------
def model(x, m, b):
    """Linear model y = m*x + b. Replace body + signature with your model."""
    return m * x + b


# Human-readable parameter names, in the SAME order as model()'s signature.
PARAM_NAMES = ["m", "b"]                          # <<< EDIT

# Optional initial guess (helps nonlinear fits converge). None = curve_fit default.
P0 = None                                         # e.g. [1.0, 0.0]


# ----------------------------------------------------------------------------
# 3-5. FIT, PARAMETER ERRORS, REDUCED CHI-SQUARE
# ----------------------------------------------------------------------------
def fit(x, y, y_err):
    # absolute_sigma=True -> y_err is taken as real 1-sigma errors, so the
    # returned covariance reflects actual measurement uncertainty (not just
    # the relative weighting). This is what you want for physics lab data.
    popt, pcov = curve_fit(model, x, y, p0=P0, sigma=y_err, absolute_sigma=True)

    # 1-sigma parameter uncertainties = sqrt of the covariance diagonal.
    perr = np.sqrt(np.diag(pcov))

    # Reduced chi-square: chi2 / dof, where dof = n_points - n_params.
    # ~1 is a good fit; >>1 underfits or underestimated errors; <<1 overestimated errors.
    resid = y - model(x, *popt)
    chi2 = np.sum((resid / y_err) ** 2)
    dof = len(x) - len(popt)
    chi2_red = chi2 / dof

    return popt, pcov, perr, chi2_red, dof


# ----------------------------------------------------------------------------
# 6. DERIVED PHYSICAL QUANTITIES (uncertainty propagation)              # <<< EDIT
# ----------------------------------------------------------------------------
def derived_quantities(popt, pcov):
    """
    Wrap the fitted params as correlated ufloats, then do ordinary algebra;
    `uncertainties` propagates the errors (including parameter correlations
    from the full covariance matrix) for you -- no hand-derived partials.
    """
    # correlated_values keeps off-diagonal covariance terms, which matters when
    # your derived quantity mixes parameters (e.g. m and b together).
    from uncertainties import correlated_values
    params = correlated_values(popt, pcov)
    m, b = params                                 # <<< EDIT names to match PARAM_NAMES

    # --- example derived results; replace with your physics ---
    # e.g. an x-intercept x0 = -b/m, or a quantity g = 4*pi^2 / m, etc.
    x_intercept = -b / m
    return {
        "x_intercept = -b/m": x_intercept,
        # "g = 4*pi^2 / slope": 4 * np.pi**2 / m,
    }


# ----------------------------------------------------------------------------
# 7. PLOT: data + best fit, with residuals subplot
# ----------------------------------------------------------------------------
def plot(x, y, y_err, popt, chi2_red):
    xs = np.linspace(x.min(), x.max(), 400)       # smooth curve for plotting
    fit_curve = model(xs, *popt)
    resid = y - model(x, *popt)

    fig, (ax, axr) = plt.subplots(
        2, 1, sharex=True, figsize=(7, 6),
        gridspec_kw={"height_ratios": [3, 1]},
    )

    # --- main panel: data + best-fit curve ---
    ax.errorbar(x, y, yerr=y_err, fmt="o", capsize=3, label="data", zorder=2)
    ax.plot(xs, fit_curve, "-", lw=2,
            label=f"fit ($\\chi^2_\\nu$ = {chi2_red:.2f})", zorder=3)
    ax.set_ylabel("y")
    ax.legend()
    ax.set_title("Fit to lab data")

    # --- residuals panel ---
    axr.axhline(0, color="k", lw=0.8)
    axr.errorbar(x, resid, yerr=y_err, fmt="o", capsize=3)
    axr.set_xlabel("x")
    axr.set_ylabel("residual")

    fig.tight_layout()
    plt.savefig("fit.png", dpi=150)               # comment out if you only want plt.show()
    plt.show()


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    x, y, y_err = load_data(path=None)            # <<< pass your file path here

    popt, pcov, perr, chi2_red, dof = fit(x, y, y_err)

    # Report fitted parameters as value +/- error. ufloat's formatting picks
    # sensible significant figures automatically (error to ~2 sig figs).
    print("Fitted parameters:")
    for name, val, err in zip(PARAM_NAMES, popt, perr):
        print(f"  {name} = {ufloat(val, err):.2uP}")

    print(f"\nReduced chi-square = {chi2_red:.3f}  (dof = {dof})")

    print("\nDerived quantities:")
    for label, q in derived_quantities(popt, pcov).items():
        print(f"  {label} = {q:.2uP}")

    plot(x, y, y_err, popt, chi2_red)


if __name__ == "__main__":
    main()
