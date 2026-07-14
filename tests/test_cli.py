import contextlib
import io
import unittest

from metaxis.cli import main


class CliTests(unittest.TestCase):
    def test_status_is_honest_about_activation(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["status"])
        self.assertEqual(result, 0)
        self.assertIn("production inference: not activated", output.getvalue())


if __name__ == "__main__":
    unittest.main()
