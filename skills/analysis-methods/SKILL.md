---
name: analysis-methods
description: Teaches the analyst agent how to write correct, readable Python analysis code using pandas, matplotlib, and scipy.
---

# Analysis Code Guidelines

## Libraries to Use

- `requests` -- for FHIR API calls
- `pandas` -- for data manipulation
- `matplotlib.pyplot` -- for charts
- `scipy.stats` -- for statistical tests (only when explicitly requested)
- `json` -- for JSON parsing

Do NOT import libraries that may not be installed (e.g., seaborn, plotly, sklearn) unless the user specifically requests them.

## Code Quality

- Write clear variable names (not `x`, `df2`, `temp`)
- Add a brief comment only when the logic is non-obvious
- Print intermediate results so the user can verify each step
- Always show the shape of dataframes after major operations (e.g., `print(f"Found {len(df)} patients")`)
- Save charts to files AND display them

## Common Patterns

### Building a patient DataFrame from FHIR

```python
import requests
import pandas as pd

base_url = "..."  # FHIR endpoint

def get_patients_with_condition(snomed_code):
    conditions = requests.get(f"{base_url}/Condition?code={snomed_code}&_count=200").json()
    patient_ids = list(set(
        e['resource']['subject']['reference'].split('/')[-1]
        for e in conditions.get('entry', [])
    ))
    return patient_ids

def get_latest_observation(patient_id, loinc_code):
    obs = requests.get(
        f"{base_url}/Observation?patient={patient_id}&code={loinc_code}&_sort=-date&_count=1"
    ).json()
    if obs.get('entry'):
        return obs['entry'][0]['resource']['valueQuantity']['value']
    return None
```

### Flagging Care Gaps

```python
gap_patients = df[(df['a1c'] > 9.0) & (~df['on_insulin'])]
print(f"Found {len(gap_patients)} patients with A1c > 9% not on insulin")
```

### Creating Visualizations

Always use clear titles, axis labels, and readable font sizes:
```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Distribution of HbA1c Among Diabetic Patients", fontsize=14)
ax.set_xlabel("HbA1c (%)", fontsize=12)
ax.set_ylabel("Number of Patients", fontsize=12)
```

## Guardrails

- Never compute statistics on fewer than 5 data points
- Always report the sample size alongside any percentage
- If data is missing for more than 30% of patients, flag it as a data quality issue
- Do not extrapolate or predict -- only describe what the data shows
