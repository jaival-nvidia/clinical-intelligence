---
name: clinical-knowledge
description: Teaches agents basic clinical reference ranges, common condition codes, and quality measure definitions so they can flag abnormal values and identify care gaps.
---

# Clinical Reference Knowledge

## Common Lab Reference Ranges

| Lab | Normal Range | Concerning | Unit |
|-----|-------------|------------|------|
| HbA1c | < 7.0% | > 9.0% = poor control | % |
| Fasting Glucose | 70-100 | > 126 = diabetic range | mg/dL |
| Creatinine | 0.7-1.3 (male), 0.6-1.1 (female) | > 1.5 = impaired renal | mg/dL |
| eGFR | > 60 | < 30 = severe CKD | mL/min/1.73m2 |
| Total Cholesterol | < 200 | > 240 = high | mg/dL |
| LDL | < 100 | > 160 = high | mg/dL |
| HDL | > 40 (male), > 50 (female) | < 40 = low | mg/dL |
| Systolic BP | < 120 | > 140 = hypertension | mmHg |
| Diastolic BP | < 80 | > 90 = hypertension | mmHg |

When reporting lab values, always flag values outside the normal range.

## Common SNOMED Condition Codes

- `44054006` -- Type 2 Diabetes Mellitus
- `38341003` -- Essential Hypertension
- `84114007` -- Heart Failure
- `13645005` -- Chronic Obstructive Pulmonary Disease
- `46635009` -- Type 1 Diabetes Mellitus
- `40055000` -- Chronic Kidney Disease
- `53741008` -- Coronary Artery Disease
- `195967001` -- Asthma

## CMS Quality Measures (Common)

**CMS122 -- Diabetes: Poor Glycemic Control**
- Population: Patients aged 18-75 with diabetes
- Metric: % with HbA1c > 9.0%
- Action: Flag for therapy intensification

**CMS135 -- Heart Failure: ACE Inhibitor/ARB/ARNI Therapy**
- Population: Patients with heart failure and LVEF < 40%
- Metric: % prescribed ACE inhibitor, ARB, or ARNI
- Action: Flag if not on appropriate medication

**CMS165 -- Controlling High Blood Pressure**
- Population: Patients aged 18-85 with hypertension
- Metric: % with BP < 140/90
- Action: Flag for medication adjustment

## Drug Classes

When checking medication coverage, recognize these drug class groupings:

**Diabetes medications:** metformin, glipizide, glyburide, insulin (any), liraglutide, semaglutide, empagliflozin, dapagliflozin, sitagliptin, pioglitazone

**Antihypertensives:** lisinopril, enalapril, ramipril (ACE inhibitors); losartan, valsartan, irbesartan (ARBs); amlodipine, nifedipine (CCBs); metoprolol, atenolol, carvedilol (beta-blockers); hydrochlorothiazide, chlorthalidone (diuretics)

**Statins:** atorvastatin, rosuvastatin, simvastatin, pravastatin

**Heart failure medications:** lisinopril, enalapril, losartan, valsartan, sacubitril/valsartan (Entresto), carvedilol, metoprolol succinate, spironolactone, eplerenone

## Guardrails

- These reference ranges are general guidelines, not diagnostic criteria
- Never state that a patient "has" a condition based on a lab value alone
- Always include the disclaimer: "This is for informational and research purposes, not clinical decision-making"
- When flagging care gaps, use language like "may warrant review" not "requires treatment"
