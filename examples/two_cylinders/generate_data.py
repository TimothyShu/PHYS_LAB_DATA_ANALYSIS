"""
Generate synthetic potential-vs-position data for two parallel charged cylinders.

Setup (cylindrical capacitor): two long conducting cylinders, radius a = 10 mm,
axes d = 140 mm apart, length l >> d so end effects are negligible and they
behave as line charges -q and +q (linear density lambda = q/l). Connected across
a 12 V source. A probe measures the on-axis potential V(x), where x = distance
from the left (negative) cylinder's axis (metres), stepped in 5 mm increments.

    V(x) = B * [ ln(x/(d-x)) - ln(a/(d-a)) ],   B = q/(2*pi*eps0*l)

The -ln(a/(d-a)) term sets V = 0 at the left cylinder's surface (x = a). The
prefactor B is fixed by the 12 V across the capacitor:
    12 V = V(d-a) - V(a) = 2*B*ln((d-a)/a)   ->   B = 6 / ln((d-a)/a)

Run from this directory:  python generate_data.py
Writes potential_vs_position.csv with columns x, y, y_err (SI units: m, V, V).
"""
import numpy as np
import pandas as pd

D = 0.140           # m   centre-to-centre separation (140 mm)
A = 0.010           # m   cylinder radius (10 mm) -- must match CYL_RADIUS in models.py
STEP = 0.005        # m   probe step (5 mm)
V_SOURCE = 12.0     # V   source across the capacitor
SIGMA = 0.10        # V   voltmeter precision (1-sigma measurement error)
EPS0 = 8.8542e-12   # F/m

# Prefactor fixed by the 12 V across the cylinder surfaces.
B = (V_SOURCE / 2.0) / np.log((D - A) / A)

# Probe positions on 5 mm steps, kept clear of the cylinders (a .. D-a).
x = np.arange(0.020, 0.120 + 1e-9, STEP)      # 20 mm .. 120 mm
V_true = B * (np.log(x / (D - x)) - np.log(A / (D - A)))

# Add Gaussian measurement noise at the voltmeter precision.
rng = np.random.default_rng(42)               # fixed seed -> reproducible CSV
V_meas = V_true + rng.normal(0.0, SIGMA, size=x.size)
y_err = np.full_like(x, SIGMA)

pd.DataFrame({"x": x, "y": V_meas, "y_err": y_err}).to_csv(
    "potential_vs_position.csv", index=False)

print(f"B_theory = {B:.5f} V   (lambda = q/l = {2 * np.pi * EPS0 * B:.3e} C/m)")
print(f"wrote potential_vs_position.csv with {x.size} points")
