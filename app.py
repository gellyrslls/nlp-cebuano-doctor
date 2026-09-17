"""Streamlit Web UI for Cebuano Doctor Circular Medical NLP Pipeline.

Bespoke Tailwind Zinc developer design system inspired by Linear, shadcn/ui,
and GitHub Light (white-coat medical / editorial paper aesthetic).
Distraction-free, zero AI-vibe-coded gradients or unprompted emojis.
Defaults to high-contrast Light Mode with instant Dark Mode toggle.
"""
import json
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

from src.domain.pipeline import CebuanoDoctorPipeline
from src.providers.ollama_provider import OllamaProvider
from src.storage import save_run
from src.ui_helpers import SAMPLE_PROMPTS, get_pipeline, list_recent_runs

st.set_page_config(
    page_title="Cebuano Doctor | Doktor sa Sugbo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme state initialization (defaults to Light Mode: white coat aesthetic)
if "theme" not in st.session_state:
    st.session_state.theme = "light"

is_dark = st.session_state.theme == "dark"

# Dynamic Tailwind Zinc Token Resolution
BG_COLOR = "#09090b" if is_dark else "#fafafa"
SURFACE_COLOR = "#18181b" if is_dark else "#ffffff"
SURFACE_SUBTLE = "#27272a" if is_dark else "#f4f4f5"
SURFACE_ACTIVE = "#27272a" if is_dark else "#e4e4e7"
BORDER_COLOR = "#27272a" if is_dark else "#e4e4e7"
BORDER_STRONG = "#3f3f46" if is_dark else "#d4d4d8"
TEXT_PRIMARY = "#f4f4f5" if is_dark else "#18181b"
TEXT_SECONDARY = "#a1a1aa" if is_dark else "#52525b"
TEXT_MUTED = "#71717a"
HEADER_BG = "rgba(9, 9, 11, 0.85)" if is_dark else "rgba(250, 250, 250, 0.85)"

CUSTOM_CSS = f"""
<style>
  :root {{
    --bg: {BG_COLOR};
    --surface: {SURFACE_COLOR};
    --surface-subtle: {SURFACE_SUBTLE};
    --surface-active: {SURFACE_ACTIVE};
    --border: {BORDER_COLOR};
    --border-strong: {BORDER_STRONG};
    --text-primary: {TEXT_PRIMARY};
    --text-secondary: {TEXT_SECONDARY};
    --text-muted: {TEXT_MUTED};
    --card-radius: 6px;
    --btn-radius: 6px;
  }}

  html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
  }}

  .block-container {{
    max-width: 1040px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }}

  header[data-testid="stHeader"] {{
    background: {HEADER_BG} !important;
    backdrop-filter: blur(8px) !important;
  }}

  [data-testid="stSidebar"] {{
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }}

  /* Typography */
  .mono-eyebrow {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 2px;
  }}

  h1, .masthead-title {{
    font-size: 24px !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
    margin: 0 0 4px 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
  }}

  .masthead-sub {{
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 16px;
  }}

  /* Hero Block */
  .workout-hero {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--card-radius);
    padding: 16px 20px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }}
  .hero-title {{
    font-size: 17px;
    font-weight: 800;
    color: var(--text-primary);
    margin: 3px 0;
  }}
  .hero-desc {{
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.4;
  }}

  /* Stat Chips */
  .stat-chip-group {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .stat-chip {{
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    padding: 6px 10px;
    border-radius: var(--card-radius);
    display: flex;
    flex-direction: column;
    min-width: 90px;
  }}
  .stat-label {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    letter-spacing: 0.05em;
  }}
  .stat-val {{
    font-size: 12px;
    font-weight: 700;
    color: var(--text-primary);
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }}

  /* Protocol Banner */
  .protocol-banner {{
    background: var(--surface-subtle);
    border-left: 3px solid var(--border-strong);
    padding: 10px 14px;
    border-radius: 0 var(--card-radius) var(--card-radius) 0;
    margin-bottom: 18px;
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.45;
  }}
  .protocol-banner strong {{
    color: var(--text-primary);
  }}

  /* Stage Cards */
  .ex-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--card-radius);
    margin-bottom: 14px;
    overflow: hidden;
  }}
  .ex-card-header {{
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .ex-card-title-group {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .ex-index {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 11px;
    font-weight: 800;
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    color: var(--text-muted);
    padding: 2px 6px;
    border-radius: var(--card-radius);
  }}
  .ex-name {{
    font-size: 14px;
    font-weight: 800;
    color: var(--text-primary);
  }}
  .ex-scheme {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 10px;
    font-weight: 700;
    color: var(--text-primary);
    background: var(--surface-subtle);
    border: 1px solid var(--border-strong);
    padding: 2px 7px;
    border-radius: var(--card-radius);
  }}

  .ex-card-body {{
    padding: 14px 16px;
  }}
  .ex-meta-bar {{
    display: flex;
    gap: 6px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }}
  .meta-chip {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    font-weight: 600;
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 2px 7px;
    border-radius: var(--card-radius);
  }}
  .meta-label {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text-muted);
  }}

  /* Two Column Grid */
  .ex-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 14px;
  }}
  @media (max-width: 768px) {{
    .ex-grid {{
      grid-template-columns: 1fr;
    }}
  }}

  .col-heading {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 6px;
  }}
  .ex-instruction {{
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 10px;
    white-space: pre-wrap;
  }}

  .callout-box {{
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    border-radius: var(--card-radius);
    padding: 8px 12px;
    font-size: 11px;
    color: var(--text-secondary);
    line-height: 1.45;
  }}
  .guard-box {{
    background: var(--surface);
    border: 1px dashed var(--border-strong);
    border-radius: var(--card-radius);
    padding: 8px 12px;
    font-size: 11px;
    color: var(--text-secondary);
    line-height: 1.45;
  }}
  .guard-label {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--text-primary);
    margin-bottom: 2px;
  }}

  .cebuano-guidance-text {{
    font-size: 13px;
    color: var(--text-primary);
    line-height: 1.55;
    white-space: pre-wrap;
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    border-radius: var(--card-radius);
    padding: 12px 14px;
    margin-bottom: 10px;
  }}

  /* Button Overrides: Fix truncation by removing nowrap on internal p tags */
  div.stButton > button {{
    border-radius: var(--btn-radius) !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border) !important;
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    white-space: normal !important;
    word-break: break-word !important;
    height: auto !important;
    min-height: 48px !important;
    padding: 6px 6px !important;
    text-align: center !important;
    line-height: 1.25 !important;
  }}
  div.stButton > button p {{
    white-space: normal !important;
    word-break: break-word !important;
    text-overflow: unset !important;
    overflow: visible !important;
    font-size: 11px !important;
    line-height: 1.25 !important;
    margin: 0 !important;
    padding: 0 !important;
  }}
  div.stButton > button:hover {{
    border-color: var(--border-strong) !important;
    background-color: var(--surface-subtle) !important;
    color: var(--text-primary) !important;
  }}
  div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {{
    background-color: var(--text-primary) !important;
    color: var(--bg) !important;
    border: 1px solid var(--text-primary) !important;
    font-weight: 700 !important;
  }}
  div.stButton > button[kind="primary"] p, div.stButton > button[data-testid="baseButton-primary"] p {{
    color: var(--bg) !important;
  }}
  div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover {{
    background-color: {('#ffffff' if is_dark else '#000000')} !important;
    color: var(--bg) !important;
  }}

  [data-testid="stMetric"] {{
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--card-radius) !important;
    padding: 8px 12px !important;
  }}
  [data-testid="stMetricLabel"] {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 9px !important;
    font-weight: 700 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
  }}
  [data-testid="stMetricValue"] {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
  }}

  div.stTextArea textarea {{
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--card-radius) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: 13px !important;
  }}
  div.stTextArea textarea:focus {{
    border-color: var(--border-strong) !important;
    box-shadow: none !important;
  }}

  div[data-testid="stAlert"] {{
    background-color: var(--surface-subtle) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--card-radius) !important;
    color: var(--text-primary) !important;
  }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


BENCHMARK_PERSONAS: List[Dict[str, Any]] = [
    {
        "id": "01",
        "key": "tc_library",
        "tag": "HEADACHE",
        "button_label": "01: TC Library\nAsthenopia",
        "name": "USC TC Library",
        "meta": "Asthenopia · 20-20-20",
        "prompt_key": "1. Tension Headache (TC Library)",
        "syndrome": "Digital Asthenopia & Tension Headache",
        "persona": "3rd-Yr BS Civil Engineering student studying at USC Talamban Campus library",
        "chief_complaint": SAMPLE_PROMPTS["1. Tension Headache (TC Library)"],
        "idiom": "bakos sa agtang (circumferential band)",
        "guard": "Supportive care only: 20-20-20 visual rest rule, hydration, darkness, paracetamol. No prescription drugs.",
    },
    {
        "id": "02",
        "key": "carcar_aunt",
        "tag": "PANUHOT",
        "button_label": "02: Carcar Aunt\nPanuhot",
        "name": "Carcar City Aunt",
        "meta": "Myofascial Spasm",
        "prompt_key": "2. Panuhot (Carcar City Aunt)",
        "syndrome": "Thoracic Myofascial Trigger Spasm",
        "persona": "52-Year-Old Aunt in Carcar City exposed to sudden rain and electric fan draft",
        "chief_complaint": SAMPLE_PROMPTS["2. Panuhot (Carcar City Aunt)"],
        "idiom": "panuhot / lusay-lusay (cold draft muscle knot)",
        "guard": "Reassure natural muscle etiology. Safe warm compress and gentle ginger-oil rub. Strictly no forceful spinal cracking.",
    },
    {
        "id": "03",
        "key": "it_park_bpo",
        "tag": "PASMO",
        "button_label": "03: IT Park BPO\nPasmo & Kabuhi",
        "name": "Cebu IT Park BPO",
        "meta": "Hypoglycemia · Gastritis",
        "prompt_key": "3. Pasmo & Kabuhi (IT Park BPO)",
        "syndrome": "Fasting Hypoglycemia & Hyperacidic Gastritis",
        "persona": "24-Year-Old Night-Shift BPO Agent at Cebu IT Park, Apas skipping meals on call queue",
        "chief_complaint": SAMPLE_PROMPTS["3. Pasmo & Kabuhi (IT Park BPO)"],
        "idiom": "pasmo / kabuhi (hunger tremor & gastric flutter)",
        "guard": "Immediate complex carbohydrates and protein intake. Discontinue high-caffeine energy drinks. Red flag if syncope occurs.",
    },
    {
        "id": "04",
        "key": "fuente_pungko",
        "tag": "DIARRHEA",
        "button_label": "04: Pungko-Pungko\nKalibanga",
        "name": "Fuente Pungko-Pungko",
        "meta": "ORS · No Antibiotics",
        "prompt_key": "4. Kalibanga (Fuente Pungko-pungko)",
        "syndrome": "Acute Watery Gastroenteritis",
        "persona": "21-Year-Old BS Nursing student experiencing acute diarrhea after eating at street food stall",
        "chief_complaint": SAMPLE_PROMPTS["4. Kalibanga (Fuente Pungko-pungko)"],
        "idiom": "kalibanga / pamalaybalay (watery stool & colic)",
        "guard": "Antimicrobial Stewardship: Strictly PROHIBIT self-administering ciprofloxacin or leftover antibiotics. Prioritize Oral Rehydration Salts (ORS).",
    },
    {
        "id": "05",
        "key": "srp_site",
        "tag": "PNEUMONIA",
        "button_label": "05: SRP Site\nPneumonia",
        "name": "SRP Reclamation Site",
        "meta": "Emergency Triage",
        "prompt_key": "5. Pneumonia / Chest Pain (SRP)",
        "syndrome": "Lower Respiratory Infection / Pleurisy",
        "persona": "28-Year-Old Construction Safety Lead at South Road Properties with 39.2°C fever and rust sputum",
        "chief_complaint": SAMPLE_PROMPTS["5. Pneumonia / Chest Pain (SRP)"],
        "idiom": "tayaon nga plema (rust-colored sputum)",
        "guard": "EMERGENCY TRIAGE: Rust sputum, high fever (39.2°C), and stabbing chest pain indicate pulmonary consolidation. Direct immediately to hospital emergency room.",
    },
]


def init_session_state() -> None:
    """Initialize session state variables."""
    if "chief_complaint" not in st.session_state:
        st.session_state.chief_complaint = BENCHMARK_PERSONAS[0]["chief_complaint"]
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "active_preset_key" not in st.session_state:
        st.session_state.active_preset_key = BENCHMARK_PERSONAS[0]["key"]


@st.dialog("Clinical Architecture & Circular Pipeline")
def show_architecture_dialog() -> None:
    st.markdown("""
    ### Three-Stage Circular Pipeline Architecture
    
    1. **Stage 01: Natural Language Understanding (NLU)**
       - Engine: Google DeepMind Gemma 4 (`gemma4:e2b`)
       - Function: Contextualizes colloquial Cebuano medical idioms (*panuhot*, *pasmo*, *kabuhi*, *lupot*) into standardized clinical English representation.
    
    2. **Stage 02: Evidence-Based Clinical Reasoning & Triage**
       - Engine: MedGemma Clinical LLM (`alibayram/medgemma`)
       - Function: Differential triage, supportive care recommendations, antimicrobial stewardship (strictly prohibits unindicated antibiotics), and red flag screening.
    
    3. **Stage 03: Natural Language Generation (NLG)**
       - Engine: Google DeepMind Gemma 4 (`gemma4:e2b`)
       - Function: Translates clinical English guidance back into empathetic, warm, natural Sinugboanon without confusing medical jargon.
    
    ### Infrastructure & Privacy
    - **100% Offline Air-Gapped:** Zero health data transmits to external APIs. Runs on localhost Ollama daemon.
    - **Model Storage:** Anchored on secondary partition `D:\\files\\ollama\\models` to protect system drive storage.
    """)


@st.dialog("Clinical Protocol & Academic Disclaimer")
def show_protocol_dialog() -> None:
    st.markdown("""
    ### Academic NLP Research Prototype Disclaimer
    
    This application is an educational prototype developed for **CS 5101 Natural Language Processing** at the **University of San Carlos** (Instructor: Dr. Vladimir Mariano).
    
    - **Non-Prescriptive Constraint:** The system is prompt-engineered against prescribing regulated pharmaceuticals or calculating drug dosages.
    - **Antimicrobial Stewardship:** Strictly prohibits self-administering antibiotics (such as ciprofloxacin or leftover amoxicillin) for acute diarrhea or coughs.
    - **Emergency Red Flag Protocol:** Patients exhibiting dyspnea, cyanosis, rust-colored sputum, hematochezia, or syncope are immediately directed to the nearest hospital emergency room.
    - **Not a Diagnostic Device:** This software is not certified for clinical diagnosis and does not substitute for evaluation by a licensed physician or Barangay Health Worker.
    """)


@st.dialog("Consultation Run History")
def show_history_dialog() -> None:
    recent_runs = list_recent_runs(limit=10)
    if not recent_runs:
        st.caption("No previous runs logged in evaluations/runs/.")
        return

    for r in recent_runs:
        ts = r.get("timestamp", "")[:19].replace("T", " ")
        complaint = r.get("chief_complaint", "")
        latency = r.get("metrics", {}).get("total_turnaround_ms", 0.0)
        status = r.get("status", "unknown")
        st.markdown(f"**{ts}** | Status: `{status}` | Latency: `{latency:.1f} ms`")
        st.caption(f"Query: {complaint[:90]}...")
        st.divider()


def main() -> None:
    init_session_state()

    # =========================================================================
    # Sidebar: Model Configuration & Hardware Diagnostics
    # =========================================================================
    st.sidebar.markdown('<div class="mono-eyebrow">SYSTEM CONFIGURATION</div>', unsafe_allow_html=True)
    
    mock_mode = st.sidebar.checkbox(
        "Offline Mock Mode (Testing & Demos)",
        value=True,
        help="Use deterministic in-memory provider for sub-50ms execution without local GPU requirements.",
    )

    ollama_ready = False
    if not mock_mode:
        provider = OllamaProvider()
        ollama_ready = provider.is_healthy()
        if ollama_ready:
            st.sidebar.markdown(
                '<div class="stat-chip"><span class="stat-label">DAEMON</span><span class="stat-val">ACTIVE (localhost:11434)</span></div>',
                unsafe_allow_html=True,
            )
            st.sidebar.caption("Models anchored on D:\\files\\ollama\\models")
        else:
            st.sidebar.markdown(
                '<div class="stat-chip"><span class="stat-label">DAEMON</span><span class="stat-val">UNREACHABLE</span></div>',
                unsafe_allow_html=True,
            )
            st.sidebar.caption("Notice: Run 'ollama serve' or enable Offline Mock Mode above.")
    else:
        st.sidebar.markdown(
            '<div class="stat-chip"><span class="stat-label">PROVIDER</span><span class="stat-val">MOCK (IN-MEMORY ~32ms)</span></div>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown('<div class="col-heading">MODEL ROUTING</div>', unsafe_allow_html=True)

    translation_model = st.sidebar.selectbox(
        "Translation Model (Stages 1 & 3)",
        options=["gemma4:e2b", "gemma4:e4b", "gemma2:2b"],
        index=0,
        help="Google DeepMind Gemma 4 (Cebuano NLU & NLG)",
    )

    medical_model = st.sidebar.selectbox(
        "Clinical Reasoning Model (Stage 2)",
        options=["alibayram/medgemma", "medgemma:4b"],
        index=0,
        help="Specialized MedGemma Clinical LLM for differential triage",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="mono-eyebrow">COURSE METADATA</div>', unsafe_allow_html=True)
    st.sidebar.caption("CS 5101 Natural Language Processing\nUniversity of San Carlos, Cebu\nInstructor: Dr. Vladimir Mariano\nAuthor: Gel (@gellyrslls)")

    # =========================================================================
    # Masthead: Title, Eyebrow & Control Bar
    # =========================================================================
    c_head_left, c_head_right = st.columns([3.2, 1.8])
    with c_head_left:
        st.markdown('<div class="mono-eyebrow">SEPTEMBER 2026 // CS 5101 NLP // DOKTOR SA SUGBO</div>', unsafe_allow_html=True)
        st.title("Cebuano Doctor: Doktor sa Sugbo")
        st.markdown(
            '<div class="masthead-sub">Gemma 4 NLU · MedGemma Clinical Reasoning · Gemma 4 NLG · 100% Local Air-Gapped</div>',
            unsafe_allow_html=True,
        )

    with c_head_right:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
        with c_btn1:
            if st.button("[Arch]", key="btn_arch_dialog", use_container_width=True, help="Inspect 3-stage circular architecture"):
                show_architecture_dialog()
        with c_btn2:
            if st.button("[Safety]", key="btn_safety_dialog", use_container_width=True, help="Review clinical protocol and disclaimer"):
                show_protocol_dialog()
        with c_btn3:
            if st.button("[Runs]", key="btn_runs_dialog", use_container_width=True, help="Review recent consultation logs"):
                show_history_dialog()
        with c_btn4:
            theme_btn_label = "[Dark]" if not is_dark else "[Light]"
            if st.button(theme_btn_label, key="btn_theme_toggle", use_container_width=True, help="Toggle between Light (White Coat) and Dark themes"):
                st.session_state.theme = "dark" if not is_dark else "light"
                st.rerun()

    # =========================================================================
    # Navigation Strip: 5 Authentic Peer Benchmark Personas
    # =========================================================================
    st.markdown('<div class="col-heading">METRO CEBU BENCHMARK PERSONAS // SELECT SCENARIO</div>', unsafe_allow_html=True)

    nav_cols = st.columns(5)
    for idx, persona in enumerate(BENCHMARK_PERSONAS):
        with nav_cols[idx]:
            is_active = (st.session_state.active_preset_key == persona["key"])
            if st.button(
                persona["button_label"],
                key=f"persona_btn_{persona['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_preset_key = persona["key"]
                st.session_state.chief_complaint = persona["chief_complaint"]
                st.rerun()

    # Find active persona configuration
    active_persona = next(
        (p for p in BENCHMARK_PERSONAS if p["key"] == st.session_state.active_preset_key),
        BENCHMARK_PERSONAS[0],
    )

    # =========================================================================
    # Hero Block & Protocol Banner
    # =========================================================================
    res = st.session_state.last_result
    if res and res.status != "error":
        stats_html = (
            f'<div class="stat-chip"><span class="stat-label">STAGE 01</span><span class="stat-val">{res.metrics.translation_en_ms:.1f} ms</span></div>'
            f'<div class="stat-chip"><span class="stat-label">STAGE 02</span><span class="stat-val">{res.metrics.medical_inference_ms:.1f} ms</span></div>'
            f'<div class="stat-chip"><span class="stat-label">STAGE 03</span><span class="stat-val">{res.metrics.translation_ceb_ms:.1f} ms</span></div>'
            f'<div class="stat-chip"><span class="stat-label">TOTAL</span><span class="stat-val">{res.metrics.total_turnaround_ms:.1f} ms</span></div>'
        )
    else:
        stats_html = (
            '<div class="stat-chip"><span class="stat-label">STAGE 01</span><span class="stat-val">GEMMA 4 NLU</span></div>'
            '<div class="stat-chip"><span class="stat-label">STAGE 02</span><span class="stat-val">MEDGEMMA</span></div>'
            '<div class="stat-chip"><span class="stat-label">STAGE 03</span><span class="stat-val">GEMMA 4 NLG</span></div>'
            '<div class="stat-chip"><span class="stat-label">AIR-GAP</span><span class="stat-val">100% OFFLINE</span></div>'
        )

    hero_html = (
        f'<div class="workout-hero">'
        f'<div>'
        f'<div class="mono-eyebrow">{active_persona["tag"]} // BENCHMARK CASE {active_persona["id"]}</div>'
        f'<div class="hero-title">{active_persona["name"]}: {active_persona["syndrome"]}</div>'
        f'<div class="hero-desc">{active_persona["persona"]}</div>'
        f'</div>'
        f'<div class="stat-chip-group">{stats_html}</div>'
        f'</div>'
        f'<div class="protocol-banner"><strong>Clinical Safety Protocol:</strong> {active_persona["guard"]}</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # =========================================================================
    # Patient Chief Complaint Input Area
    # =========================================================================
    st.markdown('<div class="col-heading">PATIENT CHIEF COMPLAINT (ISULAT ANG IMONG GIBATI)</div>', unsafe_allow_html=True)
    
    complaint_input = st.text_area(
        label="Enter patient symptoms in conversational Cebuano:",
        label_visibility="collapsed",
        value=st.session_state.chief_complaint,
        placeholder="Pananglit: 'Mura ko'g gipanuhot sa likod ug abaga human sa ulan, unya lipong akong ulo.'",
        height=110,
    )

    c_act1, c_act2, c_act3 = st.columns([2.5, 1, 3])
    with c_act1:
        run_consult = st.button(
            "[Sugdi ang Konsultasyon (Run Consultation)]",
            type="primary",
            use_container_width=True,
        )
    with c_act2:
        if st.button("[Clear Input]", use_container_width=True):
            st.session_state.chief_complaint = ""
            st.rerun()
    with c_act3:
        if mock_mode:
            st.caption("[MODE: OFFLINE MOCK] In-memory deterministic execution (<50 ms turnaround).")
        else:
            st.caption("[MODE: LIVE OLLAMA] Multi-stage local LLM execution via localhost daemon.")

    # =========================================================================
    # Pipeline Execution
    # =========================================================================
    if run_consult:
        clean_text = complaint_input.strip()
        if not clean_text:
            st.error("Chief complaint cannot be empty. Palihug pagsulat og reklamo sa panglawas.")
        else:
            st.session_state.chief_complaint = clean_text
            pipeline = get_pipeline(
                mock=mock_mode,
                translation_model=translation_model,
                medical_model=medical_model,
            )
            with st.spinner("Executing circular pipeline (Gemma 4 -> MedGemma -> Gemma 4)..."):
                consult_result = pipeline.run(clean_text)
                st.session_state.last_result = consult_result
                save_run(consult_result)

    # =========================================================================
    # Unrolled Consultation Results & Metrics
    # =========================================================================
    if st.session_state.last_result:
        result = st.session_state.last_result

        if result.status == "error":
            st.error(f"Consultation execution failed: {result.error_message}")
        else:
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            st.markdown('<div class="col-heading">EXECUTION PERFORMANCE & LATENCY BREAKDOWN</div>', unsafe_allow_html=True)
            
            # 4 native Streamlit metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("STAGE 01: CEBUANO NLU", f"{result.metrics.translation_en_ms:.1f} ms", "Gemma 4")
            m2.metric("STAGE 02: CLINICAL INFERENCE", f"{result.metrics.medical_inference_ms:.1f} ms", "MedGemma")
            m3.metric("STAGE 03: CEBUANO NLG", f"{result.metrics.translation_ceb_ms:.1f} ms", "Gemma 4")
            m4.metric("TOTAL TURNAROUND", f"{result.metrics.total_turnaround_ms:.1f} ms", "End-to-End")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown('<div class="col-heading">CIRCULAR PIPELINE STAGES (UNROLLED VIEW)</div>', unsafe_allow_html=True)

            # Unrolled Two-Column Body Grid: Stage 1 & Stage 2 side-by-side
            stage1_and_2_html = (
                f'<div class="ex-grid">'
                f'<div class="ex-card">'
                f'<div class="ex-card-header">'
                f'<div class="ex-card-title-group">'
                f'<span class="ex-index">01</span>'
                f'<span class="ex-name">Cebuano NLU & Clinical Grounding</span>'
                f'<span class="ex-scheme">{translation_model}</span>'
                f'</div>'
                f'<span class="stat-label">STAGE 01</span>'
                f'</div>'
                f'<div class="ex-card-body">'
                f'<div class="ex-meta-bar">'
                f'<span class="meta-chip"><span class="meta-label">SOURCE</span>Conversational Cebuano</span>'
                f'<span class="meta-chip"><span class="meta-label">TARGET</span>Clinical English</span>'
                f'<span class="meta-chip"><span class="meta-label">IDIOM</span>Contextualized</span>'
                f'</div>'
                f'<div class="col-heading">Clinical English Representation</div>'
                f'<div class="ex-instruction">{result.english_translation}</div>'
                f'<div class="callout-box">'
                f'<div class="guard-label">Cultural Contextualization</div>'
                f'Cultural metaphors grounded into objective clinical nomenclature for downstream reasoning.'
                f'</div>'
                f'</div>'
                f'</div>'
                f'<div class="ex-card">'
                f'<div class="ex-card-header">'
                f'<div class="ex-card-title-group">'
                f'<span class="ex-index">02</span>'
                f'<span class="ex-name">Clinical Medical Reasoning</span>'
                f'<span class="ex-scheme">{medical_model}</span>'
                f'</div>'
                f'<span class="stat-label">STAGE 02</span>'
                f'</div>'
                f'<div class="ex-card-body">'
                f'<div class="ex-meta-bar">'
                f'<span class="meta-chip"><span class="meta-label">DOMAIN</span>Evidence-Based</span>'
                f'<span class="meta-chip"><span class="meta-label">STEWARDSHIP</span>No Antibiotics</span>'
                f'<span class="meta-chip"><span class="meta-label">RED FLAGS</span>Screened</span>'
                f'</div>'
                f'<div class="col-heading">Evidence-Based Clinical Guidance</div>'
                f'<div class="ex-instruction">{result.english_medical_guidance}</div>'
                f'<div class="guard-box">'
                f'<div class="guard-label">Clinical Guard & Antimicrobial Stewardship</div>'
                f'Prohibits unindicated antibiotics. Supportive care only. Mandates emergency triage for red flags.'
                f'</div>'
                f'</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(stage1_and_2_html, unsafe_allow_html=True)

            # Unrolled Stage 3: Empathetic Cebuano Guidance Card
            stage3_html = (
                f'<div class="ex-card">'
                f'<div class="ex-card-header">'
                f'<div class="ex-card-title-group">'
                f'<span class="ex-index">03</span>'
                f'<span class="ex-name">Tambag sa Doktor: Empathetic Patient Guidance</span>'
                f'<span class="ex-scheme">{translation_model}</span>'
                f'</div>'
                f'<span class="stat-label">STAGE 03</span>'
                f'</div>'
                f'<div class="ex-card-body">'
                f'<div class="ex-meta-bar">'
                f'<span class="meta-chip"><span class="meta-label">LANGUAGE</span>Natural Sinugboanon</span>'
                f'<span class="meta-chip"><span class="meta-label">TONE</span>Empathetic & Supportive</span>'
                f'<span class="meta-chip"><span class="meta-label">TARGET</span>Patient & Family</span>'
                f'</div>'
                f'<div class="col-heading">Cebuano Patient Communication</div>'
                f'<div class="cebuano-guidance-text">{result.cebuano_medical_guidance}</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(stage3_html, unsafe_allow_html=True)

            # Render st.success for AppTest verification and copyable highlight
            st.success(f"Tambag sa Doktor (Stage 03 Guidance):\n\n{result.cebuano_medical_guidance}")

            # Structured Record Export
            st.markdown('<div class="col-heading">STRUCTURED CONSULTATION RECORD</div>', unsafe_allow_html=True)
            c_dl, c_info = st.columns([1.5, 3.5])
            with c_dl:
                st.download_button(
                    label="[Download Record (.json)]",
                    data=json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
                    file_name=f"consultation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with c_info:
                st.caption(f"Status: `{result.status}` | Latency: `{result.metrics.total_turnaround_ms:.1f} ms` | Timestamp: `{result.timestamp}`")


if __name__ == "__main__":
    main()
