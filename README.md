# PHYS_LAB_DATA_ANALYSIS

Curve-fit physics lab data with proper uncertainty handling, then plot the fit
and residuals. Built around `scipy.optimize.curve_fit` with real measurement
errors (`sigma`, `absolute_sigma=True`), reduced chi-square goodness-of-fit, and
automatic error propagation into derived quantities via the `uncertainties`
package — no hand-derived partial derivatives.

## Features

- Fit any model from a **selectable registry** (`models.py`) — pick at runtime with `--model`, no code edits to switch.
- Parameter uncertainties from the covariance matrix, reported as `value ± error` with sensible significant figures.
- **Reduced chi-square** printed and shown on the plot as a goodness-of-fit check.
- **Derived quantities** with correlated error propagation (e.g. half-life from a fitted time constant).
- Plot: data with error bars + best-fit curve, plus a **residuals subplot** below.
- Optional **theoretical-curve overlay** (`--theory`), drawn on both the main and residuals panels.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then either activate the environment (`source .venv/bin/activate`) and use
`python`, or call `.venv/bin/python` directly.

## Usage

```bash
# list available models
python fit_lab_data.py --list-models

# run on the built-in synthetic demo data (no file needed)
python fit_lab_data.py

# fit your own data with a chosen model
python fit_lab_data.py data.csv --model exponential

# save the plot to a custom path, don't open a window (batch mode)
python fit_lab_data.py data.csv -o run3.png --no-show

# overlay a theoretical prediction (model evaluated at known parameter values)
python fit_lab_data.py data.csv --model exponential --theory 5.0 2.3 --theory-label "theory τ=2.3"
```

### Command-line options

| Option | Description |
|--------|-------------|
| `data` | Path to a CSV with `x,y,y_err` columns. Omit to use synthetic demo data. |
| `-m`, `--model NAME` | Model to fit (default: `linear`). See `--list-models`. |
| `--list-models` | List available models and exit. |
| `-o`, `--out PATH` | Output image path (default: `fit.png`). |
| `--no-show` | Save the plot but don't open a window. |
| `--theory VAL...` | Overlay the model evaluated at these parameter values (same order as the model's parameters). |
| `--theory-label` | Legend label for the theory overlay. |

## Input data format

A CSV with a header row and columns `x`, `y`, `y_err` (the 1σ uncertainty on
each `y`). For other formats, edit `load_data()` in `fit_lab_data.py` — there's
a commented `np.loadtxt` branch for plain whitespace-delimited text files.

## Adding your own model

Models live in `models.py` as entries in the `MODELS` registry. Adding one never
overwrites existing models — you accumulate a library and select among them with
`--model`. Each entry bundles everything that must stay consistent:

```python
def _my_model(x, a, b, c):
    return a * x**2 + b * x + c

MODELS.register(
    "quadratic",
    func=_my_model,
    param_names=["a", "b", "c"],   # same order as the function signature
    p0=[1.0, 1.0, 1.0],            # optional initial guess (helps nonlinear fits)
    derived=lambda p: {"vertex_x = -b/2a": -p[1] / (2 * p[0])},
    description="quadratic a*x^2 + b*x + c",
)
```

The `derived` function receives the fitted parameters as **correlated** ufloats,
so any algebra you do on them propagates errors automatically (including
parameter correlations). Return `{}` or omit `derived` if there's nothing to
report.

Built-in models: `linear`, `proportional`, `exponential`, `gaussian`.

## Interpreting reduced chi-square

| χ²ᵥ | Meaning |
|-----|---------|
| ≈ 1 | Good fit; model and error bars are consistent |
| ≫ 1 | Poor fit, or `y_err` underestimated |
| ≪ 1 | `y_err` overestimated (or too many free parameters) |

This is only meaningful because the fit uses real `y_err` with
`absolute_sigma=True`. Also check the residuals panel for structure — a trend
there means the model shape is wrong even if χ²ᵥ looks fine.

## Caveat: uncertainty in x

`curve_fit` assumes the `x` values are exact. If your independent variable also
carries measurement error, this tool will report over-optimistic parameter
uncertainties; that case needs orthogonal distance regression (`scipy.odr`)
instead, which isn't wired in yet.
