"""Offline model-gating tests: no real API calls or expenses."""
import json
import unittest
from makine.agent import analyze, parse_response

EXAMPLE = {
    "generated_at_utc": "2026-10-18T07:40:03Z",
    "system_state": "ATTENTION_REQUIRED",
    "sources": {"alti": {"repo": "onurqlp/alti-quant-lab", "state": "STALE",
                         "scan_id": "old", "age_minutes": 259,
                         "warnings": [], "strategies": {}}},
    "overlaps": [{"makine_model_id": 31, "alti_strategy_id": "B1"}],
}

class AgentTests(unittest.TestCase):
    def test_not_enabled_never_calls_model(self):
        def fail(*args):
            raise AssertionError("Unexpected paid model call")
        r = analyze(EXAMPLE, sender=fail, api_key="present", model="gpt-5-mini")
        self.assertEqual(r["status"], "DISABLED")
        self.assertFalse(r["can_modify_repositories"])

    def test_missing_api_key_no_call(self):
        r = analyze(EXAMPLE, enabled=True, api_key="", model="gpt-5-mini")
        self.assertEqual(r["status"], "MISSING_API_KEY")

    def test_model_allowlist_no_call(self):
        r = analyze(EXAMPLE, enabled=True, api_key="mock", model="unauthorized-model")
        self.assertEqual(r["status"], "MODEL_NOT_ALLOWED")

    def test_structured_research_only(self):
        def mock_send(payload, key):
            self.assertEqual(key, "mock")
            self.assertFalse(payload["store"])
            self.assertEqual(payload["text"]["format"]["type"], "json_schema")
            return {"status": "completed", "output": [
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": json.dumps({
                        "summary": "ALTI raporu eski.", "risks": ["Gecikme"],
                        "proposed_tasks": [{"owner": "ALTI", "task": "Scan zamanını doğrula",
                                            "source_key": "alti", "priority": "HIGH"}]
                    })}]}]}
        r = analyze(EXAMPLE, enabled=True, api_key="mock",
                    model="gpt-5-mini", sender=mock_send)
        self.assertEqual(r["status"], "COMPLETED")
        self.assertEqual(r["proposed_tasks"][0]["approval_state"], "PROPOSED_NOT_APPROVED")
        self.assertTrue(r["requires_user_approval"])
        self.assertFalse(r["can_place_orders"])

    def test_rejects_more_than_three_model_tasks(self):
        s = {"summary": "x", "risks": [], "proposed_tasks": [
            {"owner": "ALTI", "task": str(i), "source_key": "alti", "priority": "LOW"}
            for i in range(4)]}
        with self.assertRaises(ValueError):
            parse_response({"status": "completed", "output": [
                {"type": "message", "role": "assistant",
                 "content": [{"type": "output_text", "text": json.dumps(s)}]}]})

if __name__ == "__main__":
    unittest.main()
