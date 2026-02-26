"""
Clinical Intelligence Workbench
NVIDIA-themed GUI for building clinical data workflows on FHIR endpoints.
Talks to a local LLM (Ollama / vLLM) with clinical skills loaded.
"""

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NVIDIA_GREEN = "#76B900"
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

PRESET_CONDITIONS = {
    "Diabetes Mellitus Type 2": {"snomed": "44054006", "lab": "HbA1c", "loinc": "4548-4", "threshold": "9%", "gap_meds": "insulin or GLP-1 agonist"},
    "Hypertension": {"snomed": "38341003", "lab": "Systolic BP", "loinc": "8480-6", "threshold": "140 mmHg", "gap_meds": "any antihypertensive"},
    "Heart Failure": {"snomed": "84114007", "lab": "BNP", "loinc": "42637-9", "threshold": "400 pg/mL", "gap_meds": "ACE inhibitor, ARB, or beta-blocker"},
    "Chronic Kidney Disease": {"snomed": "40055000", "lab": "eGFR", "loinc": "33914-3", "threshold": "below 30 mL/min", "gap_meds": "ACE inhibitor or ARB"},
}

DEFAULT_FHIR = "https://r4.smarthealthit.org"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_skill(name: str) -> str:
    path = SKILLS_DIR / name / "SKILL.md"
    if path.exists():
        return path.read_text()
    return ""


def build_system_prompt() -> str:
    fhir = load_skill("fhir-basics")
    clinical = load_skill("clinical-knowledge")
    analysis = load_skill("analysis-methods")
    return (
        "You are a clinical data analyst with expertise in FHIR APIs and healthcare quality measures.\n\n"
        "# FHIR Knowledge\n" + fhir + "\n\n"
        "# Clinical Knowledge\n" + clinical + "\n\n"
        "# Analysis Methods\n" + analysis + "\n\n"
        "When asked to analyze data, write complete, self-contained Python scripts that:\n"
        "- Use only requests, pandas, matplotlib, json (no other libraries)\n"
        "- Print all results clearly\n"
        "- Save any charts as PNG files in the current directory\n"
        "- Include sample sizes with every percentage\n"
        "- End with a plain-English summary\n"
        "- Add disclaimer: 'For research and operational purposes only. Clinical decisions should be made by qualified clinicians.'\n"
        "Return ONLY the Python code block, no explanation before or after."
    )


def query_llm(prompt: str, base_url: str, model: str) -> str:
    try:
        r = requests.post(
            f"{base_url}/api/chat",
            json={"model": model, "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt},
            ], "stream": False},
            timeout=300,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception:
        pass

    try:
        r = requests.post(
            f"{base_url}/v1/chat/completions",
            json={"model": model, "messages": [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt},
            ], "max_tokens": 4096, "temperature": 0.2},
            headers={"Authorization": "Bearer not-needed"},
            timeout=300,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error contacting LLM: {e}"


def extract_code(response: str) -> str | None:
    if "```python" in response:
        start = response.index("```python") + len("```python")
        end = response.index("```", start)
        return response[start:end].strip()
    if "```" in response:
        start = response.index("```") + 3
        if response[start] == "\n":
            start += 1
        end = response.index("```", start)
        return response[start:end].strip()
    return None


def run_code(code: str, work_dir: str) -> tuple[str, list[str]]:
    script_path = os.path.join(work_dir, "_analysis.py")
    with open(script_path, "w") as f:
        f.write(code)

    result = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=120,
        cwd=work_dir,
    )
    output = result.stdout
    if result.returncode != 0:
        output += "\n\nSTDERR:\n" + result.stderr

    pngs = sorted(Path(work_dir).glob("*.png"))
    return output, [str(p) for p in pngs]


def test_fhir_connection(url: str) -> tuple[bool, str]:
    try:
        r = requests.get(f"{url}/metadata", timeout=10)
        if r.status_code == 200:
            return True, "Connected"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

