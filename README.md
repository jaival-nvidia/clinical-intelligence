# Clinical Intelligence -- DGX Station Demo

A Claude Code plugin that uses specialized AI agents to pull patient data from hospital FHIR endpoints, compile case summaries, and run cross-patient analysis -- all locally.

## What This Is

Hospitals store patient data across multiple systems (EHR, labs, pharmacy). Getting a complete picture of one patient means manually querying each system and compiling the results. This takes 1-2 hours per patient for tasks like tumor board preparation.

This plugin gives Claude Code a team of agents that automate that work:

- **Patient Data Agent** -- pulls demographics and diagnoses
- **Labs/Vitals Agent** -- pulls lab results and flags abnormal values
- **Medications Agent** -- pulls prescriptions and classifies drug types
- **Analyst Agent** -- writes Python code to analyze data across patients

The agents are taught hospital data formats and clinical knowledge through **skill files** (Markdown documents). The whole system is customizable by editing text files.

## Why DGX Station

Hospital patient data is protected by HIPAA. It cannot be sent to cloud AI services like ChatGPT or Claude's hosted API. The LLM must run locally inside the hospital's network.

A DGX Station runs the LLM (GLM-4.7-Flash via Ollama) on local GPUs. The agents query hospital endpoints and process data without anything leaving the building.

## What's Inside

```
clinical-intelligence/
  .claude-plugin/
    plugin.json                     # Plugin manifest
  skills/
    fhir-basics/SKILL.md           # How FHIR APIs work, endpoints, JSON paths
    clinical-knowledge/SKILL.md    # Lab reference ranges, condition codes, drug classes
    analysis-methods/SKILL.md      # How to write correct analysis code
    case-summary/SKILL.md          # /case-summary slash command
    cohort-compare/SKILL.md        # /cohort-compare slash command
  agents/
    patient-data-agent.md          # Queries Patient + Condition endpoints
    labs-vitals-agent.md           # Queries Observation endpoint (labs, vitals)
    medications-agent.md           # Queries MedicationRequest endpoint
    analyst-agent.md               # Writes and runs analysis code
  scripts/
    serve-llm.sh                   # Start GLM-4.7-Flash via Ollama
    test-fhir.py                   # Verify FHIR test server is reachable
    cache-fhir-data.py             # Pre-cache FHIR data as offline fallback
  fallback-data/                   # Cached FHIR responses (populated by script)
```

## Setup

### 1. LLM (already done if you have Ollama + GLM-4.7-Flash running)

```bash
ollama pull glm-4.7-flash
ollama run glm-4.7-flash "Hello"   # quick test
```

Ollama serves at `http://localhost:11434` by default.

### 2. Install skills and agents into your project

From your working directory (e.g., `~/clinical-demo`):

```bash
git clone https://github.com/jaival-nvidia/clinical-intelligence.git /tmp/ci-plugin

mkdir -p .claude/agents .claude/skills
cp /tmp/ci-plugin/agents/* .claude/agents/
cp -r /tmp/ci-plugin/skills/* .claude/skills/

rm -rf /tmp/ci-plugin
```

Then start Claude Code from that directory:

```bash
claude
```

Type `/` to verify skills appear: `/case-summary`, `/cohort-compare`, `/fhir-basics`, `/clinical-knowledge`, `/analysis-methods`.

### 3. Verify FHIR test server

The demo uses SMART on FHIR's public test server (`https://r4.smarthealthit.org`). No auth needed, synthetic patients, real FHIR format.

```bash
pip install requests
python clinical-intelligence/scripts/test-fhir.py
```

This prints a test patient and their conditions. Note the patient name/ID for the demo.

### 4. (Optional) Cache data for offline fallback

If you're worried about the FHIR server being slow during the demo:

```bash
python clinical-intelligence/scripts/cache-fhir-data.py
```

This saves FHIR responses to `fallback-data/` as local JSON files.

## Demo Commands

### Compile a patient case summary

```
/case-summary the first patient from https://r4.smarthealthit.org
```

This uses the fhir-basics and clinical-knowledge skills to query all FHIR endpoints, compile demographics, conditions, labs, and medications, and flag abnormal values.

### Run a cohort quality analysis

```
/cohort-compare Find all diabetic patients (SNOMED 44054006) from https://r4.smarthealthit.org. Get latest A1c (LOINC 4548-4) and medications. Find patients with A1c above 9% not on insulin or GLP-1. Show distribution.
```

This finds the patient cohort, pulls data for each, writes Python analysis code, and produces a report with statistics and a chart.

### Try a different clinical question

```
/cohort-compare Find all hypertensive patients (SNOMED 38341003) from https://r4.smarthealthit.org. Get latest systolic BP (LOINC 8480-6). Find patients with systolic above 140 not on any antihypertensive.
```

Same skills, different question. The system adapts because the skills teach it what the data means.

## How to Customize

### Add a new skill

Create a file at `skills/my-new-skill/SKILL.md`. Write the knowledge in Markdown. All agents will be able to use it.

Example: adding drug interaction knowledge, radiology terminology, or new quality measure definitions.

### Add a new agent

Create a file at `agents/my-agent.md` with YAML frontmatter (`name`, `description`) and a system prompt in the body.

Example: a radiology agent that queries FHIR DiagnosticReport endpoints for imaging results.

### Add a new command

Create a file at `commands/my-command.md` with a description and step-by-step instructions for how to orchestrate the agents.

## GUI Workbench

A Streamlit web app that provides a visual interface for the same clinical workflows -- no terminal needed.

```bash
cd app
pip install -r requirements.txt
streamlit run workbench.py
```

Features:
- NVIDIA dark theme
- Configure FHIR endpoints and test connections
- Pre-built workflows: Case Summary, Quality Gap Analysis, Custom Query
- Pre-populated clinical conditions (Diabetes, Hypertension, Heart Failure, CKD) with correct SNOMED/LOINC codes
- Code generation, execution, and chart display in one click
- Download results as TXT or the generated Python script
- Timing metrics (LLM generation time, code execution time)

The workbench talks directly to your local LLM (Ollama or vLLM) and loads the same skill files as the Claude Code plugin.

## Key Facts

- **FHIR** is the API standard used by ~70% of US hospitals (source: ONC 2024)
- **CMS122** (diabetes glycemic control) is a real quality measure hospitals must report
- **SMART on FHIR test server** at `r4.smarthealthit.org` returns synthetic data in the exact format real hospitals use
- The public test server requires no authentication; real hospital endpoints use OAuth2
- **GLM-4.7-Flash** is a 30B-parameter MoE model (3.6B active) that fits in ~60GB VRAM in BF16

## Disclaimers

- This is a proof of concept for research and operational use, not a clinical decision support system
- The FHIR test server contains synthetic patient data, not real patients
- Lab reference ranges and quality measure logic are simplified for demonstration purposes
- All clinical decisions should be made by qualified clinicians
- FAERS adverse event data (if queried) does not establish causation
