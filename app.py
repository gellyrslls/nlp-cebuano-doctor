"""Streamlit Web UI for Cebuano Doctor Circular Medical NLP Pipeline."""
import json
import streamlit as st
from datetime import datetime

from src.ui_helpers import SAMPLE_PROMPTS, get_pipeline, list_recent_runs
from src.providers.ollama_provider import OllamaProvider
from src.storage import save_run


st.set_page_config(
    page_title="Cebuano Doctor | Doktor sa Sugbo",
    page_icon="🩺",
    layout="wide",
)


def init_session_state() -> None:
    """Initialize session state variables."""
    if "chief_complaint" not in st.session_state:
        st.session_state.chief_complaint = ""
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def main() -> None:
    init_session_state()

    # Sidebar: Model Configuration & Diagnostics
    st.sidebar.title("🩺 Configuration")
    mock_mode = st.sidebar.checkbox(
        "Offline Mock Mode (Testing & Demos)",
        value=True,
        help="Use deterministic mock model provider for fast local testing without GPU/Ollama.",
    )

    ollama_ready = False
    if not mock_mode:
        provider = OllamaProvider()
        ollama_ready = provider.is_available()
        if ollama_ready:
            st.sidebar.success("✅ Ollama daemon online (localhost:11434)")
        else:
            st.sidebar.error("❌ Ollama daemon unreachable. Start Ollama or enable Mock Mode.")

    translation_model = st.sidebar.selectbox(
        "Translation Model (Stages 1 & 3)",
        options=["gemma4:e2b", "gemma4:e4b", "gemma2:2b"],
        index=0,
    )

    medical_model = st.sidebar.selectbox(
        "Clinical Reasoning Model (Stage 2)",
        options=["alibayram/medgemma", "medgemma:4b"],
        index=0,
    )

    # Sidebar History Expander
    with st.sidebar.expander("📁 Recent Consultation Runs", expanded=False):
        recent_runs = list_recent_runs(limit=8)
        if not recent_runs:
            st.caption("No previous runs found.")
        else:
            for r in recent_runs:
                ts = r.get("timestamp", "")[:19].replace("T", " ")
                query = r.get("chief_complaint", "")
                st.markdown(f"**{ts}**\n*{query[:40]}...*")
                st.caption(f"Latency: {r.get('metrics', {}).get('total_turnaround_ms', 0):.1f} ms")
                st.divider()

    # Main Header & Academic Disclaimer
    st.title("🩺 Cebuano Doctor (Doktor sa Sugbo)")
    st.caption("CS 5101: Natural Language Processing — Three-Stage Circular Translation & Medical Reasoning Pipeline")

    st.warning(
        "⚠️ **Academic AI Disclaimer**: This tool is an academic research prototype developed for CS 5101 NLP. "
        "It provides preliminary educational guidance only and is **NOT** a certified medical device or a substitute "
        "for clinical evaluation by a licensed healthcare professional. In an emergency, proceed to the nearest hospital."
    )

    # Sample Preset Selectors
    st.markdown("### 💡 Sample Cebuano Health Queries")
    col_presets = st.columns(3)
    preset_keys = list(SAMPLE_PROMPTS.keys())
    
    for i, key in enumerate(preset_keys):
        col_idx = i % 3
        with col_presets[col_idx]:
            if st.button(key, key=f"btn_preset_{i}", use_container_width=True):
                st.session_state.chief_complaint = SAMPLE_PROMPTS[key]

    # Input Area
    st.markdown("### 📝 Isulat ang Imong Gibati (Chief Complaint)")
    user_query = st.text_area(
        "Enter patient symptoms in conversational Cebuano:",
        value=st.session_state.chief_complaint,
        placeholder="Pananglit: 'Mura ko'g gipanuhot sa likod ug abaga human sa ulan, unya lipong akong ulo.'",
        height=110,
    )

    col_action, _ = st.columns([2, 5])
    with col_action:
        run_button = st.button("🚀 Sugdi ang Konsultasyon (Run Consultation)", type="primary", use_container_width=True)

    if run_button:
        query_text = user_query.strip()
        if not query_text:
            st.error("Palihug pagsulat og reklamo sa panglawas (Chief complaint cannot be empty).")
        else:
            pipeline = get_pipeline(
                mock=mock_mode,
                translation_model=translation_model,
                medical_model=medical_model,
            )
            with st.spinner("Naglutos sa 3-stage circular pipeline (Gemma 4 -> MedGemma -> Gemma 4)..."):
                result = pipeline.run(query_text)
                st.session_state.last_result = result
                save_run(result)

    # Render Consultation Results if available
    if st.session_state.last_result:
        result = st.session_state.last_result

        if result.status == "error":
            st.error(f"❌ Consultation failed: {result.error_message}")
        else:
            st.markdown("---")
            st.subheader("📊 Execution Performance & Latency")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Stage 1: NLU Translation", f"{result.metrics.translation_en_ms:.1f} ms", "Gemma 4")
            m2.metric("Stage 2: Clinical Reasoning", f"{result.metrics.medical_inference_ms:.1f} ms", "MedGemma")
            m3.metric("Stage 3: Cebuano NLG", f"{result.metrics.translation_ceb_ms:.1f} ms", "Gemma 4")
            m4.metric("Total Turnaround", f"{result.metrics.total_turnaround_ms:.1f} ms", "End-to-End")

            st.markdown("---")
            st.subheader("🩺 Circular Pipeline Breakdown")

            # Final Cebuano Medical Guidance (Prominent Stage 3 Card)
            st.markdown("#### 🌺 Stage 3: Tambag sa Doktor (Final Cebuano Guidance)")
            st.success(result.cebuano_medical_guidance)

            # Intermediate Stage Cards
            with st.expander("🔍 Inspect Stage 1: Cebuano → Clinical English Translation (Gemma 4)", expanded=True):
                st.info(result.english_translation)

            with st.expander("🔍 Inspect Stage 2: MedGemma Clinical Medical Reasoning (English)", expanded=True):
                st.info(result.english_medical_guidance)

            # Download Artifact JSON
            st.download_button(
                label="📥 Download Structured Consultation Log (.json)",
                data=json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
                file_name=f"consultation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )


if __name__ == "__main__":
    main()
