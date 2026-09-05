import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from pathlib import Path
import subprocess
from update_activity import main, render


def fixture():
    return {"data": {"user": {"contributionsCollection": {
        "totalCommitContributions": 0, "totalPullRequestContributions": 2,
        "totalIssueContributions": 1, "contributionCalendar": {
            "totalContributions": 3, "weeks": [{"contributionDays": [
                {"date": "2026-09-05", "contributionCount": 3, "contributionLevel": "FIRST_QUARTILE"}]}]}}}}}


class ActivityTests(unittest.TestCase):
    def test_empty_counts_and_calendar_date_are_rendered(self):
        root = ET.fromstring(render(fixture(), "2026-09-05"))
        text = " ".join(root.itertext())
        self.assertIn("2026-09-05: 3 contributions", text)
        self.assertIn("Commits", text)
        self.assertIn(">0<", render(fixture(), "2026-09-05"))

    def test_graphql_error_does_not_render_misleading_zeroes(self):
        with self.assertRaises(ValueError):
            render({"errors": [{"message": "rate limit"}]}, "2026-09-05")

    def test_invalid_calendar_is_rejected(self):
        data = fixture()
        data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"] = []
        with self.assertRaises(ValueError):
            render(data, "2026-09-05")

    def test_failed_fetch_preserves_cached_asset(self):
        with patch("update_activity.subprocess.run", side_effect=subprocess.CalledProcessError(1, "gh")):
            with patch.object(Path, "write_text") as write:
                with self.assertRaises(subprocess.CalledProcessError):
                    main()
                write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
