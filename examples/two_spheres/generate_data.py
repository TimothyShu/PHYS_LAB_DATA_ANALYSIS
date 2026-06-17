"""
Generate synthetic potential-vs-position data for two charged spheres.

Setup: two small spheres, centres D = 140 mm apart, connected across a 12 V
source so they sit at +6 V and -6 V. Treated as point charges +Q and -Q.
A probe measures the on-axis potential V(x), where x = distance from the
+6 V sphere (metres).

    V(x) = C * (1/x - 1/(D - x)),   C = k*Q

Calibration: a point charge diverges at x = 0, so we fix C using an assumed
sphere radius a = 10 mm whose surface (x = a) sits at +6 V:
    6 V = C * (1/a - 1/(D - a))   ->   C = 6 / (1/a - 1/(D - a))

Run from this directory:  python generate_data.py
Writes potential_vs_position.csv with columns x, y, y_err (SI units: m, V, V).
"""
import numpy as np
import pandas as pd

D = 0.140           # m   centre-to-centre separation (140 mm)
A = 0.010           # m   assumed sphere radius (10 mm) for point-charge calibration
STEP = 0.005        # m   probe step (5 mm)
V_HALF = 6.0        # V   half the 12 V source -> +/-6 V on the surfaces
SIGMA = 0.10        # V   voltmeter precision (1-sigma measurement error)

# Charge constant fixed by the +6 V surface condition.
C = V_HALF / (1.0 / A - 1.0 / (D - A))

# Probe positions on 5 mm steps, kept clear of the spheres (a .. D-a).
x = np.arange(0.020, 0.120 + 1e-9, STEP)      # 20 mm .. 120 mm
V_true = C * (1.0 / x - 1.0 / (D - x))

# Add Gaussian measurement noise at the voltmeter precision.
rng = np.random.default_rng(42)               # fixed seed -> reproducible CSV
V_meas = V_true + rng.normal(0.0, SIGMA, size=x.size)
y_err = np.full_like(x, SIGMA)

pd.DataFrame({"x": x, "y": V_meas, "y_err": y_err}).to_csv(
    "potential_vs_position.csv", index=False)

print(f"C_theory = {C:.5f} V*m   (Q = {C / 8.9875e9:.3e} C)")
print(f"wrote potential_vs_position.csv with {x.size} points")
