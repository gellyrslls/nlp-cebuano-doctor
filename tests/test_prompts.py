"""Unit tests for prompt formatting and idiom mapping."""
import unittest
from src.domain.prompts import (
    CEBUANO_MEDICAL_IDIOMS,
    STAGE1_TRANSLATION_PROMPT,
    STAGE2_MEDICAL_PROMPT,
    STAGE3_BACK_TRANSLATION_PROMPT,
    format_stage1_prompt,
    format_stage2_prompt,
    format_stage3_prompt,
)


class TestPrompts(unittest.TestCase):
    def test_cultural_idioms_present(self):
        assert "panuhot" in CEBUANO_MEDICAL_IDIOMS
        assert "pasmo" in CEBUANO_MEDICAL_IDIOMS
        assert "pamaol" in CEBUANO_MEDICAL_IDIOMS
        assert "bughat" in CEBUANO_MEDICAL_IDIOMS
        assert "kalibanga" in CEBUANO_MEDICAL_IDIOMS

    def test_stage1_system_prompt_mentions_idioms(self):
        prompt_lower = STAGE1_TRANSLATION_PROMPT.lower()
        assert "panuhot" in prompt_lower
        assert "pasmo" in prompt_lower
        assert "pamaol" in prompt_lower
        assert "kalibanga" in prompt_lower
        assert "cebuano" in prompt_lower

    def test_stage2_system_prompt_enforces_safety(self):
        prompt_lower = STAGE2_MEDICAL_PROMPT.lower()
        assert "medgemma" in prompt_lower
        assert "red flag" in prompt_lower
        assert "licensed physician" in prompt_lower or "doctor" in prompt_lower
        assert "not prescribe" in prompt_lower

    def test_stage3_system_prompt_mentions_cebuano(self):
        prompt_lower = STAGE3_BACK_TRANSLATION_PROMPT.lower()
        assert "cebuano" in prompt_lower
        assert "everyday" in prompt_lower or "conversational" in prompt_lower

    def test_prompt_formatters(self):
        p1 = format_stage1_prompt("Sakit akong tiyan")
        assert "Sakit akong tiyan" in p1
        assert "English Clinical Translation" in p1

        p2 = format_stage2_prompt("Patient has stomach pain")
        assert "Patient has stomach pain" in p2
        assert "Clinical Guidance" in p2

        p3 = format_stage3_prompt("Drink oral rehydration salts")
        assert "Drink oral rehydration salts" in p3
        assert "Cebuano Medical Guidance" in p3


if __name__ == "__main__":
    unittest.main()