def inject_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        .stApp {{
            background: linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 100%);
        }}
        h1, h2, h3 {{
            font-weight: 600 !important;
        }}
        .nvidia-header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 1px solid #3a3a3a;
            border-left: 4px solid {NVIDIA_GREEN};
            border-radius: 8px;
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
        }}
        .nvidia-header h1 {{
            color: {NVIDIA_GREEN} !important;
            margin: 0 !important;
            font-size: 1.8rem !important;
        }}
        .nvidia-header p {{
            color: #999 !important;
            margin: 0.25rem 0 0 0 !important;
            font-size: 0.95rem !important;
        }}
        .endpoint-card {{
            background: #2d2d2d;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
        }}
        .status-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-green {{ background-color: {NVIDIA_GREEN}; }}
        .status-red {{ background-color: #ff4444; }}
        .status-gray {{ background-color: #666; }}
        .metric-card {{
            background: linear-gradient(135deg, #2d2d2d 0%, #333 100%);
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 1.25rem;
            text-align: center;
        }}
        .metric-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: {NVIDIA_GREEN};
        }}
        .metric-card .label {{
            font-size: 0.85rem;
            color: #999;
            margin-top: 0.25rem;
        }}
        .result-box {{
            background: #0d0d0d;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 1.25rem;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            white-space: pre-wrap;
            max-height: 500px;
            overflow-y: auto;
        }}
        div.stButton > button {{
            background: {NVIDIA_GREEN} !important;
            color: #000 !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.6rem 2rem !important;
            font-size: 0.95rem !important;
        }}
        div.stButton > button:hover {{
            background: #8fd400 !important;
        }}
        .stSelectbox label, .stTextInput label, .stTextArea label {{
            color: #ccc !important;
            font-weight: 500 !important;
        }}
        [data-testid="stSidebar"] {{
            background: #111 !important;
            border-right: 1px solid #2d2d2d !important;
        }}
        .disclaimer {{
            background: #1a1a00;
            border: 1px solid #4a4a00;
            border-radius: 6px;
            padding: 0.75rem 1rem;
            font-size: 0.8rem;
            color: #cca700;
            margin-top: 1rem;
        }}
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar: Configuration
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.markdown(f"<h2 style='color:{NVIDIA_GREEN}; margin-bottom:0;'>Configuration</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666; font-size:0.8rem;'>LLM & endpoint settings</p>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown(f"**<span style='color:{NVIDIA_GREEN}'>LLM Connection</span>**", unsafe_allow_html=True)
        llm_url = st.text_input("LLM Base URL", value="http://localhost:11434", help="Ollama default: http://localhost:11434")
        llm_model = st.text_input("Model Name", value="glm-4.7-flash:bf16")

        st.markdown("---")
        st.markdown(f"**<span style='color:{NVIDIA_GREEN}'>FHIR Endpoints</span>**", unsafe_allow_html=True)

        if "endpoints" not in st.session_state:
            st.session_state.endpoints = [{"name": "SMART Test Server", "url": DEFAULT_FHIR, "status": "unknown"}]

        for i, ep in enumerate(st.session_state.endpoints):
            col1, col2 = st.columns([3, 1])
            with col1:
                ep["name"] = st.text_input(f"Name##ep{i}", value=ep["name"], label_visibility="collapsed")
                ep["url"] = st.text_input(f"URL##ep{i}", value=ep["url"], label_visibility="collapsed")
            with col2:
                if st.button("Test", key=f"test_{i}"):
                    ok, msg = test_fhir_connection(ep["url"])
                    ep["status"] = "ok" if ok else "error"
                    if ok:
                        st.success("OK")
                    else:
                        st.error(msg)

        if st.button("+ Add Endpoint"):
            st.session_state.endpoints.append({"name": "", "url": "", "status": "unknown"})
            st.rerun()

        st.markdown("---")
        st.markdown(
            "<p style='color:#555; font-size:0.75rem;'>"
            "Powered by NVIDIA DGX Station<br>"
            "All processing runs locally<br>"
            "No patient data leaves this network"
            "</p>",
            unsafe_allow_html=True,
        )

    return llm_url, llm_model


# ---------------------------------------------------------------------------
# Main Page
# ---------------------------------------------------------------------------

def render_main(llm_url: str, llm_model: str):
    # Header
    st.markdown(
        "<div class='nvidia-header'>"
        "<h1>Clinical Intelligence Workbench</h1>"
        "<p>Build clinical data workflows on FHIR endpoints — powered by local AI on DGX Station</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Endpoint status bar
    cols = st.columns(len(st.session_state.endpoints))
    for i, ep in enumerate(st.session_state.endpoints):
        status_class = {"ok": "status-green", "error": "status-red"}.get(ep["status"], "status-gray")
        with cols[i]:
            st.markdown(
                f"<div class='endpoint-card'>"
                f"<span class='status-dot {status_class}'></span>"
                f"<strong>{ep['name'] or 'Unnamed'}</strong><br>"
                f"<span style='color:#888; font-size:0.8rem;'>{ep['url'][:40]}...</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Workflow selection
    tab1, tab2, tab3 = st.tabs(["Case Summary", "Quality Gap Analysis", "Custom Query"])

    # --- Tab 1: Case Summary ---
    with tab1:
        st.markdown("### Single Patient Case Summary")
        st.markdown("Pull demographics, conditions, labs, and medications for one patient.")

        fhir_url = st.session_state.endpoints[0]["url"] if st.session_state.endpoints else DEFAULT_FHIR
        patient_query = st.text_input("Patient search", value="first patient", placeholder="e.g., patient name or 'first patient'")

        if st.button("Generate Case Summary", key="btn_case"):
            prompt = (
                f"Using the FHIR endpoint at {fhir_url}, prepare a complete case summary for {patient_query}. "
                "Query the Patient, Condition, Observation, and MedicationRequest endpoints. "
                "Flag any abnormal lab values based on clinical reference ranges. "
                "Write a Python script that does all of this and prints a formatted case summary."
            )
            run_workflow(prompt, llm_url, llm_model)

    # --- Tab 2: Quality Gap Analysis ---
    with tab2:
        st.markdown("### Population Quality Gap Analysis")
        st.markdown("Screen patients for care gaps based on CMS quality measures.")

        fhir_url = st.session_state.endpoints[0]["url"] if st.session_state.endpoints else DEFAULT_FHIR

        condition = st.selectbox("Condition", list(PRESET_CONDITIONS.keys()))
        preset = PRESET_CONDITIONS[condition]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**SNOMED Code:** `{preset['snomed']}`")
            st.markdown(f"**Lab Metric:** {preset['lab']} (LOINC `{preset['loinc']}`)")
        with col2:
            st.markdown(f"**Threshold:** {preset['threshold']}")
            st.markdown(f"**Gap if not on:** {preset['gap_meds']}")

        if st.button("Run Gap Analysis", key="btn_gap"):
            prompt = (
                f"Using the FHIR endpoint at {fhir_url}, find all patients with {condition} "
                f"(SNOMED code {preset['snomed']}). For each patient, get their latest "
                f"{preset['lab']} (LOINC {preset['loinc']}) and medication list. "
                f"Find patients with {preset['lab']} above {preset['threshold']} "
                f"who are NOT on {preset['gap_meds']}. "
                f"Write a Python script that builds a pandas DataFrame, identifies gap patients, "
                f"creates a histogram of the {preset['lab']} distribution (save as gap_chart.png), "
                f"and prints a summary with counts and percentages."
            )
            run_workflow(prompt, llm_url, llm_model)

    # --- Tab 3: Custom Query ---
    with tab3:
        st.markdown("### Custom Query")
        st.markdown("Ask any clinical data question in plain English.")

        fhir_url = st.session_state.endpoints[0]["url"] if st.session_state.endpoints else DEFAULT_FHIR
        custom = st.text_area(
            "Your question",
            height=120,
            placeholder="e.g., Find all patients over 65 with both diabetes and hypertension. Compare their medication counts.",
        )

        if st.button("Run Query", key="btn_custom") and custom.strip():
            prompt = (
                f"Using the FHIR endpoint at {fhir_url}, answer this clinical data question:\n\n"
                f"{custom}\n\n"
                "Write a Python script that queries the relevant FHIR endpoints, "
                "analyzes the data, creates any relevant visualizations (save as PNG), "
                "and prints a clear summary."
            )
            run_workflow(prompt, llm_url, llm_model)


def run_workflow(prompt: str, llm_url: str, llm_model: str):
    work_dir = tempfile.mkdtemp(prefix="clinical_")

    with st.status("Running workflow...", expanded=True) as status:
        st.write("Sending query to LLM...")
        t0 = time.time()
        response = query_llm(prompt, llm_url, llm_model)
        llm_time = time.time() - t0
        st.write(f"LLM responded in {llm_time:.1f}s")

        code = extract_code(response)
        if not code:
            status.update(label="LLM did not return executable code", state="error")
            st.markdown("**LLM Response:**")
            st.markdown(f"<div class='result-box'>{response}</div>", unsafe_allow_html=True)
            return

        st.write("Executing analysis code...")
        with st.expander("Generated Code", expanded=False):
            st.code(code, language="python")

        t1 = time.time()
        try:
            output, charts = run_code(code, work_dir)
        except subprocess.TimeoutExpired:
            status.update(label="Code execution timed out", state="error")
            return
        exec_time = time.time() - t1
        st.write(f"Code executed in {exec_time:.1f}s")
        status.update(label="Workflow complete", state="complete")

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<div class='metric-card'><div class='value'>{llm_time:.1f}s</div><div class='label'>LLM Generation</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-card'><div class='value'>{exec_time:.1f}s</div><div class='label'>Code Execution</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<div class='metric-card'><div class='value'>{llm_time + exec_time:.1f}s</div><div class='label'>Total Time</div></div>",
            unsafe_allow_html=True,
        )

    # Output
    st.markdown("### Results")
    st.markdown(f"<div class='result-box'>{output}</div>", unsafe_allow_html=True)

    # Charts
    if charts:
        st.markdown("### Visualizations")
        for chart_path in charts:
            st.image(chart_path)

    # Downloads
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download Results (TXT)", output, file_name="results.txt", mime="text/plain")
    with col2:
        st.download_button("Download Code (PY)", code, file_name="analysis.py", mime="text/x-python")

    # Disclaimer
    st.markdown(
        "<div class='disclaimer'>"
        "⚠ This analysis uses synthetic FHIR data for research and demonstration purposes. "
        "Clinical decisions should be made by qualified clinicians. "
        "FAERS adverse event data does not establish causation."
        "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Clinical Intelligence Workbench",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    llm_url, llm_model = render_sidebar()
    render_main(llm_url, llm_model)


if __name__ == "__main__":
    main()
