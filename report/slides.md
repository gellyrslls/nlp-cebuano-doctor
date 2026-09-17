---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #fafafa
color: #18181b
style: |
  section {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    padding: 36px 54px;
    background-color: #fafafa;
    color: #18181b;
  }
  h1 { color: #18181b; font-weight: 800; letter-spacing: -0.02em; }
  h2 { color: #18181b; font-weight: 800; border-bottom: 1px solid #e4e4e7; padding-bottom: 8px; }
  table { font-size: 0.65rem; line-height: 1.35; border-collapse: collapse; width: 100%; }
  th { background-color: #f4f4f5; color: #71717a; font-family: ui-monospace, monospace; text-transform: uppercase; border-bottom: 1px solid #d4d4d8; }
  td { border-bottom: 1px solid #e4e4e7; color: #52525b; }
  .badge { background: #f4f4f5; color: #18181b; border: 1px solid #d4d4d8; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-family: ui-monospace, monospace; }
  .mono { font-family: ui-monospace, monospace; }
  .disclaimer { font-size: 0.72rem; color: #52525b; border-left: 3px solid #d4d4d8; padding-left: 12px; background: #ffffff; }
---

# The Cebuano Doctor (Doktor sa Sugbo)
### Three-Stage Circular Translation and Clinical Reasoning Pipeline

**Course:** CS 5101: Natural Language Processing, 1st Semester 2026-2027  
**Institution:** University of San Carlos (USC), Cebu City, Philippines  
**Instructor:** Dr. Vladimir Mariano  
**Authors / Presenters:** Angelo Rosillosa and Liam Jones ([@gellyrslls](https://github.com/gellyrslls))  
**Repository:** [github.com/gellyrslls/nlp-cebuano-doctor](https://github.com/gellyrslls/nlp-cebuano-doctor.git)  
**Submission Date:** September 17, 2026 | **Presentation Date:** September 18, 2026  

---

## 1. Executive Summary and Problem Statement

* **The Clinical Reality:** In the Visayas, patients describe physical distress through culture-bound illness categories (*panuhot*, *pasmo*, *kabuhi*, *pamaol*, *lupot*, *bughat*, *pamalaybalay*).
* **The Model Dilemma:** Frontier clinical LLMs like Google DeepMind's **MedGemma** are trained overwhelmingly on English biomedical literature and international clinical guidelines.
* **The Failure of Direct Prompting:** Feeding raw Cebuano into English clinical models causes semantic loss, hallucinated triage, or missed emergency red flags.
* **The Solution:** A local-first, privacy-preserving **3-stage circular pipeline**:
  1. $\text{Cebuano Chief Complaint} \xrightarrow{\text{NLU via Gemma 4}} \text{Clinical English Summary}$
  2. $\text{Clinical English Summary} \xrightarrow{\text{Inference via MedGemma}} \text{Evidence-Based Guidance}$
  3. $\text{Evidence-Based Guidance} \xrightarrow{\text{NLG via Gemma 4}} \text{Empathetic Cebuano Advice}$

---

## 2. Technical Architecture: Circular Medical Pipeline

```
+-----------------------------------------------------------------------------+
|                       PATIENT (Cebuano Speaker)                             |
|         "Bay, grabeha na gyud aning labad sa akong ulo... sa TC library"    |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 1: Natural Language Understanding (NLU) via Gemma 4 (gemma4:e2b)      |
| Preserves cultural idiom context: "bakos sa agtang" -> tension headache     |
| Output: "Patient presents with severe circumferential band-like tension..." |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 2: Clinical Medical Reasoning (Inference) via MedGemma (alibayram)    |
| Differential assessment, supportive care (20-20-20 rule), antimicrobial     |
| stewardship (prohibit ciprofloxacin/leftover drugs), emergency red flags    |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 3: Natural Language Generation (NLG) via Gemma 4 (gemma4:e2b)         |
| Empathetic back-translation into warm, accessible, natural Sinugboanon      |
| Output: "Base sa imong gipamati, nagpakita kini og tension headache..."     |
+-----------------------------------------------------------------------------+
```

---

## 3. Privacy, Local Execution, and Hardware Rationale

Dr. Mariano emphasized two primary real-world imperatives: **Data Privacy** and **Zero Token Costs**.

* **100% Offline Air-Gapped Execution:**
  * Powered locally by **Ollama daemon** (`localhost:11434`).
  * Runs with Wi-Fi disabled: zero patient telemetry or sensitive health data leaves the machine.
* **Storage and Hardware Architecture:**
  * Ollama model repository permanently configured on SSD secondary partition (`D:\files\ollama\models`).
  * Protected Windows C: drive partition (~4.6 GB free) from model storage exhaustion.
  * Successfully executes quantized Gemma 4 (7.2 GB) and MedGemma (2.5 GB) on 16 GB RAM + 4 GB VRAM.
* **Dual Execution Paths:**
  * **Live Mode:** Real local LLM multi-stage reasoning (~3.5 min end-to-end CPU/GPU turnaround).
  * **Mock Mode:** Instant sub-50ms deterministic testing for rapid UI/CLI demonstrations and regression suites.

---

## 4. Linguistic Nuance and Idiom Grounding: "Lost in Translation"

Generic LLMs fail when translating regional illness categories. The Cebuano Doctor system prompt provides explicit clinical anchoring:

| Cebuano Cultural Idiom | Generic Translation (Failure Mode) | Cebuano Doctor Clinical Contextualization |
| :--- | :--- | :--- |
| ***Panuhot*** | *"Wind inside the body / flatulence"* | **Musculoskeletal spasm, thoracic trigger points, and stiffness from cold draft/rain** |
| ***Pasmo*** | *"Spasm / seizure / convulsion"* | **Fasting hypoglycemia, hand tremors, cold sweats, and hunger gastritis from delayed meals** |
| ***Kabuhi*** | *"Life / soul"* | **Epigastric visceral fluttering, hypermotility, or acid reflux surging toward throat** |
| ***Kalibanga / Lupot*** | Generic stomach ache | **Acute watery diarrhea demanding immediate Oral Rehydration Salts (ORS)** |
| ***Pamalaybalay*** | *"House building"* | **Hyperactive borborygmi, loud peristalsis, and spasmodic colic before loose bowel movements** |
| ***Tayaon nga plema*** | *"Rusty saliva"* | **Purulent, rust-colored sputum indicating lower respiratory consolidation / pneumonia** |
| ***Bakos sa agtang*** | *"Belt on forehead"* | **Circumferential band-like tension headache exacerbated by visual fatigue/screen study** |
| ***Pamaol*** | *"Chronic joint arthritis"* | **Delayed-onset muscle soreness (DOMS) and fatigue following strenuous physical exertion** |
| ***Hilanat / Ubo*** | *"General weakness"* | **Elevated body temperature (>38.5 deg C) and productive cough requiring clinical triage** |

---

## 5. Dual-Interface Application Design

The system implements two independent, decoupled presentation layers:

1. **Interactive Rich Terminal CLI (`python -m src.cli`):**
   * High-contrast ANSI formatted panels for Chief Complaint, Stage 1, Stage 2, and Stage 3.
   * Live latency breakdown performance tables.
   * Preset scenario selector (`--preset 1-5`) and offline mock flag (`--mock`).
   * Continuous REPL interactive loop for patient dialogue.

2. **Streamlit Web Application (`streamlit run app.py`):**
   * Single-page responsive layout with Tailwind Zinc developer aesthetic defaulting to Light Mode (white coat).
   * 5 one-click benchmark persona presets (USC TC Library, Carcar Aunt, IT Park BPO, Pungko-pungko, SRP Site).
   * Clear input button and instant toggle between Offline Mock Mode and Live Ollama Daemon.
   * Unrolled Stage 1, Stage 2, and Stage 3 cards showing intermediate representations and JSON run export.

---

## 6. Evaluation Methodology: 4-Axis Quality Matrix

Per Dr. Mariano's rubric, 5 diverse authentic clinical scenarios were evaluated across 4 core axes:

1. **Translation Fidelity (Cebuano to English NLU):** Did Gemma 4 accurately disambiguate colloquial idioms, symptom severity, duration, and anatomical locations?
2. **Clinical Medical Soundness (MedGemma Inference):** Is the advice medically sound, free of hallucinations, non-prescriptive, compliant with antimicrobial stewardship, and triaged with red flags?
3. **Cultural Naturalness (English to Cebuano NLG):** Is the back-translation warm, accessible, and empathetic to ordinary Cebuano-speaking families without medicalized jargon?
4. **Quantitative Latency and Performance:** Per-stage millisecond timings and total turnaround on local hardware (comparing live Ollama vs mock mode).

---

## 7. The 5 Authentic Peer Benchmark Personas

Derived from primary peer interviews and clinical NLP benchmarks across Metro Cebu:

| ID | Persona and Location | Cebuano Chief Complaint (Prompt) | Clinical Syndrome |
| :--- | :--- | :--- | :--- |
| **01** | **3rd-Yr BS Civil Eng.**  <br>*USC TC Library* | *"Bay, grabeha na gyud aning labad sa akong ulo... mura bitaw'g gipugos og bakos akong agtang sa kahuot, nya magsakit pud akong mata..."* | Digital Asthenopia and Tension Headache (20-20-20 rule) |
| **02** | **52-Yr-Old Aunt**  <br>*Carcar City, Cebu* | *"Dong, maayong hapon... kining akong abaga ug likod mura man gud og gipanuhot... nanikig gyud akong liog unya dunay bukol-bukol sa gusok..."* | Thoracic Myofascial Trigger Spasm ("Panuhot") |
| **03** | **24-Yr-Old BPO Agent**  <br>*Cebu IT Park, Apas* | *"Doc, nag-night shift man gud ko sa IT Park, sige ra ko'g laktaw-laktaw og kaon... mura na gyud ko'g gipasmo kay nagkurog akong kamot, nagkabuhi..."* | Fasting Hypoglycemia and Hyperacidic Gastritis ("Pasmo") |
| **04** | **21-Yr-Old BS Nursing**  <br>*Fuente Osmena* | *"Doc, sukad gabii pagkahuman nakog kaon sa pungko-pungko, gikalibanga na gyud ko... pamalaybalay sa tiyan. Mag-start na ba ko'g ciprofloxacin?"* | Acute Watery Gastroenteritis (ORS and No Antibiotics) |
| **05** | **28-Yr-Old Safety Lead**  <br>*SRP Reclamation Site* | *"Doc, hapit na 2 ka semana kining akong ubo nga walay lurang-lurang... 39.2 deg C akong hilanat... plema tayaon, unya gidunggab og kutsilyo akong dughan..."* | Community-Acquired Pneumonia and Pleurisy (Emergency) |

---

## 8. Benchmark Evaluation Results Matrix

| Scenario | NLU Fidelity (Gemma 4) | Clinical Soundness (MedGemma) | NLG Quality (Gemma 4) | Safety & Stewardship |
| :--- | :--- | :--- | :--- | :---: |
| **01: TC Library** | Correctly parsed 'bakos sa agtang' and eye strain | Advised 20-20-20 rule, hydration, darkness, paracetamol | Natural, comforting advice in relatable Cebuano | `[PASS]` |
| **02: Carcar Aunt** | Mapped 'panuhot' and 'lusay-lusay' to myofascial spasms | Recommended warm compress and safe ginger-oil rub; no deep force | Respectful, warm Sinugboanon tone | `[PASS]` |
| **03: IT Park BPO** | Disambiguated 'pasmo' and 'kabuhi' to hypoglycemia | Urgent complex carbs/protein, cut energy drinks, frequent meals | Practical shift-worker guidance | `[PASS]` |
| **04: Pungko-pungko** | Classified acute diarrhea and parsed 'pamalaybalay' | **Antimicrobial Stewardship:** Strictly prohibited ciprofloxacin; prioritized ORS | Clear warning against antibiotics | `[PASS]` |
| **05: SRP Pneumonia** | Identified 'tayaon' (rust sputum) and 39.2 deg C fever | Prohibited leftover antibiotics; emergency hospital and chest X-ray | Urgent directive to proceed to Emergency Room | `[PASS]` |

---

## 9. Latency Performance: Live Ollama vs. Offline Mock

Execution performance was comprehensively profiled on local hardware:

| Performance Metric | Live Ollama Daemon (`D:\files\ollama`) | Offline Mock Provider (`--mock`) |
| :--- | :---: | :---: |
| **Execution Environment** | Local Laptop CPU / GPU (4 GB VRAM) | In-Memory Deterministic Pipeline |
| **Stage 1: NLU Translation** | ~35,200 ms (35.2 s) | **10.7 ms** |
| **Stage 2: Clinical Reasoning** | ~89,500 ms (89.5 s) | **10.6 ms** |
| **Stage 3: Cebuano NLG** | ~91,100 ms (91.1 s) | **11.0 ms** |
| **Total Turnaround Time** | **~215,800 ms (3.6 min)** | **32.3 ms** |
| **Network and Privacy** | **100% Offline (Air-Gapped)** | **100% Offline (Air-Gapped)** |
| **Clinical Safety Pass Rate** | **100.0% (5/5 PASS)** | **100.0% (5/5 PASS)** |

---

## 10. Medical Safety and Antimicrobial Stewardship

Medical hallucinations and improper self-medication are dangerous. Our system enforces strict safety guardrails:

* **Antimicrobial Stewardship:**
  * When patients ask about taking antibiotics (e.g., ciprofloxacin for *pungko-pungko* diarrhea, or leftover amoxicillin for cough), the pipeline **strictly prohibits** self-administered antibiotics.
  * Educates patients that indiscriminate antibiotics cause dangerous resistance, disrupt gut flora, and fail on viral pathogens.
* **Triage vs. Prescription Separation:**
  * System prompts prohibit prescribing regulated drugs or calculating dosages.
  * Recommends evidence-backed supportive care (ORS, rest, hydration, 20-20-20 rule).
* **Mandatory Red Flag Surveillance:**
  * Explicitly screens for alarming signs: dyspnea, cyanosis, rust sputum, hematochezia, syncope, and thunderclap headache.
* **Universal Professional Disclaimer:**
  * Every consultation reinforces that the tool is educational and urges consultation with a licensed physician or Barangay Health Worker.

---

## 11. Engineering Discipline and TDD Methodology

Following industry best practices and our repo rules:

* **Test-Driven Development (TDD):**
  * Red to Green vertical slices: tests written before every implementation module.
  * Zero tests written against internal private methods; tested strictly through public seams (`CebuanoDoctorPipeline`, `save_run`, `parse_args`, `AppTest`).
* **Test Suite Metrics:**
  * **43 Passing Tests** across 8 test modules:
    * `test_pipeline.py`: Circular orchestration, custom query fallbacks, latency metrics, error recovery.
    * `test_prompts.py`: Cultural idiom formatting, clinical translation prompts.
    * `test_ollama_provider.py`: Daemon connection, offline error handling.
    * `test_storage.py`: JSON run artifact persistence, slug sanitization.
    * `test_cli.py`: Argument parser, preset scenarios, Rich card rendering.
    * `test_ui.py`: Streamlit AppTest integration and interaction flow.
    * `test_evaluate.py`: Benchmark runner, KPI calculations, safety rule evaluation.
    * `test_report.py`: Slide deck and PDF presentation verification.
* **Conventional Commits:** Clean, semantic commit history on GitHub main branch.

---

## 12. Deployment Vision: Rural Barangay Health Stations

Dr. Mariano challenged us to consider real-world deployment on edge hardware:

```
+-----------------------------------------------------------------------------+
|               BARANGAY HEALTH STATION (BHS) / RURAL CLINIC                  |
|                     (No Internet / Mountain Barangay)                       |
+-----------------------------------------------------------------------------+
|                                                                             |
|   +------------------------+            +-------------------------------+   |
|   |   Patient / Resident   |            |   Barangay Health Worker      |   |
|   |   (Speaks Cebuano)     |            |   (BHW Triage Assistant)      |   |
|   +-----------+------------+            +---------------+---------------+   |
|               |                                         |                   |
|               v                                         v                   |
|   +---------------------------------------------------------------------+   |
|   |   Local Edge Device (Raspberry Pi 5 / Jetson Orin Nano / Mini-PC)   |   |
|   |   - Ollama Local Daemon + Gemma 4 + MedGemma (Quantized GGUF)       |   |
|   |   - Zero Internet Required | Local SQLite / JSON Run Archive        |   |
|   |   - Touchscreen Kiosk UI or Local Wi-Fi Hotspot Portal              |   |
|   +---------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------+
```

---

## 13. Key Learnings and Course Reflections

1. **NLU Is Far More Difficult Than NLG for Regional Languages:**
   Translating informal colloquial Cebuano (*"mura ko'g gipanuhot"*, *"pamalaybalay"*, *"nagkabuhi"*) requires deep cultural semantics that generic models misunderstand without specialized system prompt framing.
2. **The Power of Local Model Distillation:**
   Frontier models distilled into compact 2B/4B parameters enable real-world, privacy-preserving AI on accessible consumer laptops without expensive cloud infrastructure.
3. **The Importance of the Circular Seam:**
   Single-pass black-box chatbots conceal errors. Circular translation makes the reasoning transparent, verifiable, and auditable at every stage.
4. **Antimicrobial Stewardship Is Critical in Low-Resource Triage:**
   Community chatbots must actively discourage over-the-counter and leftover antibiotic misuse rather than simply remaining silent.
5. **Engineering Rigor Matters:**
   Building structured automated tests, CLI tools, and reproducible evaluation benchmarks turns an academic prototype into a production-ready portfolio project.

---

## 14. Deliverables and Verification Links

* **GitHub Repository:**  
  [https://github.com/gellyrslls/nlp-cebuano-doctor.git](https://github.com/gellyrslls/nlp-cebuano-doctor.git)
* **Codebase Deliverables:**
  * Core Seam & Pipeline: [`src/domain/pipeline.py`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/src/domain/pipeline.py)
  * Rich Terminal Runner: [`src/cli.py`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/src/cli.py)
  * Streamlit Web Application: [`app.py`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/app.py)
  * Automated 5-Prompt Benchmark: [`src/evaluate.py`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/src/evaluate.py)
  * Benchmark Report: [`evaluations/benchmark_report.md`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/evaluations/benchmark_report.md)
  * Presentation Slide Deck: [`report/slides.md`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/report/slides.md)
  * Printable HTML Presentation Report: [`report/presentation_report.html`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/report/presentation_report.html)
  * Print-Ready Slide Deck PDF: [`report/presentation_report.pdf`](file:///C:/Users/angel/OneDrive/Desktop/nlp-cebuano-doctor/report/presentation_report.pdf)
  * 43 Automated Tests: `python -m pytest tests` (100% passing)

---

# Daghang Salamat!
### Questions and Academic Discussion

**CS 5101: Natural Language Processing: University of San Carlos**  
*The Cebuano Doctor: Local, Privacy-Preserving Healthcare AI for the Visayas*
