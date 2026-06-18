# Example: potential between concentric ring electrodes

Real measured potential `V(r)` between two concentric ring electrodes (a 2D
coaxial geometry), compared against the logarithmic theory.

## Physical setup

- Inner ring radius **a = 10 mm**, outer ring radius **b = 60 mm**, across a **12 V source**.
- A probe measures the potential at radius `r`. The recorded `x` column is the
  radius in metres.

In the annulus, Laplace's equation gives a logarithmic potential:

    V(r) = B·ln(r/a),   V = 0 at the inner ring, V = source at the outer ring
    B = V_source / ln(b/a) = 12 / ln(60/10) = 12/ln6 = 6.70 V

Registered as `concentric_rings` in `../../models.py` (and `concentric_rings_freea`,
which fits the effective inner radius instead of fixing it).

## Files

- `concentric_rings.csv` — measured data (`x` = radius in m, `y` = mean of 3
  trials, `y_err` = 0.05 V). The inner-ring `(r, 0)` point is excluded — it is a
  reading on the conductor, not in the field region.
- `concentric_rings_fit.png` — data + fit + theory overlay.

## Reproduce

From the repository root (venv set up — see the top-level README):

```bash
python fit_lab_data.py examples/concentric_rings/concentric_rings.csv \
    --model concentric_rings \
    --theory 6.697 --theory-label "theory (B=6.70=12/ln6)" \
    --xlabel "radius r (m)" --ylabel "potential V (V)" \
    --no-residuals --no-chi2 --title "Concentric Rings (a = 10 mm)" \
    --xmin 0.010 -o examples/concentric_rings/concentric_rings_fit.png
```

## Result

| Quantity | Fit (a = 10 mm) | Theory |
|---|---|---|
| Prefactor `B` | 6.17 ± 0.01 V | 6.70 V (= 12/ln6) |
| Implied source `B·ln(b/a)` | 11.06 V | 12 V |
| χ²ᵥ | 4.6 | — |

**Note on the inner radius.** The data was originally analysed with the recorded
inner radius of 15 mm, which gave a very poor fit (χ²ᵥ ≈ 400) — the data was
visibly steeper near the inner ring than `ln(r/15)` allows. Letting the inner
radius float (`concentric_rings_freea`) preferred ~9.6 mm, so the geometry was
re-examined and corrected to **a = 10 mm**, which fits well (χ²ᵥ = 4.6). The
remaining ~8% amplitude shortfall (`B = 6.17` vs `6.70`, implied 11.1 V vs 12 V)
is consistent with the probe not reaching the full source voltage at the outer
ring (contact resistance / supply slightly under 12 V at the electrodes).
