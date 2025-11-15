# Enduro Strat

Enduro Strat is a lightweight toolkit for analysing endurance-race strategy. It provides helper functions, fuel and stint calculators, and a small Jupyter environment for exploring fixed-distance race scenarios (fuel burn, stints, pit stops, tyre timing, etc.).

## Features

### Fuel & Stint Planning

- Calculate fuel per lap, laps per stint, stints, stops, and last-stint adjustments.
- Works for both fixed-distance and fixed-time endurance events.

### Pit-Stop Modelling
- Account for tank capacity, tyre-change fuel limits, pit-lane loss, service time, and splash-and-dash logic.

### Notebook Workflow
- Jupyter notebooks for experimenting with what-if scenarios.
- Quick visualisation and iteration without running the full application.

### Modular Helper Functions
- strategy_helper.py centralises all calculations.
- Easy to extend with new models (weather, multi-driver, stint-pace deltas).

```shell
enduro_strat/
│
├── strategy_helper.py     # Core fuel, stint, and pit-strategy logic
├── jupyter/               # Notebooks for exploration
└── models/                # Optional: future expansion for data classes
```

## Getting Started
### 1. Install dependencies:

```shell
pip install -r requirements.txt
```

### 2. Launch the Jupyter environment:
```shell
jupyter notebook
```

### 3. Open the example notebook to explore race scenarios.
```shell
from strategy_helper import StrategyHelper

helper = StrategyHelper()

result = helper.calculate_stint_plan(
    total_laps=173,
    tank_capacity=103.9,
    fuel_per_lap=3.67,
    tyre_change_litres=21.0
)

print(result)
```

## Notes
- Inputs are based on real-world endurance racing conventions (LMP2 / GT3 style).
- All calculations assume clean laps without FCY or slow zones.
- Designed for exploratory strategy work rather than live telemetry integration.