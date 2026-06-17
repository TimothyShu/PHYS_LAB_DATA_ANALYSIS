# Example: potential between two parallel charged cylinders

Measuring the electric potential `V(x)` along the axis joining two long parallel
conducting cylinders (a cylindrical capacitor), and comparing the measurements
against the line-charge theory.

## Physical setup

- Two long conducting cylinders, radius **a = 10 mm**, axes **d = 140 mm** apart.
- Length **l ≫ d**, so end effects are negligible and each behaves as a uniform
  **line charge**: −q on the left cylinder, +q on the right (linear density λ = q/l).
- Connected across a **12 V source**.
- A probe measures the on-axis potential `V(x)`, with `x` = distance from the
  left cylinder's axis, stepped in **5 mm** increments.

Superposing the two line charges gives a **logarithmic** on-axis potential:

    V(x) = B · [ ln(x/(d − x)) − ln(a/(d − a)) ],    B = q / (2·π·ε₀·l)

The `−ln(a/(d−a))` term sets `V = 0` at the left cylinder's surface (`x = a`).
The single fittable parameter is the prefactor `B`; `d` and `a` are known
geometry. The 12 V across the capacitor fixes the theoretical value:

    12 V = V(d−a) − V(a) = 2·B·ln((d−a)/a)   →   B = 6 / ln((d−a)/a) ≈ 2.339 V

This is registered as the `two_cylinder_potential` model in `../../models.py`,
which fits `B` and reports the derived charge-per-length `λ = 2·π·ε₀·B` and the
recovered capacitor PD (a cross-check that it returns ~12 V).

> **Note on geometry:** this is a *line-charge* model (potential ∝ ln r), correct
> for long cylinders/rods. It is **not** the point-charge model (potential ∝ 1/r)
> used for spheres — that model (`two_sphere_potential`) also exists in the
> registry, but does not apply to this apparatus.

## Files

- `generate_data.py` — produces `potential_vs_position.csv` (synthetic probe
  readings = theory + Gaussian noise at the 0.05 V multimeter resolution; fixed
  random seed, so it is reproducible). Units are SI: x in metres, V in volts.
- `potential_vs_position.csv` — the generated sample data (`x, y, y_err`).
- `two_cylinders_fit.png` — the fit + theory overlay plot.

## Reproduce

From the repository root (with the venv set up — see the top-level README):

```bash
# 1. regenerate the sample data (optional; the CSV is already committed)
cd examples/two_cylinders && python generate_data.py && cd ../..

# 2. fit the data and overlay the theoretical curve (B = 2.339 V)
python fit_lab_data.py examples/two_cylinders/potential_vs_position.csv \
    --model two_cylinder_potential \
    --theory 2.33924 --theory-label "theory (B=2.34)" \
    --xlabel "position x (m)" --ylabel "potential V (V)" \
    -o examples/two_cylinders/two_cylinders_fit.png
```

## Result

The fit recovers:

| Quantity | Fitted | Expected |
|---|---|---|
| Prefactor `B` | 2.3393 ± 0.0040 V | 2.339 V |
| Charge/length `λ` | (1.3014 ± 0.0022) × 10⁻¹⁰ C/m | — |
| Capacitor PD `2·B·ln((d−a)/a)` | 12.000 ± 0.020 V | 12 V (source) |

Reduced chi-square ≈ 0.72 — a good fit. The recovered capacitor PD lands right
on the 12 V source. In the plot the fit and theory curves overlap, and the
residuals (`data − fit` and `data − theory`) scatter evenly about zero.
