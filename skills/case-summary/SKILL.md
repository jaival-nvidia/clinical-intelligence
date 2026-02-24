---
name: case-summary
description: Prepare a complete clinical case summary for a patient from FHIR endpoints. Use when asked to summarize a patient, compile a case, or prepare for tumor board.
---

Prepare a complete case summary for $ARGUMENTS

Use your fhir-basics skill to query the FHIR endpoints (Patient, Condition, Observation, MedicationRequest). Use your clinical-knowledge skill to flag abnormal values.

Steps:
1. Search for the patient and retrieve demographics
2. Get all active conditions with SNOMED/ICD codes
3. Get recent lab results and vital signs, flag any outside normal reference ranges
4. Get current medications with dosages
5. Compile into a formatted case summary with sections: Demographics, Active Conditions, Recent Labs, Current Medications, Clinical Flags
6. End with: "This summary is auto-generated from FHIR data for research and operational use. Verify all information before clinical decision-making."
