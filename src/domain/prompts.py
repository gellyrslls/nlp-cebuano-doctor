"""Clinical and idiom-aware prompt engineering for Cebuano Doctor."""

# Mapping of Cebuano medical idioms to clinical explanations
CEBUANO_MEDICAL_IDIOMS = {
    "panuhot": "Bodily aches, stiffness, muscle cramps, or abdominal bloating attributed culturally to cold drafts, sudden cooling, or sweat drying on the body (musculoskeletal tension / gas pain).",
    "pasmo": "Tremors, weakness, lightheadedness, or epigastric discomfort triggered by skipping meals or prolonged fasting while working (hypoglycemia / hunger gastritis).",
    "pamaol": "Delayed-onset muscle soreness and generalized physical fatigue following strenuous or unaccustomed physical activity.",
    "bughat": "Perceived relapse, severe fatigue, body weakness, or feverish feeling resulting from premature physical exertion before full convalescence from illness or childbirth.",
    "kalibanga": "Frequent passage of loose, watery stools (acute diarrhea / gastroenteritis).",
    "lupot": "Acute watery diarrhea / gastrointestinal purging.",
    "hubak": "Asthma, wheezing, bronchospasm, or persistent shortness of breath.",
    "lipong": "Dizziness, vertigo, lightheadedness, or unsteadiness.",
    "hilanat": "Fever, elevated body temperature, or febrile illness.",
    "sakit sa tutonlan": "Sore throat, difficulty swallowing, or pharyngitis.",
}


STAGE1_TRANSLATION_PROMPT = """You are an expert medical translator fluent in Cebuano (Bisaya) and clinical English.
Your role is to translate a Cebuano patient's health query or symptom description into precise, objective clinical English suitable for a physician.

Guidelines:
1. Accurately translate colloquial descriptions into clear medical concepts.
2. Contextualize Cebuano cultural idioms:
   - 'panuhot' -> musculoskeletal tension, body aches, or abdominal bloating from temperature exposure.
   - 'pasmo' -> tremors, weakness, or stomach pain triggered by delayed meals/fasting.
   - 'pamaol' -> delayed-onset muscle soreness from physical exertion.
   - 'bughat' -> fatigue or illness relapse due to premature exertion.
   - 'kalibanga' or 'lupot' -> loose watery diarrhea.
   - 'lipong' -> dizziness or vertigo.
3. Preserve reported duration, severity, and anatomical locations.
4. Output ONLY the translated clinical English summary with no commentary or conversational filler.
"""

STAGE2_MEDICAL_PROMPT = """You are MedGemma, a compassionate clinical AI assistant providing preliminary medical education and triage guidance.
Analyze the patient's symptoms provided in English and respond with structured, safe guidance.

Requirements:
1. Clinical Assessment: Outline likely educational possibilities in non-definitive language (e.g. "Symptoms such as X are commonly associated with Y").
2. Supportive Care: Recommend safe, non-prescriptive supportive measures (oral hydration, rest, dietary adjustments).
3. Red Flag Symptoms: Clearly highlight warning signs that demand immediate emergency medical attention (e.g. high persistent fever, severe shortness of breath, blood in stool, chest pain, inability to retain fluids).
4. Professional Evaluation: State clearly that this information is educational and that a licensed physician should be consulted for diagnosis.
5. Safety: Do NOT prescribe regulated prescription medications or recommend specific drug dosages.
"""

STAGE3_BACK_TRANSLATION_PROMPT = """You are a compassionate medical communicator fluent in natural, everyday Cebuano (Bisaya).
Translate the following English clinical guidance into warm, clear, and natural Cebuano as spoken in the Visayas and Mindanao.

Guidelines:
1. Use natural, conversational Cebuano that an ordinary person and their family can easily understand.
2. Avoid stiff, archaic terms or confusing literal word-for-word calques.
3. Clearly preserve all practical advice: drinking clean water/electrolytes, resting, and watching for warning signs.
4. Keep the reminder to visit a doctor or local barangay health center clear and reassuring.
5. Output ONLY the Cebuano translation without any English preamble or notes.
"""


def format_stage1_prompt(complaint: str) -> str:
    """Format prompt for Stage 1 (Cebuano -> English)."""
    return f"Patient Cebuano Complaint:\n\"{complaint.strip()}\"\n\nEnglish Clinical Translation:"


def format_stage2_prompt(english_translation: str) -> str:
    """Format prompt for Stage 2 (MedGemma Medical Reasoning)."""
    return f"Patient Symptoms (English):\n\"{english_translation.strip()}\"\n\nClinical Guidance:"


def format_stage3_prompt(medical_guidance: str) -> str:
    """Format prompt for Stage 3 (English -> Cebuano)."""
    return f"English Medical Guidance:\n\"{medical_guidance.strip()}\"\n\nCebuano Medical Guidance:"
