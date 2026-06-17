"""
Generate synthetic potential-vs-position data for a parallel-plate capacitor.

Setup: two large parallel plates a distance d = 6 cm apart, connected across a
12 V source. The field between ideal plates is uniform, E = V_source / d, so the
on-axis potential rises LINEARLY from one plate to the other. A probe measures
V(x), with x = distance from the 0 V plate (metres), stepped in 5 mm increments.

    V(x) = E * x + V0,   E = V_source / d = 12 / 0.06 = 200 V/m,   V0 = 0

Run from this directory:  python generate_data.py
Writes potential_vs_position.csv with columns x, y, y_err (SI units: m, V, V).
"""
import numpy as np
import pandas as pd

D = 0.060           # m   plate separation (6 cm) -- must match PLATE_SEPARATION in models.py
STEP = 0.005        # m   probe step (5 mm)
V_SOURCE = 12.0     # V   source across the plates
SIGMA = 0.05        # V   multimeter resolution (1-sigma measurement error)

E_TRUE = V_SOURCE / D       # 200 V/m uniform field
V0_TRUE = 0.0               # probe origin at the 0 V plate

# Probe positions from one plate to the other on 5 mm steps.
x = np.arange(0.0, 0.060 + 1e-9, STEP)        # 0 mm .. 60 mm
V_true = E_TRUE * x + V0_TRUE

# Add Gaussian measurement noise at the multimeter resolution.
rng = np.random.default_rng(42)               # fixed seed -> reproducible CSV
V_meas = V_true + rng.normal(0.0, SIGMA, size=x.size)
y_err = np.full_like(x, SIGMA)

pd.DataFrame({"x": x, "y": V_meas, "y_err": y_err}).to_csv(
    "potential_vs_position.csv", index=False)

print(f"E_theory = {E_TRUE:.1f} V/m   (plate PD = {E_TRUE * D:.1f} V)")
print(f"wrote potential_vs_position.csv with {x.size} points")
