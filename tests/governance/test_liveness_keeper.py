import base64
import importlib.util
import json
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "liveness_keeper", ROOT / "scripts/governance/liveness_keeper.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

GOV = "juno18k65at7fkf8elhece0fnhsvuxggqg6cved6trp5fyk3lftfn93xsmpeaac"
MARKET = "juno1fl48vsnmsdzcv85q5d2q4z5ajdha8yu3rf257t"
ORACLE = "juno1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83d88wr"
PAYEE = "juno17xpfvakm2amg962yls6f84z3kell8c5lxtqmvp"
QID = base64.b64encode(bytes(range(32))).decode()
OTHER_QID = base64.b64encode(bytes(range(1, 33))).decode()
ANSWER = base64.b64encode(b"\x00" * 31 + b"\x01").decode()
NOW = 1_800_000_050
DEADLINE = 1_800_000_100


class TimestampTests(unittest.TestCase):
    def test_parses_nanosecond_precision(self):
        self.assertEqual(
            MODULE.parse_rfc3339("2026-07-19T09:00:00.123456789Z"), 1784451600
        )

    def test_parses_no_fraction(self):
        self.assertEqual(MODULE.parse_rfc3339("2026-07-19T09:00:00Z"), 1784451600)

    def test_parses_single_digit_fraction(self):
        self.assertEqual(MODULE.parse_rfc3339("2026-07-19T09:00:00.5Z"), 1784451600)

    def test_rejects_missing_utc_suffix(self):
        with self.assertRaises(MODULE.KeeperError):
            MODULE.parse_rfc3339("2026-07-19T09:00:00+02:00")


class ClassifyOracleQuestionTests(unittest.TestCase):
    def test_open_unanswered_before_opening_is_ok(self):
        response = {"state": "open_unanswered", "question": {"opening_ts": NOW + 500}}
        result = MODULE.classify_oracle_question(NOW, response)
        self.assertEqual(result["alert"], "ok")
        self.assertEqual(result["seconds_until_opening"], 500)

    def test_open_unanswered_past_opening_needs_attention(self):
        response = {"state": "open_unanswered", "question": {"opening_ts": NOW - 10}}
        result = MODULE.classify_oracle_question(NOW, response)
        self.assertEqual(result["alert"], "attention")

    def test_open_answered_reports_finalize_countdown(self):
        response = {
            "state": "open_answered",
            "question": {"finalize_ts": NOW + 86_400},
        }
        result = MODULE.classify_oracle_question(NOW, response)
        self.assertEqual(result["alert"], "ok")
        self.assertEqual(result["seconds_until_finalize"], 86_400)

    def test_pending_arbitration_is_urgent(self):
        response = {
            "state": "pending_arbitration",
            "question": {"arbitration_deadline": DEADLINE},
        }
        result = MODULE.classify_oracle_question(NOW, response)
        self.assertEqual(result["alert"], "urgent")
        self.assertEqual(result["seconds_until_arbitration_deadline"], DEADLINE - NOW)

    def test_finalized_is_ok(self):
        response = {"state": "finalized", "question": {}}
        self.assertEqual(MODULE.classify_oracle_question(NOW, response)["alert"], "ok")


class ClassifyMarketTests(unittest.TestCase):
    def test_trading_reports_close_countdown(self):
        state = {"status": "trading"}
        question = {"close_ts": NOW + 1_000}
        result = MODULE.classify_market(NOW, state, question, None)
        self.assertEqual(result["alert"], "ok")
        self.assertEqual(result["seconds_until_close"], 1_000)

    def test_awaiting_resolution_needs_attention(self):
        state = {"status": "awaiting_resolution"}
        result = MODULE.classify_market(NOW, state, {"close_ts": NOW}, None)
        self.assertEqual(result["alert"], "attention")

    def test_pending_arbitration_is_urgent_with_deadline(self):
        state = {"status": "pending_arbitration"}
        challenge = {"deadline": DEADLINE}
        result = MODULE.classify_market(NOW, state, {"close_ts": NOW}, challenge)
        self.assertEqual(result["alert"], "urgent")
        self.assertEqual(result["seconds_until_challenge_deadline"], DEADLINE - NOW)

    def test_pending_arbitration_without_challenge_response_has_no_deadline(self):
        state = {"status": "pending_arbitration"}
        result = MODULE.classify_market(NOW, state, {"close_ts": NOW}, None)
        self.assertEqual(result["alert"], "urgent")
        self.assertIsNone(result["challenge_deadline"])

    def test_resolved_is_ok(self):
        state = {"status": "resolved"}
        result = MODULE.classify_market(NOW, state, {"close_ts": NOW}, None)
        self.assertEqual(result["alert"], "ok")


def valid_oracle_response():
    return {
        "question_id": QID,
        "question": {
            "arbitrator": MARKET,
            "arbitration_deadline": DEADLINE,
        },
        "state": "pending_arbitration",
    }


def valid_preflight_kwargs():
    return {
        "chain_id": "juno-1",
        "observed_unix": NOW,
        "governance_module": GOV,
        "market": MARKET,
        "oracle": ORACLE,
        "answer": ANSWER,
        "payee": PAYEE,
        "title": "Rehearsal-only PM arbitration verdict",
        "summary": "Authorized rehearsal evidence only; no production market.",
        "market_state": {"status": "pending_arbitration"},
        "market_question": {"question_id": QID},
        "market_challenge": {"deadline": DEADLINE},
        "oracle_response": valid_oracle_response(),
    }


