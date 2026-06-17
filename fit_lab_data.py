"""
Physics lab data: curve fit + uncertainty propagation + residuals plot.

Pipeline:
  1. Load (x, y, y_err)  -- swap in your file/format in load_data()
  2. Pick the fit model by name from models.py  (--model NAME)
  3. Fit with scipy.optimize.curve_fit (sigma=y_err, absolute_sigma=True)
  4. Parameter uncertainties from the covariance matrix
  5. Reduced chi-square goodness-of-fit
  6. Propagate fitted params into derived quantities via `uncertainties`
  7. Plot: errorbar data + best-fit curve, with a residuals subplot below

Models live in models.py (a registry you add to). Data loading is the only
remaining per-experiment edit here, in load_data().
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from uncertainties import ufloat
from uncertainties import unumpy as unp   # vectorised ufloat math, if you need it

from models import MODELS


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
# 2b. THEORETICAL CURVE (optional overlay)
# ----------------------------------------------------------------------------
# Two ways to overlay a theoretical prediction, in order of precedence:
#
#   1. Custom shape  -- write theory_custom() below. Use this ONLY when theory
#      has a DIFFERENT functional form than the chosen model. Return None to skip.
#
#   2. Known parameters -- the common case: theory is the chosen model evaluated
#      at values fixed by theory. Don't edit code; pass them on the command line:
#          python fit_lab_data.py data.csv --theory 9.81 0.0
#      (values are in the same order as the model's parameters.)
#
def theory_custom(x):
    """Return a predicted curve with a different shape than the model, or None."""
    return None                                   # <<< EDIT only for a different shape


def theory_curve(mdl, x, theory_params):
    """Resolve the theory overlay: custom shape > CLI params > none."""
    custom = theory_custom(x)
    if custom is not None:
        return np.asarray(custom)
    if theory_params is not None:
        return mdl.func(x, *theory_params)        # same model, fixed params
    return None


# ----------------------------------------------------------------------------
# 3-5. FIT, PARAMETER ERRORS, REDUCED CHI-SQUARE
# ----------------------------------------------------------------------------
def fit(mdl, x, y, y_err):
    # absolute_sigma=True -> y_err is taken as real 1-sigma errors, so the
    # returned covariance reflects actual measurement uncertainty (not just
    # the relative weighting). This is what you want for physics lab data.
    popt, pcov = curve_fit(mdl.func, x, y, p0=mdl.p0, sigma=y_err,
                           absolute_sigma=True)

    # 1-sigma parameter uncertainties = sqrt of the covariance diagonal.
    perr = np.sqrt(np.diag(pcov))

    # Reduced chi-square: chi2 / dof, where dof = n_points - n_params.
    # ~1 is a good fit; >>1 underfits or underestimated errors; <<1 overestimated errors.
    resid = y - mdl.func(x, *popt)
    chi2 = np.sum((resid / y_err) ** 2)
    dof = len(x) - len(popt)
    chi2_red = chi2 / dof

    return popt, pcov, perr, chi2_red, dof


# ----------------------------------------------------------------------------
# 6. DERIVED PHYSICAL QUANTITIES (uncertainty propagation)
# ----------------------------------------------------------------------------
def derived_quantities(mdl, popt, pcov):
    """
    Wrap the fitted params as correlated ufloats, then let the model's own
    `derived` function do ordinary algebra; `uncertainties` propagates the
    errors (including parameter correlations) for you -- no hand-derived partials.
    Returns {} for models that define no derived quantities.
    """
    if mdl.derived is None:
        return {}
    # correlated_values keeps off-diagonal covariance terms, which matters when
    # a derived quantity mixes parameters (e.g. m and b together).
    from uncertainties import correlated_values
    params = correlated_values(popt, pcov)
    return mdl.derived(params)


# ----------------------------------------------------------------------------
# 7. PLOT: data + best fit, with residuals subplot
# ----------------------------------------------------------------------------
def plot(mdl, x, y, y_err, popt, chi2_red, outpath="fit.png", show=True,
         theory_params=None, theory_label="theory",
         residuals=True, xlabel="x", ylabel="y"):
    xs = np.linspace(x.min(), x.max(), 400)       # smooth curve for plotting
    fit_curve = mdl.func(xs, *popt)
    resid = y - mdl.func(x, *popt)

    # Optional theory overlay. theory_curve() returns None when not requested.
    theory_smooth = theory_curve(mdl, xs, theory_params)  # smooth curve for the main panel
    theory_at_x = theory_curve(mdl, x, theory_params)     # at data points, for residuals

    # Layout: two stacked panels (main + residuals) or a single panel.
    if residuals:
        fig, (ax, axr) = plt.subplots(
            2, 1, sharex=True, figsize=(7, 6),
            gridspec_kw={"height_ratios": [3, 1]},
        )
    else:
        fig, ax = plt.subplots(figsize=(7, 5))
        axr = None

    # --- main panel: data + best-fit curve (+ optional theory) ---
    ax.errorbar(x, y, yerr=y_err, fmt="o", capsize=3, label="data", zorder=2)
    ax.plot(xs, fit_curve, "-", lw=2,
            label=f"fit ($\\chi^2_\\nu$ = {chi2_red:.2f})", zorder=3)
    if theory_smooth is not None:
        ax.plot(xs, theory_smooth, "--", lw=2, color="C2",
                label=theory_label, zorder=1)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.set_title("Fit to lab data")

    # --- residuals panel: data - fit, plus data - theory if available ---
    if residuals:
        axr.axhline(0, color="k", lw=0.8)
        axr.errorbar(x, resid, yerr=y_err, fmt="o", capsize=3, label="data $-$ fit")
        if theory_at_x is not None:
            axr.errorbar(x, y - theory_at_x, yerr=y_err, fmt="s", capsize=3,
                         color="C2", alpha=0.7, label="data $-$ theory")
            axr.legend(fontsize="small")
        axr.set_xlabel(xlabel)
        axr.set_ylabel("residual")
    else:
        # No residuals panel -> the main panel carries the x-axis label.
        ax.set_xlabel(xlabel)

    fig.tight_layout()
    plt.savefig(outpath, dpi=150)
    print(f"\nSaved plot to {outpath}")
    if show:
        plt.show()


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description="Curve-fit physics lab data with uncertainty propagation.")
    # Data file is positional and OPTIONAL: omit it to run on synthetic demo data.
    p.add_argument("data", nargs="?", default=None,
                   help="path to data file (CSV with x,y,y_err columns). "
                        "Omit to use built-in synthetic data.")
    p.add_argument("-m", "--model", default="linear", choices=sorted(MODELS),
                   help="which model from models.py to fit (default: linear)")
    p.add_argument("--list-models", action="store_true",
                   help="list available models and exit")
    p.add_argument("-o", "--out", default="fit.png",
                   help="output image path (default: fit.png)")
    p.add_argument("--no-show", action="store_true",
                   help="save the plot but don't open a window (for batch runs)")
    p.add_argument("--theory", nargs="+", type=float, metavar="VAL", default=None,
                   help="overlay model() evaluated at these parameter values "
                        "(same order as the model's parameters), e.g. --theory 9.81 0.0")
    p.add_argument("--theory-label", default="theory",
                   help="legend label for the theory overlay")
    p.add_argument("--no-residuals", dest="residuals", action="store_false",
                   help="omit the residuals subplot (show only the main panel)")
    p.add_argument("--xlabel", default="x", help="x-axis label (default: x)")
    p.add_argument("--ylabel", default="y", help="y-axis label (default: y)")
    return p.parse_args()


def main():
    args = parse_args()

    if args.list_models:
        print("Available models (--model NAME):")
        for name in sorted(MODELS):
            m = MODELS[name]
            print(f"  {name:14s} {m.description}  [params: {', '.join(m.param_names)}]")
        return

    mdl = MODELS[args.model]
    x, y, y_err = load_data(path=args.data)

    popt, pcov, perr, chi2_red, dof = fit(mdl, x, y, y_err)

    # Report fitted parameters as value +/- error. ufloat's formatting picks
    # sensible significant figures automatically (error to ~2 sig figs).
    print(f"Model: {args.model}  ({mdl.description})")
    print("Fitted parameters:")
    for name, val, err in zip(mdl.param_names, popt, perr):
        print(f"  {name} = {ufloat(val, err):.2uP}")

    print(f"\nReduced chi-square = {chi2_red:.3f}  (dof = {dof})")

    derived = derived_quantities(mdl, popt, pcov)
    if derived:
        print("\nDerived quantities:")
        for label, q in derived.items():
            # ufloats format with .2uP; constants (no fit dependence) are plain
            # floats, so fall back to an ordinary format for those.
            if hasattr(q, "std_dev"):
                print(f"  {label} = {q:.2uP}")
            else:
                print(f"  {label} = {q:.4g}")

    plot(mdl, x, y, y_err, popt, chi2_red, outpath=args.out, show=not args.no_show,
         theory_params=args.theory, theory_label=args.theory_label,
         residuals=args.residuals, xlabel=args.xlabel, ylabel=args.ylabel)


if __name__ == "__main__":
    main()
