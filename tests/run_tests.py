"""Standard library unittest runner for pipeline seam tests."""
import unittest
from tests.test_pipeline import (
    test_empty_complaint_returns_error,
    test_circular_pipeline_runs_successfully,
    test_stage_metrics_measured,
    test_provider_error_handled_gracefully,
    test_cultural_idiom_passed_to_stage1,
)


class TestCebuanoDoctorPipeline(unittest.TestCase):
    def test_empty_complaint(self):
        test_empty_complaint_returns_error()

    def test_circular_pipeline(self):
        test_circular_pipeline_runs_successfully()

    def test_stage_metrics(self):
        test_stage_metrics_measured()

    def test_provider_error(self):
        test_provider_error_handled_gracefully()

    def test_cultural_idiom(self):
        test_cultural_idiom_passed_to_stage1()


if __name__ == "__main__":
    unittest.main()
