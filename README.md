# Cebuano Doctor

A local, privacy-preserving 3-stage translation and clinical guidance pipeline designed to handle Cebuano cultural illness idioms.

## Pipeline Architecture

Frontier clinical models (MedGemma) are trained on English medical texts and fail when prompted directly with colloquial Cebuano idioms. This system decouples language understanding, clinical reasoning, and back-translation:

```text
Cebuano Complaint  -->  [Stage 1: NLU (Gemma)]          --> Clinical English Description
Clinical English   -->  [Stage 2: Inference (MedGemma)] --> Triage & Supportive Advice
English Advice     -->  [Stage 3: NLG (Gemma)]          --> Natural Cebuano Guidance
```

## Cultural Idioms Handled

| Cebuano Idiom         | Generic Translation Failure         | Clinical Grounding                                                          |
| :-------------------- | :---------------------------------- | :-------------------------------------------------------------------------- |
| **Panuhot**           | "Wind trapped in body" / Flatulence | Musculoskeletal tension or spasm attributed to cold drafts or sweat.        |
| **Pasmo**             | "Spasm" / Convulsion                | Mild hypoglycemia, tremors, and gastric pain from skipped meals.            |
| **Kalibanga / Lupot** | Generic stomach ache                | Acute watery diarrhea requiring Oral Rehydration Salts (ORS).               |
| **Pamaol**            | Arthritis / Systemic illness        | Delayed-Onset Muscle Soreness (DOMS) from heavy physical exertion.          |
| **Bughat**            | Depressive relapse                  | Fatigue or illness relapse triggered by premature exertion during recovery. |
| **Lipong**            | General weakness                    | Dizziness, vertigo, lightheadedness, or postural instability.               |

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/gellyrslls/nlp-cebuano-doctor.git
cd nlp-cebuano-doctor
python -m pip install -r requirements.txt
```

### 2. Run in Offline Mock Mode (No GPU or Model Downloads Required)

```bash
# Terminal CLI with live latency timers
python -m src.cli --mock

# Interactive Streamlit Web UI
streamlit run app.py

# 5-Prompt Automated Evaluation Benchmark
python -m src.evaluate --mock --output evaluations/benchmark_report.md
```

### 3. Run with Live Local Ollama Models

Prerequisites: [Ollama](https://ollama.com/) running locally with models pulled:

```bash
ollama pull gemma4:e2b
ollama pull alibayram/medgemma

python -m src.doctor      # Verify environment and storage
python -m src.cli         # Launch interactive terminal runner
```

---

## Testing

```bash
python -m pytest tests
```

---
