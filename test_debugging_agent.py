import unittest

from debugging_agent import extract_code, validate_python


class ExtractCodeTests(unittest.TestCase):
    def test_prefers_code_block_for_selected_language(self):
        response = (
            "Example:\n```text\nnot the program\n```\n"
            "Correction:\n```python\nprint('fixed')\n```"
        )
        self.assertEqual(extract_code(response, "Python"), "print('fixed')")

    def test_returns_empty_when_no_fenced_code_is_present(self):
        self.assertEqual(extract_code("No correction.", "Python"), "")


class PythonValidationTests(unittest.TestCase):
    def test_reports_syntax_error_without_running_code(self):
        status, details = validate_python("if True print('bad')", approved=True)
        self.assertEqual(status, "FAILED")
        self.assertIn("Syntax error", details)

    def test_requires_approval_before_execution(self):
        status, details = validate_python("print('ok')", approved=False)
        self.assertEqual(status, "SYNTAX PASSED")
        self.assertIn("Approve local execution", details)

    def test_compares_program_output_to_expected_output(self):
        status, details = validate_python(
            "print(' 0 ')", expected_output="0", approved=True
        )
        self.assertEqual(status, "TESTS PASSED")
        self.assertIn("matched the expected output", details)

    def test_empty_input_average_demo(self):
        corrected_program = (
            "numbers = list(map(int, input().split()))\n"
            "print(sum(numbers) / len(numbers) if numbers else 0)"
        )
        status, details = validate_python(
            corrected_program,
            user_input="\n",
            expected_output="0",
            approved=True,
        )
        self.assertEqual(status, "TESTS PASSED")
        self.assertIn("Output:\n0", details)

    def test_reports_mismatched_program_output(self):
        status, details = validate_python(
            "print(1)", expected_output="2", approved=True
        )
        self.assertEqual(status, "TESTS FAILED")
        self.assertIn("Expected:", details)
        self.assertIn("Actual:", details)

    def test_reports_runtime_failure(self):
        status, details = validate_python(
            "raise ValueError('broken')", approved=True
        )
        self.assertEqual(status, "EXECUTION FAILED")
        self.assertIn("ValueError", details)


if __name__ == "__main__":
    unittest.main()
