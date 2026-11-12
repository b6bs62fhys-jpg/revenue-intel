# revenue-intel (working title)

Open baseline for finding VAT carousel fraud in e-invoice data using graph analysis.

- `synth.py`   synthetic invoice network with planted fraud rings (easy and hard mode)
- `score.py`   baseline risk score: loop share of sales, short activity span, turnover burst
- `run_demo.py` runs both modes and prints precision and recall

```
pip install networkx numpy
python3 run_demo.py
```

Current baseline (synthetic data, seed 7):

| mode | top N = fraud firms | top 2N recall |
|------|---------------------|---------------|
| easy | 100% / 100%         | 100%          |
| hard | 58.5% / 58.5%       | 89.2%         |

Synthetic data only. No real tax data is used. Hard mode adds honest long-lived loops
and leaky fraud rings with cover business. The aim is to beat this baseline and
publish the comparison, including the published Bulgarian network method
(Alexopoulos et al., JRSS A, 2025) as a second reference.

## Contributing

Open an issue if you have a better score, a harder synthetic scenario, or a reference method to compare against. Results on synthetic data only, please say so in the title.

## Status

Early baseline. No real tax data. Not a product.
