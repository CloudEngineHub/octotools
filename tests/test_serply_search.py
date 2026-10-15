import unittest
from unittest.mock import MagicMock, patch

from octotools.tools.serply_search.tool import Serply_Search_Tool


def fake_response(status_code=200, payload=None, reason="OK"):
    response = MagicMock()
    response.status_code = status_code
    response.reason = reason
    response.json.return_value = payload if payload is not None else {}
    return response


class SerplySearchTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.dict("os.environ", {"SERPLY_API_KEY": "test-key"})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tool = Serply_Search_Tool()

    def test_missing_key_returns_error(self):
        with patch.dict("os.environ", {}, clear=True):
            tool = Serply_Search_Tool()
        with patch("requests.get") as get:
            result = tool.execute(query="python")
        get.assert_not_called()
        self.assertIn("SERPLY_API_KEY", result[0]["error"])

    def test_maps_results_and_sends_key_header(self):
        payload = {"results": [
            {"title": "Python", "link": "https://www.python.org/", "description": "Official site."},
            {"title": "Token", "link": "CAESHAgBEhh0b2tlbg", "description": "Not a URL."},
            {"title": "Docs", "link": "https://docs.python.org/3/", "description": "Documentation."},
            {"title": "Extra", "link": "https://example.org/", "description": "Over the limit."},
        ]}
        with patch("requests.get", return_value=fake_response(payload=payload)) as get:
            result = self.tool.execute(query="python", num_results=2, gl="gb", time_range="week")

        self.assertEqual(result, [
            {"title": "Python", "link": "https://www.python.org/", "snippet": "Official site."},
            {"title": "Docs", "link": "https://docs.python.org/3/", "snippet": "Documentation."},
        ])
        kwargs = get.call_args.kwargs
        self.assertEqual(kwargs["params"], {"q": "python", "num": 2, "gl": "gb", "tbs": "qdr:w"})
        self.assertEqual(kwargs["headers"]["X-Api-Key"], "test-key")
        self.assertNotIn("test-key", str(kwargs["params"]))

    def test_num_results_is_capped_at_ten(self):
        with patch("requests.get", return_value=fake_response(payload={"results": []})) as get:
            result = self.tool.execute(query="python", num_results=50)
        self.assertEqual(get.call_args.kwargs["params"]["num"], 10)
        self.assertEqual(result, [{"error": "No results found."}])

    def test_api_error_detail_is_reported(self):
        response = fake_response(401, {"detail": "Invalid API key"}, "Unauthorized")
        with patch("requests.get", return_value=response):
            result = self.tool.execute(query="python")
        self.assertEqual(result, [{"error": "Serply API error (HTTP 401): Invalid API key"}])

    def test_invalid_time_range_is_rejected(self):
        with patch("requests.get") as get:
            result = self.tool.execute(query="python", time_range="decade")
        get.assert_not_called()
        self.assertIn("Invalid time_range", result[0]["error"])


if __name__ == "__main__":
    unittest.main()
