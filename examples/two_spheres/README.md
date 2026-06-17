# Example: potential between two charged spheres

Measuring the electric potential `V(x)` along the axis between two charged
spheres, and comparing the measurements against the point-charge theory.

## Physical setup

- Two spheres, centres **d = 140 mm** apart.
- Connected across a **12 V source**, so their surfaces sit at **+6 V** and **−6 V**.
- Treated as **point charges** `+Q` and `−Q`.
- A probe measures the on-axis potential `V(x)`, with `x` = distance from the
  +6 V sphere, stepped in **5 mm** increments.

By superposition, the on-axis potential is

    V(x) = k·Q · (1/x − 1/(d − x)) = C · (1/x − 1/(d − x)),   C = k·Q

A point charge diverges at `x = 0`, so the scale `C` is calibrated with an
assumed sphere radius **a = 10 mm** whose surface sits at +6 V:

    C = 6 V / (1/a − 1/(d − a)) = 0.0650 V·m   →   Q ≈ 7.2 pC

This is registered as the `two_sphere_potential` model in `../../models.py`,
which fits the single parameter `C` (and reports the derived charge `Q = C/k`).

## Files

- `generate_data.py` — produces `potential_vs_position.csv` (synthetic probe
  readings = theory + Gaussian noise at the 0.10 V voltmeter precision; fixed
  random seed, so it is reproducible). Units are SI: x in metres, V in volts.
- `potential_vs_position.csv` — the generated sample data (`x, y, y_err`).
- `two_spheres_fit.png` — the fit + theory overlay plot.

## Reproduce

From the repository root (with the venv set up — see the top-level README):

```bash
# 1. regenerate the sample data (optional; the CSV is already committed)
cd examples/two_spheres && python generate_data.py && cd ../..

# 2. fit the data and overlay the theoretical curve (C = 0.065 V·m)
python fit_lab_data.py examples/two_spheres/potential_vs_position.csv \
    --model two_sphere_potential \
    --theory 0.065 --theory-label "theory (C=0.065)" \
    -o examples/two_spheres/two_spheres_fit.png
```

## Result

The fit recovers `C = 0.0646 ± 0.0011 V·m` (charge `Q = (7.19 ± 0.12) × 10⁻¹² C`),
consistent with the calibrated theoretical value of 0.0650 V·m, with reduced
chi-square ≈ 0.7 — a good fit. In the plot the fit and theory curves overlap,
and the residuals (`data − fit` and `data − theory`) scatter evenly about zero.

> Note: the plot axes are labelled generically (`x`, `y`); here `x` is the probe
> position in metres and `y` is the potential in volts.
