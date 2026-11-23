# Babbage's Analytical Engine & Ada Lovelace's Note G Emulator

A Python & Streamlit emulator of Charles Babbage's **Analytical Engine** (separating the memory **Store** from the arithmetic **Mill**), executing Ada Lovelace's historic 1843 algorithm for computing Bernoulli numbers.

## Key Features
- **Store & Mill Architecture (`core.py`):** Simulates variable columns ($V_1 \dots V_{24+}$) and instruction execution with exact rational arithmetic (`fractions.Fraction`).
- **1843 Bug Simulation:** Toggle the famous historical typo in Operation 4 ($V_5 \div V_4$ instead of $V_4 \div V_5$) to observe error propagation across iterations.
- **Complexity & Trace Inspection:** Full step-by-step Mill operation trace and register state viewer.
- **Precision Benchmark:** Compares exact rational arithmetic against IEEE-754 64-bit `float` overflow up to $B_{300}$.

## Quickstart
```bash
pip install -r requirements.txt
streamlit run app.py
```

