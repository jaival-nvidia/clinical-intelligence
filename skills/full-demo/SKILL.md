---
name: full-demo
description: Run the complete Clinical Intelligence demo end-to-end. Use when asked to run the full demo, showcase all capabilities, or demonstrate the complete workflow.
---

Run the complete Clinical Intelligence demo using the FHIR endpoint at $ARGUMENTS

This demo showcases all skills and agents working together. Execute these three phases in sequence:

## Phase 1: Single Patient Case Summary

Using your fhir-basics and clinical-knowledge skills:
1. Query the FHIR Patient endpoint and pick the first patient
2. Pull their demographics, active conditions (from Condition endpoint), recent lab results (from Observation endpoint), and current medications (from MedicationRequest endpoint)
3. Flag any lab values outside normal reference ranges
4. Compile a formatted case summary with sections: Demographics, Active Conditions, Recent Labs (with abnormal flags), Current Medications, Clinical Flags
5. Print: "--- Phase 1 Complete: Case summary compiled in seconds. This normally takes a nurse coordinator 1-2 hours. ---"

## Phase 2: Population Quality Gap Analysis (Diabetes)

Using your fhir-basics, clinical-knowledge, and analysis-methods skills:
1. Query the FHIR Condition endpoint for all patients with diabetes (SNOMED code 44054006)
2. For each diabetic patient, get their latest HbA1c (LOINC 4548-4) and medication list
3. Write and execute Python code to:
   - Build a pandas DataFrame with patient ID, latest A1c value, and medication list
   - Identify patients with A1c > 9% who are NOT on insulin or a GLP-1 agonist
   - Create a histogram of A1c distribution and save as diabetic_a1c_chart.png
   - Print the number and percentage of gap patients
4. Print: "--- Phase 2 Complete: Screened entire diabetic population for CMS Quality Measure 122 (poor glycemic control). This normally takes weeks of manual chart abstraction. ---"

## Phase 3: Population Quality Gap Analysis (Hypertension)

Using the same skills:
1. Query the FHIR Condition endpoint for all patients with hypertension (SNOMED code 38341003)
2. For each hypertensive patient, get their latest systolic blood pressure (LOINC 8480-6) and medication list
3. Write and execute Python code to:
   - Build a pandas DataFrame with patient ID, latest systolic BP, and medication list
   - Identify patients with systolic > 140 who are NOT on any antihypertensive
   - Create a histogram of BP distribution and save as hypertension_bp_chart.png
   - Print the number and percentage of gap patients
4. Print: "--- Phase 3 Complete: Screened entire hypertensive population for CMS Quality Measure 165 (blood pressure control). Same skills, different disease -- zero code changes. ---"

## Wrap-Up

Print a final summary:
```
============================================
CLINICAL INTELLIGENCE DEMO COMPLETE
============================================
Phase 1: Patient case summary compiled from 4 FHIR endpoints
Phase 2: Diabetic population screened for quality gap (CMS122)
Phase 3: Hypertensive population screened for quality gap (CMS165)

All data queried from live FHIR endpoints.
All analysis code generated and executed by AI agents.
All processing ran locally on DGX Station.
No patient data left this network.
============================================
```

Add disclaimer: "This demo uses synthetic FHIR data for research and demonstration purposes. Clinical decisions should be made by qualified clinicians."
