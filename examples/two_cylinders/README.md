# Example: potential between two parallel charged cylinders

Real measured potential `V(x)` along the axis joining two long parallel
conducting cylinders, compared against the line-charge theory.

## Physical setup

- Two long conducting cylinders, radius **a = 5 mm**, axes **d = 120 mm** apart,
  length **l ≫ d** (so they behave as line charges −q and +q), across a **12 V source**.
- A probe measures the on-axis potential. The probe position is read from the
  **near cylinder's surface**, so the axis distance is `x = x_probe + a` (the
  recorded `x = 0` is the surface, at axis distance 5 mm).

The superposed line-charge potential is

    V(x) = B·[ ln(x/(d − x)) − ln(a/(d − a)) ]  =  B·ln(x/(d − x)) + C

with the prefactor and constant fixed by the 12 V across the surfaces:

    B = 6 / ln((d − a)/a) = 6/ln(23) = 1.914 V
    C = B·ln((d − a)/a)   = 6.00 V   (midpoint potential)

i.e. **`V = 1.914·ln(x/(120 − x)) + 6`** (x in mm). `V = 0` at the near surface
(x = 5 mm), 6 V at the midpoint (x = 60 mm), 12 V at the far surface (x = 115 mm).
Registered as `two_cylinder_potential` in `../../models.py`.

## Files

- `parallel_cylinders.csv` — measured data (`x` = axis distance in m, `y` = mean
  of 3 trials, `y_err` = 0.05 V multimeter resolution).
- `parallel_cylinders_fit.png` — data + fit + theory overlay.
- `misspecification_demo.py` / `.png` — shows how a wrong fixed constant or an
  unmodeled offset inflates χ² and bends the residuals (teaching aid).

## Reproduce

From the repository root (venv set up — see the top-level README):

```bash
python fit_lab_data.py examples/two_cylinders/parallel_cylinders.csv \
    --model two_cylinder_potential \
    --theory 1.9136 --theory-label "theory (B=1.914, V=B*ln(x/(120-x))+6)" \
    --xlabel "axis distance x (m)" --ylabel "potential V (V)" \
    --no-residuals --no-chi2 --title "Parallel Cylinders (a=5mm, d=120mm)" \
    --xmax 0.115 -o examples/two_cylinders/parallel_cylinders_fit.png
```

## Result

| Quantity | Fit | Theory |
|---|---|---|
| Prefactor `B` | 1.939 ± 0.004 V | 1.914 V (= 6/ln23) |
| Capacitor PD `2·B·ln((d−a)/a)` | 12.16 ± 0.02 V | 12 V (source) |
| Charge/length `λ` | (1.079 ± 0.002) × 10⁻¹⁰ C/m | — |

The data reproduces `V = 1.914·ln(x/(120−x)) + 6` to ~1.3% on both `B` and the
recovered 12 V supply — the closest agreement of the example set. The plot shows
the characteristic S-curve (steep near each cylinder, flat through 6 V at the
midpoint), with fit and theory essentially coincident. χ²ᵥ ≈ 18 is somewhat
above 1, indicating the 0.05 V resolution slightly underestimates the true
point-to-point scatter (~0.2 V), but the shape, `B`, and PD all match theory.
