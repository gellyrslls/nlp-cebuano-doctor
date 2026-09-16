# Cebuano Doctor

A local, privacy-preserving 3-stage translation and clinical guidance pipeline designed to handle Cebuano cultural illness idioms.

## Pipeline Architecture

Frontier clinical models (MedGemma) are trained on English medical texts and fail when prompted directly with colloquial Cebuano idioms. This system decouples language understanding, clinical reasoning, and back-translation:

```text
Cebuano Chief Complaint  -->  [Stage 1: NLU (Gemma 4)]     --> Clinical English Description
Clinical English         -->  [Stage 2: Inference (MedGemma)] --> Triage & Supportive Advice
English Advice           -->  [Stage 3: NLG (Gemma 4)]     --> Natural Cebuano Guidance
```

---

## Repository Layout

```text
├── app.py                   # Streamlit interactive web application
├── src/
│   ├── domain/              # Core business logic & architecture seam
│   │   ├── pipeline.py      # CebuanoDoctorPipeline (primary execution seam)
│   │   ├── provider.py      # ModelProvider protocol & MockModelProvider
│   │   ├── models.py        # ConsultationResult & StageMetrics dataclasses
│   │   └── prompts.py       # Stage 1, 2, 3 prompts & cultural idiom definitions
│   ├── providers/           # Concrete infrastructure adapters
│   │   └── ollama_provider.py # OllamaProvider (local HTTP daemon client)
│   ├── cli.py               # Rich terminal REPL and stage-by-stage inspection
│   ├── doctor.py            # Environment, storage, and GPU diagnostics
│   ├── evaluate.py          # 5-scenario evaluation runner with automated safety grading
│   ├── storage.py           # Structured JSON run artifact persistence
│   └── ui_helpers.py        # Preset complaint catalog and pipeline factory
├── evaluations/
│   ├── benchmark_report.md  # Generated evaluation matrix and qualitative analysis
│   └── runs/                # Persisted consultation logs (<timestamp>_<slug>.json)
├── tests/                   # 40 automated unit, seam, and UI integration tests
└── CONTEXT.md               # Canonical domain glossary and vocabulary rules
```

---

## Core Architecture Seam

All interfaces (CLI, Web UI, and Evaluation runner) interact through a single decoupled seam:

```python
from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider

# 1. Initialize pipeline with injectable provider (MockModelProvider or OllamaProvider)
pipeline = CebuanoDoctorPipeline(
    provider=MockModelProvider(),
    translation_model="gemma4:e2b",
    medical_model="alibayram/medgemma",
)

# 2. Execute 3-stage circular consultation
result = pipeline.run("Gisakit akong tiyan unya gikalibanga ko.")

# 3. Access structured results, intermediate stages, and metrics
print(result.english_translation)       # Stage 1 (NLU)
print(result.english_medical_guidance)  # Stage 2 (MedGemma)
print(result.cebuano_medical_guidance)  # Stage 3 (NLG)
print(result.metrics.total_turnaround_ms)
```

Every run automatically serializes a complete JSON execution record into `evaluations/runs/<timestamp>_<slug>.json`.

---

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

### 2. Offline Mock Mode (Instant Testing & Demos)

Runs immediately on CPU without GPU, Ollama, or downloading model weights:

```bash
# Interactive Rich terminal REPL
python -m src.cli --mock

# Single Chief Complaint execution
python -m src.cli --mock --chief-complaint "Mura ko'g gipanuhot sa likod"

# Selective stage inspection (e.g., inspect only Stage 1 NLU translation)
python -m src.cli --mock --chief-complaint "Gisakit akong ulo" --stages 1

# Interactive Streamlit Web UI
streamlit run app.py

# 5-scenario evaluation runner with automated safety grading
python -m src.evaluate --mock
```

### 3. Live Local Ollama Inference

Prerequisites: [Ollama](https://ollama.com/) running locally:

```bash
# Pull model weights
ollama pull gemma4:e2b
ollama pull alibayram/medgemma

# Verify local daemon, GPU, and model storage
python -m src.doctor

# Launch terminal runner against live models
python -m src.cli

# Launch web application (uncheck "Offline Mock Mode" in sidebar)
streamlit run app.py

# Run live benchmark evaluation report
python -m src.evaluate --output evaluations/benchmark_report.md
```

---

## Testing

The test suite covers public interfaces, seam integration, UI components, and safety evaluation:

```bash
# Run all 40 automated tests
python -m pytest

# Run specific test suites
python -m pytest tests/test_pipeline.py    # Core circular pipeline & auto-persistence
python -m pytest tests/test_cli.py         # Terminal CLI argument parsing & stage flags
python -m pytest tests/test_ui.py          # Streamlit UI AppTest integration
python -m pytest tests/test_evaluate.py    # Safety grading & benchmark evaluation
```

---

## Domain Documentation

- [CONTEXT.md](CONTEXT.md): Canonical domain vocabulary, avoided synonyms, and Cebuano idiom definitions.
- [docs/adr/0001-circular-pipeline-architecture.md](docs/adr/0001-circular-pipeline-architecture.md): Architectural Decision Record detailing the 3-stage circular decoupling.
