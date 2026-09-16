# 0001: Three-Stage Circular Translation and Medical Reasoning Pipeline

Status: accepted

## Context
Patients seek medical guidance using colloquial Cebuano and regional cultural idioms, while state-of-the-art specialized open medical models (MedGemma) are trained predominantly on English clinical literature and guidelines. Direct end-to-end Cebuano prompts to medical models obscure where translation errors versus clinical hallucinations occur.

## Decision
We implement a three-stage circular pipeline:
1. Translate Cebuano Chief Complaint to English using Gemma 4.
2. Generate English Medical Guidance using MedGemma.
3. Translate English Medical Guidance back to Cebuano using Gemma 4.

Each stage is decoupled, timed independently, and persisted in structured JSON run logs alongside an interactive dual-interface (Rich CLI and Streamlit Web UI). An injectable mock provider is included to allow deterministic offline testing.

## Consequences
- Every stage can be measured and evaluated separately for linguistic accuracy, clinical soundness, and latency.
- Introduces latency overhead across two translation steps compared to single-pass inference.
- Eliminates cloud token costs and protects patient privacy by running entirely on local hardware via Ollama.