class BuildPreflightRequestTests(unittest.TestCase):
    def test_builds_a_prepare_rehearsal_compatible_request(self):
        request = MODULE.build_preflight_request(**valid_preflight_kwargs())
        self.assertEqual(request["question_id"], QID)
        self.assertEqual(request["challenge_deadline_unix"], DEADLINE)
        self.assertEqual(request["market_state"]["governance"], GOV)
        self.assertEqual(request["oracle_state"]["arbitrator"], MARKET)
        expected_keys = {
            "chain_id", "observed_unix", "governance_module", "market", "oracle",
            "question_id", "answer", "payee", "challenge_deadline_unix",
            "market_state", "oracle_state", "title", "summary",
        }
        self.assertEqual(set(request), expected_keys)

    def test_rejects_market_not_pending_arbitration(self):
        kwargs = valid_preflight_kwargs()
        kwargs["market_state"] = {"status": "awaiting_resolution"}
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_rejects_oracle_not_pending_arbitration(self):
        kwargs = valid_preflight_kwargs()
        oracle_response = valid_oracle_response()
        oracle_response["state"] = "open_answered"
        kwargs["oracle_response"] = oracle_response
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_rejects_missing_market_question_id(self):
        kwargs = valid_preflight_kwargs()
        kwargs["market_question"] = {"question_id": None}
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_rejects_question_id_mismatch(self):
        kwargs = valid_preflight_kwargs()
        oracle_response = valid_oracle_response()
        oracle_response["question_id"] = OTHER_QID
        kwargs["oracle_response"] = oracle_response
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_rejects_missing_challenge_deadline(self):
        kwargs = valid_preflight_kwargs()
        kwargs["market_challenge"] = {"deadline": None}
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_rejects_deadline_mismatch_between_market_and_oracle(self):
        kwargs = valid_preflight_kwargs()
        oracle_response = valid_oracle_response()
        oracle_response["question"]["arbitration_deadline"] = DEADLINE + 1
        kwargs["oracle_response"] = oracle_response
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_rejects_arbitrator_not_the_exact_market(self):
        kwargs = valid_preflight_kwargs()
        oracle_response = valid_oracle_response()
        oracle_response["question"]["arbitrator"] = "juno1someoneelse"
        kwargs["oracle_response"] = oracle_response
        with self.assertRaises(MODULE.KeeperError):
            MODULE.build_preflight_request(**kwargs)

    def test_output_is_accepted_by_prepare_rehearsal_build(self):
        rehearsal_spec = importlib.util.spec_from_file_location(
            "prepare_rehearsal", ROOT / "scripts/governance/prepare_rehearsal.py"
        )
        assert rehearsal_spec is not None and rehearsal_spec.loader is not None
        rehearsal = importlib.util.module_from_spec(rehearsal_spec)
        rehearsal_spec.loader.exec_module(rehearsal)

        request = MODULE.build_preflight_request(**valid_preflight_kwargs())
        packet = rehearsal.build_packet(request)
        rehearsal.validate_packet(packet)
        message = packet["proposal"]["messages"][0]
        self.assertEqual(message["sender"], GOV)
        self.assertEqual(message["contract"], MARKET)
        decoded = json.loads(base64.b64decode(message["msg"], validate=True))
        self.assertEqual(
            decoded,
            {"governance_verdict": {"question_id": QID, "answer": ANSWER, "payee": PAYEE}},
        )


class LcdSmartQueryTests(unittest.TestCase):
    def test_encodes_query_as_base64_in_the_url_and_returns_data(self):
        captured_urls = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *exc_info):
                return False

            def read(self):
                return json.dumps({"data": {"state": "trading"}}).encode()

        def fake_urlopen(url, timeout):
            captured_urls.append(url)
            return FakeResponse()

        with mock.patch.object(MODULE.urllib.request, "urlopen", fake_urlopen):
            result = MODULE.lcd_smart_query("https://lcd.example", MARKET, {"state": {}})

        self.assertEqual(result, {"state": "trading"})
        expected_b64 = base64.b64encode(b'{"state":{}}').decode()
        self.assertEqual(captured_urls[0], f"https://lcd.example/cosmwasm/wasm/v1/contract/{MARKET}/smart/{expected_b64}")

    def test_raises_keeper_error_on_missing_data_field(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *exc_info):
                return False

            def read(self):
                return json.dumps({"oops": True}).encode()

        with mock.patch.object(MODULE.urllib.request, "urlopen", lambda url, timeout: FakeResponse()):
            with self.assertRaises(MODULE.KeeperError):
                MODULE.lcd_smart_query("https://lcd.example", MARKET, {"state": {}})

    def test_raises_keeper_error_on_network_failure(self):
        def fake_urlopen(url, timeout):
            raise urllib.error.URLError("boom")

        with mock.patch.object(MODULE.urllib.request, "urlopen", fake_urlopen):
            with self.assertRaises(MODULE.KeeperError):
                MODULE.lcd_smart_query("https://lcd.example", MARKET, {"state": {}})


class LcdLatestBlockTests(unittest.TestCase):
    def test_extracts_height_and_unix_time(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *exc_info):
                return False

            def read(self):
                body = {"block": {"header": {"height": "123", "time": "2026-07-19T09:00:00Z"}}}
                return json.dumps(body).encode()

        with mock.patch.object(MODULE.urllib.request, "urlopen", lambda url, timeout: FakeResponse()):
            height, observed = MODULE.lcd_latest_block("https://lcd.example")

        self.assertEqual(height, 123)
        self.assertEqual(observed, 1784451600)


if __name__ == "__main__":
    unittest.main()
