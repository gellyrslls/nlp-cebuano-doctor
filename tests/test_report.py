"""Tests for slide presentation report deck and deliverables."""
from pathlib import Path


def test_presentation_slides_markdown_exists_and_contains_rubric_sections():
    slides_path = Path("report/slides.md")
    assert slides_path.exists(), "Expected report/slides.md to exist"

    content = slides_path.read_text(encoding="utf-8")
    assert len(content) > 2000

    # Verify key metadata
    assert "CS 5101" in content
    assert "Dr. Vladimir Mariano" in content
    assert "University of San Carlos" in content
    assert "gellyrslls/nlp-cebuano-doctor" in content
    assert "Angelo Rosillosa and Liam Jones" in content

    # Verify core architectural and evaluation concepts
    assert "Gemma 4" in content
    assert "MedGemma" in content
    assert "NLU" in content
    assert "NLG" in content
    assert "Circular Translation" in content

    # Verify all 5 benchmark prompts are covered
    assert "PROMPT-01" in content or "Panuhot" in content
    assert "PROMPT-02" in content or "Pasmo" in content
    assert "PROMPT-03" in content or "Kalibanga" in content
    assert "PROMPT-04" in content or "Pamaol" in content
    assert "PROMPT-05" in content or "Hilanat" in content

    # Verify linguistic nuance section
    assert "panuhot" in content.lower()
    assert "pasmo" in content.lower()
    assert "pamaol" in content.lower()

    # Verify future work and barangay deployment vision
    assert "Barangay" in content or "barangay" in content


def test_presentation_report_html_pdf_ready_exists():
    html_path = Path("report/presentation_report.html")
    assert html_path.exists(), "Expected report/presentation_report.html to exist"

    html_content = html_path.read_text(encoding="utf-8")
    assert len(html_content) > 3000
    assert "<html" in html_content.lower()
    assert "@page" in html_content or "print" in html_content
    assert "Cebuano Doctor" in html_content
    assert "Angelo Rosillosa and Liam Jones" in html_content


def test_presentation_report_pdf_exists():
    pdf_path = Path("report/presentation_report.pdf")
    assert pdf_path.exists(), "Expected report/presentation_report.pdf to exist"
    assert pdf_path.stat().st_size > 100_000, "Expected PDF file size > 100 KB"

