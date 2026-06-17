# Example: potential between parallel capacitor plates

Measuring the electric potential `V(x)` across a parallel-plate capacitor and
comparing it against the uniform-field (linear) theory.

## Physical setup

- Two large parallel plates, separation **d = 6 cm**, connected across a **12 V source**.
- The field between ideal plates is **uniform**, `E = V_source / d`, so the
  potential rises **linearly** from one plate to the other.
- A probe measures `V(x)`, with `x` = distance from the 0 V plate, stepped in
  **5 mm** increments (0 → 60 mm).

$$V(x) = E\,x + V_0,\qquad E = \frac{V_\text{source}}{d} = \frac{12}{0.06} = 200\ \text{V/m},\quad V_0 = 0$$

Two fittable parameters: the field `E` (slope) and an offset `V0` (probe-origin
or contact-potential zero). The plate PD follows as `E·d`. This uses the
`parallel_plate_potential` model in `../../models.py` (a linear law with
field/PD reporting); the generic `linear` model would fit identically.

> Contrast with the other examples: parallel plates give a **linear** potential
> (uniform field), the **cylinders** give a **logarithmic** one (`ln r`), and
> **point charges/spheres** give a `1/r` one. Same framework, different model.

## Files

- `generate_data.py` — produces `potential_vs_position.csv` (theory + Gaussian
  noise at the 0.05 V multimeter resolution; fixed seed, reproducible). SI units.
- `potential_vs_position.csv` — the generated sample data (`x, y, y_err`).
- `parallel_plates_fit.png` — the fit + theory overlay plot.

## Reproduce

From the repository root (with the venv set up — see the top-level README):

```bash
# 1. regenerate the sample data (optional; the CSV is already committed)
cd examples/parallel_plates && python generate_data.py && cd ../..

# 2. fit the data and overlay the theoretical line (E = 200 V/m, V0 = 0)
python fit_lab_data.py examples/parallel_plates/potential_vs_position.csv \
    --model parallel_plate_potential \
    --theory 200 0 --theory-label "theory (E=200 V/m)" \
    --xlabel "position x (m)" --ylabel "potential V (V)" \
    -o examples/parallel_plates/parallel_plates_fit.png
```

## Result

| Quantity | Fitted | Expected |
|---|---|---|
| Field `E` | 200.42 ± 0.74 V/m | 200 V/m |
| Offset `V0` | −0.019 ± 0.026 V | 0 V |
| Plate PD `E·d` | 12.025 ± 0.044 V | 12 V (source) |

Reduced chi-square ≈ 0.89 — a good fit. The recovered plate PD lands on the
12 V source, the offset is consistent with zero, and the residuals scatter
evenly about zero.
