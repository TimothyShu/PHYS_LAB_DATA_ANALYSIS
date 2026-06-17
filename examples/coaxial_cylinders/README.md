# Example: coaxial cylindrical capacitor

Measuring the radial potential `V(p)` inside a **coaxial** capacitor — one
cylinder inside another — and comparing it against the logarithmic theory.

## Physical setup

- An inner conductor of radius **a = 15 mm** inside an outer cylindrical shell of
  radius **b = 110 mm**, length **l ≫ b** (so end effects are negligible),
  connected across a **12 V source**.
- The probe position **p is zeroed at the inner surface**: `p = 0` at the inner
  conductor (radius `r = a`), stepped in **5 mm**.
- The span runs from the inner surface (`p = 0`) to the outer shell
  (`p = b − a = 110 − 15 = 95 mm`), so the potential goes **0 V → 12 V**.

The field between coaxial conductors is radial, `E(r) = λ/(2·π·ε₀·r)`, so the
potential is a **single logarithm** in the radius `r = p + a`:

    V(p) = B · ln((p + a) / a),    B = q / (2·π·ε₀·l) = λ / (2·π·ε₀)

`V = 0` at `p = 0` (inner surface) by construction. The fitted parameter is the
prefactor `B`; `a` and `b` are known geometry. The 12 V across the gap fixes

    B = V_source / ln(b/a) = 12 / ln(110/15) ≈ 6.023 V

Registered as `coaxial_potential` in `../../models.py`.

> Contrast with the [two_cylinders](../two_cylinders) example (two *parallel*
> cylinders side by side): there the potential is `B[ln(x/(d−x)) − const]`; here,
> with one cylinder *inside* the other, it is the simpler `B·ln((p+a)/a)`.

## Files

- `generate_data.py` — produces `potential_vs_position.csv` (theory + Gaussian
  noise at 0.10 V; fixed seed, reproducible). The `x` column is the zeroed radial
  position `p` (0 .. 0.095 m).
- `potential_vs_position.csv` — the generated sample data.
- `coaxial_cylinders_fit.png` — the fit + theory overlay plot.

## Reproduce

From the repository root (with the venv set up — see the top-level README):

```bash
cd examples/coaxial_cylinders && python generate_data.py && cd ../..

python fit_lab_data.py examples/coaxial_cylinders/potential_vs_position.csv \
    --model coaxial_potential \
    --theory 6.0228 --theory-label "theory (B=6.02)" \
    --xlabel "radial position from inner surface p (m)" --ylabel "potential V (V)" \
    -o examples/coaxial_cylinders/coaxial_cylinders_fit.png
```

## Result

| Quantity | Fitted | Expected |
|---|---|---|
| Prefactor `B` | 6.024 ± 0.016 V | 6.023 V |
| Charge/length `λ` | (3.352 ± 0.009) × 10⁻¹⁰ C/m | — |
| Capacitor PD `B·ln(b/a)` | 12.003 ± 0.032 V | 12 V (source) |
| Capacitance/length `2πε₀/ln(b/a)` | 2.79 × 10⁻¹¹ F/m | (geometric) |

Reduced chi-square ≈ 0.76 — a good fit. `V` runs from 0 V at the inner conductor
to 12 V at the outer shell, with the characteristic steep-then-flattening
logarithmic profile, and the residuals scatter evenly about zero.

(The capacitance per length is purely geometric — it depends only on `b/a`, not
on the fitted `B` — so it is reported as a constant with no fit uncertainty.)
