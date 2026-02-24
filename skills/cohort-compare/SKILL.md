---
name: cohort-compare
description: Analyze a cohort of patients from FHIR endpoints to find care gaps and patterns. Use when asked to compare patients, find quality gaps, or analyze a population.
---

Analyze a patient cohort: $ARGUMENTS

Use your fhir-basics skill to query FHIR endpoints. Use your clinical-knowledge skill to identify care gaps. Use your analysis-methods skill to write correct Python analysis code.

Steps:
1. Identify the target condition and query the FHIR Condition endpoint to find matching patients
2. For each patient, pull the relevant lab values and medication list
3. Build a pandas DataFrame with one row per patient
4. Compute the requested metrics (counts, percentages, distributions)
5. Identify patients who fall into the care gap
6. Generate a visualization (chart) and save as PNG
7. Write a plain-English summary including sample size
8. End with: "This analysis is for research and operational purposes. Clinical decisions should be made by qualified clinicians."
