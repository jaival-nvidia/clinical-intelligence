---
name: case
description: "Compile a complete case summary for a patient from FHIR endpoints. Usage: /clinical:case \"Prepare case summary for [patient name or ID] from [FHIR endpoint URL]\""
---

When the user requests a case summary:

1. Delegate to **patient-data-agent**: Find the patient and retrieve their demographics and active conditions.

2. Delegate to **labs-vitals-agent** (in parallel with step 3): Retrieve the patient's recent lab results and vital signs from the last 12 months. Flag any abnormal values.

3. Delegate to **medications-agent** (in parallel with step 2): Retrieve the patient's current active medications with dosages.

4. Once all three agents have returned their data, compile a formatted case summary with these sections:
   - **Patient Demographics**: Name, DOB, age, sex
   - **Active Conditions**: List with codes and onset dates
   - **Recent Lab Results**: Table with value, date, and normal/abnormal flag
   - **Current Medications**: List with dosages
   - **Clinical Flags**: Any notable findings (abnormal labs, potential care gaps based on conditions vs. medications)

5. End with the disclaimer: "This summary is auto-generated from FHIR data for research and operational use. Verify all information before clinical decision-making."
