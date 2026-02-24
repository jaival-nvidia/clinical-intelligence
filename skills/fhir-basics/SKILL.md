---
name: fhir-basics
description: Teaches agents how FHIR (Fast Healthcare Interoperability Resources) APIs work, what resources are available, and how to parse the JSON responses.
---

# FHIR Data Retrieval

FHIR is the standard API format used by ~70% of US hospitals. All queries use REST GET requests returning JSON.

## Common Endpoints

- `GET /Patient?name=John&name=Smith` -- search patients by name
- `GET /Patient/{id}` -- get a specific patient
- `GET /Condition?patient={id}` -- get diagnoses for a patient
- `GET /Observation?patient={id}` -- get lab results and vitals
- `GET /Observation?patient={id}&code={loinc}` -- get a specific lab by LOINC code
- `GET /MedicationRequest?patient={id}` -- get prescriptions
- `GET /Encounter?patient={id}` -- get visit history
- `GET /DiagnosticReport?patient={id}` -- get lab/imaging reports

## Key LOINC Codes for Common Labs

- `4548-4` -- Hemoglobin A1c (HbA1c)
- `2345-7` -- Glucose
- `2160-0` -- Creatinine
- `33914-3` -- eGFR (estimated Glomerular Filtration Rate)
- `2093-3` -- Total Cholesterol
- `2571-8` -- Triglycerides
- `2085-9` -- HDL Cholesterol
- `18262-6` -- LDL Cholesterol
- `8480-6` -- Systolic Blood Pressure
- `8462-4` -- Diastolic Blood Pressure

## Parsing FHIR JSON

A Patient search returns a Bundle with entries:
```
response['entry'][0]['resource']['id']          -- patient ID
response['entry'][0]['resource']['name'][0]     -- name object
  ['given'][0]                                  -- first name
  ['family']                                    -- last name
response['entry'][0]['resource']['birthDate']   -- "YYYY-MM-DD"
response['entry'][0]['resource']['gender']      -- "male" or "female"
```

A Condition search returns:
```
entry['resource']['code']['coding'][0]['code']     -- SNOMED or ICD code
entry['resource']['code']['coding'][0]['display']  -- human-readable name
entry['resource']['onsetDateTime']                 -- when diagnosed
entry['resource']['clinicalStatus']['coding'][0]['code'] -- "active", "resolved"
```

An Observation (lab) returns:
```
entry['resource']['code']['coding'][0]['display']  -- lab name
entry['resource']['valueQuantity']['value']        -- numeric result
entry['resource']['valueQuantity']['unit']         -- unit of measure
entry['resource']['effectiveDateTime']             -- when taken
```

A MedicationRequest returns:
```
entry['resource']['medicationCodeableConcept']['text']         -- drug name
entry['resource']['dosageInstruction'][0]['text']               -- dosage string
entry['resource']['status']                                     -- "active", "stopped"
```

## Pagination

FHIR responses default to 20 results. Use `_count=100` for more. Check for `response['link']` with `relation: "next"` for additional pages.

## Error Handling

- Always check if `entry` exists in the response before iterating
- Some fields may be missing -- use `.get()` with a fallback of "Not recorded"
- Never fabricate data. If a field is absent, say so explicitly.
