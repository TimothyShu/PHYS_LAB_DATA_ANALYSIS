"""
Demonstration: what wrong constants / an unmodeled offset do to the fit.

The two_cylinder_potential model has ONE free parameter, the prefactor B; the
geometry (d, a) is fixed and the model has no additive offset term. So if the
real data carries a constant offset, or if the geometry constants are wrong,
the fit cannot absorb it. The symptom is always the same: the reduced
chi-square balloons and the residuals develop systematic STRUCTURE instead of
scattering randomly about zero.

Three columns, same generated data shape:
  (A) correct model + correct constants      -> good fit, flat residuals
  (B) data has a +0.8 V voltmeter zero error  -> model has no offset to absorb it
  (C) model uses the wrong separation d       -> wrong curve shape

Run from this directory:  python misspecification_demo.py
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

D, A, EPS0 = 0.120, 0.005, 8.8542e-12      # true geometry
B0 = 6.0 / np.log((D - A) / A)             # true prefactor (12 V across surfaces)
SIGMA = 0.05                               # multimeter resolution

x = np.arange(0.010, 0.110 + 1e-9, 0.005)
err = np.full_like(x, SIGMA)
rng = np.random.default_rng(42)
V_clean = B0 * (np.log(x / (D - x)) - np.log(A / (D - A)))
noise = rng.normal(0.0, SIGMA, x.size)


def cyl(x, B, d=D, a=A):
    return B * (np.log(x / (d - x)) - np.log(a / (d - a)))


def reduced_chi2(y, yfit):
    return np.sum(((y - yfit) / err) ** 2) / (len(y) - 1)


# --- three scenarios: (title, data, fit-model) ---
y_correct = V_clean + noise
y_offset = V_clean + 0.8 + noise                       # +0.8 V zero error
y_wrongd = y_correct                                   # same data, wrong-d model below

scenarios = [
    ("(A) correct model", y_correct, lambda x, B: cyl(x, B)),
    ("(B) +0.8 V zero offset\n(model has no offset)", y_offset, lambda x, B: cyl(x, B)),
    ("(C) wrong d in model\n(0.15 vs 0.12 m)", y_wrongd, lambda x, B: cyl(x, B, d=0.15)),
]

fig, axes = plt.subplots(2, 3, figsize=(13, 6), sharex=True,
                         gridspec_kw={"height_ratios": [3, 1]})
xs = np.linspace(x.min(), x.max(), 400)

for col, (title, y, fmodel) in enumerate(scenarios):
    popt, _ = curve_fit(fmodel, x, y, p0=[2.0], sigma=err, absolute_sigma=True)
    yfit_pts = fmodel(x, *popt)
    c2 = reduced_chi2(y, yfit_pts)

    top, bot = axes[0, col], axes[1, col]
    top.errorbar(x, y, yerr=err, fmt="o", ms=4, capsize=2, label="data", zorder=2)
    top.plot(xs, fmodel(xs, *popt), "-", lw=2, color="C1", zorder=3,
             label=f"fit (B={popt[0]:.2f})")
    top.set_title(f"{title}\n$\\chi^2_\\nu$ = {c2:.1f}", fontsize=10)
    top.legend(fontsize=8)
    if col == 0:
        top.set_ylabel("potential V (V)")

    bot.axhline(0, color="k", lw=0.8)
    bot.errorbar(x, y - yfit_pts, yerr=err, fmt="o", ms=4, capsize=2, color="C3")
    bot.set_xlabel("position x (m)")
    if col == 0:
        bot.set_ylabel("residual")

fig.suptitle("Effect of wrong constants / unmodeled offset on the fit", fontsize=12)
fig.tight_layout()
fig.savefig("misspecification_demo.png", dpi=150)
print("saved misspecification_demo.png")
for title, y, fmodel in scenarios:
    popt, _ = curve_fit(fmodel, x, y, p0=[2.0], sigma=err, absolute_sigma=True)
    print(f"  {title.splitlines()[0]:24s} B = {popt[0]:.3f},  "
          f"chi2_red = {reduced_chi2(y, fmodel(x, *popt)):.2f}")
