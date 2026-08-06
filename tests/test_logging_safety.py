import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from observability.error_reporting import mask_sensitive_text


class LoggingSafetyTests(unittest.TestCase):
    def test_masks_email_and_phone(self):
        masked = mask_sensitive_text("Email test@example.com phone +44 7700 900123")
        self.assertNotIn("test@example.com", masked)
        self.assertNotIn("+44 7700 900123", masked)
        self.assertIn("[masked]", masked)


if __name__ == "__main__":
    unittest.main()
