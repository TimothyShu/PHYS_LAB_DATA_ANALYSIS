"""
Synthetic data for a coaxial cylindrical capacitor (one cylinder inside another).

Setup: an inner conductor of radius a = 15 mm inside an outer cylindrical shell
of radius b = 110 mm, length l >> b so end effects are negligible. Charge +/-q
per length, across a 12 V source. A probe measures the radial potential V(p),
where p = distance from the INNER surface (p = 0 at r = a, so r = p + a),
stepped in 5 mm. The span runs from the inner surface (p = 0) to the outer
surface (p = b - a = 110 - 15 = 95 mm), so the potential goes 0 V -> 12 V.

    V(p) = B * ln((p + a) / a),   B = q/(2*pi*eps0*l) = lambda/(2*pi*eps0)
    B = V_source / ln(b/a)        (fixed by 12 V across the gap)

Run from this directory:  python generate_data.py
Writes potential_vs_position.csv with columns x, y, y_err (SI units: m, V, V).
Note: the 'x' column is the zeroed radial position p (0 .. 0.095 m).
"""
import numpy as np
import pandas as pd

A = 0.015           # m   inner conductor radius (15 mm)  -- match COAX_INNER in models.py
B_OUTER = 0.110     # m   outer shell radius (110 mm)     -- match COAX_OUTER in models.py
STEP = 0.005        # m   probe step (5 mm)
V_SOURCE = 12.0     # V   source across the capacitor
SIGMA = 0.10        # V   voltmeter precision (1-sigma measurement error)
EPS0 = 8.8542e-12   # F/m

B = V_SOURCE / np.log(B_OUTER / A)

# Zeroed radial positions, inner surface (p=0) to outer surface (p = b - a).
p = np.arange(0.0, (B_OUTER - A) + 1e-9, STEP)      # 0 mm .. 95 mm
V_true = B * np.log((p + A) / A)

rng = np.random.default_rng(42)                      # fixed seed -> reproducible CSV
V_meas = V_true + rng.normal(0.0, SIGMA, size=p.size)
y_err = np.full_like(p, SIGMA)

pd.DataFrame({"x": p, "y": V_meas, "y_err": y_err}).to_csv(
    "potential_vs_position.csv", index=False)

print(f"B_theory = {B:.5f} V   (lambda = q/l = {2 * np.pi * EPS0 * B:.3e} C/m)")
print(f"p spans 0 .. {p[-1] * 1000:.0f} mm ; wrote {p.size} points")
