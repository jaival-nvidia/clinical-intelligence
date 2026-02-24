---
name: compare
description: "Analyze a cohort of patients across FHIR endpoints to find patterns and care gaps. Usage: /clinical:compare \"[research question about a patient population] from [FHIR endpoint URL]\""
---

When the user asks to analyze a patient cohort:

1. Parse the research question to identify:
   - The target condition (e.g., diabetes, hypertension, heart failure)
   - The metric of interest (e.g., A1c levels, blood pressure, medication coverage)
   - The care gap to check (e.g., "not on insulin", "BP above 140")

2. Delegate to **patient-data-agent**: Query the FHIR Condition endpoint to find all patients with the target condition. Return the list of patient IDs.

3. For each patient in the cohort, delegate to the appropriate agents in parallel:
   - **labs-vitals-agent**: Pull the relevant lab/vital for each patient (e.g., latest A1c)
   - **medications-agent**: Pull the medication list for each patient

4. Delegate to **analyst-agent**: Take the combined data from all agents and:
   - Build a pandas DataFrame with one row per patient
   - Compute the requested metrics (counts, percentages, distributions)
   - Identify patients who fall into the care gap
   - Generate a visualization (histogram, bar chart, or table as appropriate)
   - Write a plain-English summary of the findings

5. Present the results with:
   - The sample size and any data quality notes
   - The visualization
   - The list of gap patients (if applicable)
   - The disclaimer: "This analysis is for research and operational purposes. Clinical decisions should be made by qualified clinicians."
