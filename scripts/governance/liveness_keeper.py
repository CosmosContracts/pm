#!/usr/bin/env python3
"""Read-only liveness monitor for cw-reality questions and binary-market challenges.

This tool is deliberately read-only. It performs LCD smart-queries over plain
HTTPS GET and never signs, broadcasts, or holds key material. It has two
purposes:

1. ``report`` -- summarise the oracle/market lifecycle for one or more
   markets so an operator (or an alerting cron job) can see unanswered,
   stalled, or pending-arbitration questions without hand-composing queries.
   This is the "operate alerts/keepers" half of ADR-013.

2. ``preflight`` -- for one market that is in ``pending_arbitration``, fetch
   every queryable field required by ``scripts/governance/prepare_rehearsal.py``
   and emit a ready-to-review request JSON. This automates steps 1-5 of
   ``docs/prediction-market/dao-dao-verdict-runbook.md`` ("Pre-execution
   review") and the "Offline preparation" step of
   ``docs/prediction-market/governance-rehearsal/README.md``. It does not
   choose the answer or payee, does not build or validate the final packet,
   and does not submit, vote on, or execute anything. Feed its output
   straight into::

       python3 scripts/governance/prepare_rehearsal.py build request.json packet.json
       python3 scripts/governance/prepare_rehearsal.py validate packet.json

   and independently re-verify every field before any separately authorized
   proposal process, exactly as both runbooks require.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn

# The v1 verdict authority pinned by ADR-017 (issue #45): the Juno Agents DAO
# core. Only a default -- always cross-checked against the live market config
# before it is trusted for anything.
DEFAULT_GOVERNANCE_MODULE = "juno18k65at7fkf8elhece0fnhsvuxggqg6cved6trp5fyk3lftfn93xsmpeaac"


class KeeperError(ValueError):
    pass


def _fail(message: str) -> NoReturn:
    raise KeeperError(message)


def parse_rfc3339(value: str) -> int:
    """Parse a Tendermint RFC3339 timestamp (any fractional precision) to Unix seconds."""
    if not value.endswith("Z"):
        _fail(f"expected a Z-suffixed UTC timestamp, got {value!r}")
    body = value[:-1]
    head, _, frac = body.partition(".")
    micros = (frac + "000000")[:6]
    try:
        return int(datetime.fromisoformat(f"{head}.{micros}+00:00").timestamp())
    except ValueError as error:
        _fail(f"malformed timestamp {value!r}: {error}")


# ---- LCD access (network I/O lives only in these two functions) ----


def lcd_smart_query(lcd: str, address: str, query: dict[str, Any]) -> dict[str, Any]:
    encoded = base64.b64encode(json.dumps(query, separators=(",", ":")).encode()).decode()
    url = f"{lcd.rstrip('/')}/cosmwasm/wasm/v1/contract/{address}/smart/{encoded}"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.URLError as error:
        _fail(f"LCD smart-query to {address} failed: {error}")
    except json.JSONDecodeError as error:
        _fail(f"LCD smart-query to {address} returned invalid JSON: {error}")
    if not isinstance(payload, dict) or "data" not in payload:
        _fail(f"LCD smart-query to {address} returned no data field")
    return payload["data"]


def lcd_latest_block(lcd: str) -> tuple[int, int]:
    url = f"{lcd.rstrip('/')}/cosmos/base/tendermint/v1beta1/blocks/latest"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.URLError as error:
        _fail(f"LCD latest-block query failed: {error}")
    except json.JSONDecodeError as error:
        _fail(f"LCD latest-block query returned invalid JSON: {error}")
    try:
        header = payload["block"]["header"]
        height = int(header["height"])
        observed_unix = parse_rfc3339(header["time"])
    except (KeyError, TypeError, ValueError) as error:
        _fail(f"LCD latest-block response missing height/time: {error}")
    return height, observed_unix


# ---- Query builders (binary-market::msg::QueryMsg / cw_reality::msg::QueryMsg) ----


def market_config_query() -> dict[str, Any]:
    return {"config": {}}


def market_state_query() -> dict[str, Any]:
    return {"state": {}}


def market_question_query() -> dict[str, Any]:
    return {"question": {}}


def market_challenge_query() -> dict[str, Any]:
    return {"challenge": {}}


def oracle_question_query(question_id_base64: str) -> dict[str, Any]:
    return {"question": {"question_id": question_id_base64}}


# ---- Pure classification (network-free, unit-tested) ----


def classify_oracle_question(now: int, response: dict[str, Any]) -> dict[str, Any]:
    """Classify a cw-reality ``QueryMsg::Question`` response.

    ``response`` is the exact ``QuestionResponse`` shape: ``question_id``,
    ``question`` (the full ``Question`` struct), and ``state``.
    """
    state = response["state"]
    question = response["question"]
    result: dict[str, Any] = {"oracle_state": state}
    if state == "open_unanswered":
        opening_ts = question.get("opening_ts")
        result["alert"] = "attention" if opening_ts is not None and now >= opening_ts else "ok"
        if opening_ts is not None:
            result["seconds_until_opening"] = opening_ts - now
    elif state == "open_answered":
        finalize_ts = question.get("finalize_ts")
        result["finalize_ts"] = finalize_ts
        result["seconds_until_finalize"] = None if finalize_ts is None else finalize_ts - now
        result["alert"] = "ok"
    elif state == "pending_arbitration":
        deadline = question.get("arbitration_deadline")
        result["arbitration_deadline"] = deadline
        result["seconds_until_arbitration_deadline"] = None if deadline is None else deadline - now
        result["alert"] = "urgent"
    else:
        # not_created, finalized, claimed
        result["alert"] = "ok"
    return result


def classify_market(
    now: int,
    state_response: dict[str, Any],
    question_response: dict[str, Any],
    challenge_response: dict[str, Any] | None,
) -> dict[str, Any]:
    """Classify a binary-market ``State`` + ``Question`` + ``Challenge`` response set."""
    status = state_response["status"]
    result: dict[str, Any] = {"market_status": status}
    if status == "trading":
        result["seconds_until_close"] = question_response["close_ts"] - now
        result["alert"] = "ok"
    elif status == "awaiting_resolution":
        result["alert"] = "attention"
    elif status == "pending_arbitration":
        deadline = challenge_response.get("deadline") if challenge_response else None
        result["challenge_deadline"] = deadline
        result["seconds_until_challenge_deadline"] = None if deadline is None else deadline - now
        result["alert"] = "urgent"
    else:
        # initializing, resolved
        result["alert"] = "ok"
    return result


def build_preflight_request(
    *,
    chain_id: str,
    observed_unix: int,
    governance_module: str,
    market: str,
    oracle: str,
    answer: str,
    payee: str,
    title: str,
    summary: str,
    market_state: dict[str, Any],
    market_question: dict[str, Any],
    market_challenge: dict[str, Any],
    oracle_response: dict[str, Any],
) -> dict[str, Any]:
    """Assemble a ``prepare_rehearsal.py``-compatible request from live query responses.

    Every identity/state/deadline field is taken directly from the queried
    responses, never invented, and cross-checked for internal consistency.
    ``prepare_rehearsal.py build`` still independently re-validates the
    result; this function narrows -- it never widens -- what it accepts.
    """
    if market_state["status"] != "pending_arbitration":
        _fail(f"market is not pending_arbitration (observed {market_state['status']!r})")
    if oracle_response["state"] != "pending_arbitration":
        _fail(f"oracle question is not pending_arbitration (observed {oracle_response['state']!r})")

    question_id = market_question.get("question_id")
    if question_id is None:
        _fail("market has no bound question_id yet")
    if question_id != oracle_response["question_id"]:
        _fail("market question_id does not match the oracle question_id")

    deadline = market_challenge.get("deadline")
    if deadline is None:
        _fail("market has no active challenge deadline")
    oracle_deadline = oracle_response["question"].get("arbitration_deadline")
    if oracle_deadline != deadline:
        _fail("market challenge deadline does not match the oracle arbitration deadline")

    arbitrator = oracle_response["question"].get("arbitrator")
    if arbitrator != market:
        _fail(f"oracle arbitrator {arbitrator!r} is not the exact market {market!r}")

    return {
        "chain_id": chain_id,
        "observed_unix": observed_unix,
        "governance_module": governance_module,
        "market": market,
        "oracle": oracle,
        "question_id": question_id,
        "answer": answer,
        "payee": payee,
        "challenge_deadline_unix": deadline,
        "market_state": {
            "status": "pending_arbitration",
            "governance": governance_module,
            "oracle": oracle,
            "question_id": question_id,
            "deadline_unix": deadline,
        },
        "oracle_state": {
            "status": "pending_arbitration",
            "arbitrator": market,
            "question_id": question_id,
            "deadline_unix": deadline,
        },
        "title": title,
        "summary": summary,
    }


# ---- Commands ----


def _report_one(lcd: str, market: str, now: int) -> dict[str, Any]:
    config = lcd_smart_query(lcd, market, market_config_query())
    state = lcd_smart_query(lcd, market, market_state_query())
    question = lcd_smart_query(lcd, market, market_question_query())
    challenge = lcd_smart_query(lcd, market, market_challenge_query())
    oracle = config["oracle"]

    entry: dict[str, Any] = {
        "market": market,
        "oracle": oracle,
        "market_summary": classify_market(now, state, question, challenge),
    }
    question_id = question.get("question_id")
    if question_id is not None:
        oracle_response = lcd_smart_query(lcd, oracle, oracle_question_query(question_id))
        entry["oracle_summary"] = classify_oracle_question(now, oracle_response)

    severity = {"ok": 0, "attention": 1, "urgent": 2}
    alerts = [entry["market_summary"]["alert"]]
    if "oracle_summary" in entry:
        alerts.append(entry["oracle_summary"]["alert"])
    entry["alert"] = max(alerts, key=lambda level: severity[level])
    return entry


def _cmd_report(args: argparse.Namespace) -> int:
    _, now = lcd_latest_block(args.lcd)
    report = {
        "lcd": args.lcd,
        "observed_unix": now,
        "markets": [_report_one(args.lcd, market, now) for market in args.market],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _cmd_preflight(args: argparse.Namespace) -> int:
    _, now = lcd_latest_block(args.lcd)
    market_config = lcd_smart_query(args.lcd, args.market, market_config_query())
    oracle = market_config["oracle"]
    if args.oracle is not None and args.oracle != oracle:
        _fail(f"--oracle {args.oracle!r} does not match market-configured oracle {oracle!r}")

    market_state = lcd_smart_query(args.lcd, args.market, market_state_query())
    market_question = lcd_smart_query(args.lcd, args.market, market_question_query())
    market_challenge = lcd_smart_query(args.lcd, args.market, market_challenge_query())

    question_id = market_question.get("question_id")
    if question_id is None:
        _fail("market has no bound question_id yet")
    oracle_response = lcd_smart_query(args.lcd, oracle, oracle_question_query(question_id))

    request = build_preflight_request(
        chain_id=args.chain_id,
        observed_unix=now,
        governance_module=args.governance_module,
        market=args.market,
        oracle=oracle,
        answer=args.answer,
        payee=args.payee,
        title=args.title,
        summary=args.summary,
        market_state=market_state,
        market_question=market_question,
        market_challenge=market_challenge,
        oracle_response=oracle_response,
    )
    text = json.dumps(request, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n")
        print(f"wrote preflight request: {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser("report", help="summarise oracle/market liveness (read-only)")
    report.add_argument("--lcd", required=True, help="Juno LCD/REST base URL")
    report.add_argument(
        "--market", action="append", required=True, help="binary-market contract address; repeatable"
    )

    preflight = subparsers.add_parser(
        "preflight",
        help="assemble a prepare_rehearsal.py request for one pending-arbitration market (read-only)",
    )
    preflight.add_argument("--lcd", required=True, help="Juno LCD/REST base URL")
    preflight.add_argument("--chain-id", default="juno-1")
    preflight.add_argument("--market", required=True, help="binary-market contract address")
    preflight.add_argument(
        "--oracle", default=None, help="expected cw-reality address; cross-checked against market config"
    )
    preflight.add_argument(
        "--governance-module",
        default=DEFAULT_GOVERNANCE_MODULE,
        help="verdict authority address (defaults to the ADR-017 v1 Juno Agents DAO core)",
    )
    preflight.add_argument("--answer", required=True, help="base64-encoded 32-byte answer")
    preflight.add_argument("--payee", required=True, help="checksummed Juno payee address")
    preflight.add_argument("--title", required=True)
    preflight.add_argument("--summary", required=True)
    preflight.add_argument("--out", default=None, help="write the request JSON here instead of stdout")

    args = parser.parse_args()
    try:
        if args.command == "report":
            return _cmd_report(args)
        return _cmd_preflight(args)
    except (KeeperError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
