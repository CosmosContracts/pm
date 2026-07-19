# Liveness keeper (operational tooling, not a new decision)

**Status:** proposed operational tooling; does not amend any accepted ADR, decision, protocol parameter, or generated schema.
**Implements:** the alerts/keepers half of [ADR-013](adrs/ADR-013-resolution-liveness.md) and the automatable steps of [dao-dao-verdict-runbook.md](dao-dao-verdict-runbook.md) and [governance-rehearsal/README.md](governance-rehearsal/README.md).

`scripts/governance/liveness_keeper.py` is a dependency-free, read-only Python
script. It performs LCD smart-queries over plain HTTPS GET and never signs,
broadcasts, or holds key material — the same posture as
`scripts/oracle/verify-deployment.py` and `scripts/governance/prepare_rehearsal.py`.

## `report`

```sh
python3 scripts/governance/liveness_keeper.py report \
  --lcd https://lcd-juno.example.com \
  --market <MARKET_ADDR> [--market <MARKET_ADDR> ...]
```

For each market, queries `Config`, `State`, `Question`, and `Challenge`, then
(if a question is bound) the oracle's `Question`. Prints one JSON report with
a per-market `alert` of `ok`, `attention`, or `urgent`:

- **`attention`** — `awaiting_resolution` (question closed, unanswered oracle
  answer still pending) or an oracle question past its `opening_ts` with no
  answer yet.
- **`urgent`** — `pending_arbitration` on either the market or the oracle,
  with the challenge/arbitration deadline countdown included.

This is intended to run on a schedule (cron, CI scheduled job, or any
existing alerting pipeline) so operators learn about a stalled question or an
open challenge without polling the chain by hand.

## `preflight`

```sh
python3 scripts/governance/liveness_keeper.py preflight \
  --lcd https://lcd-juno.example.com \
  --market <MARKET_ADDR> \
  --answer <BASE64_32_BYTES> \
  --payee <JUNO_PAYEE> \
  --title "..." \
  --summary "..." \
  --out request.json
```

For one market that is `pending_arbitration`, queries every field
`scripts/governance/prepare_rehearsal.py` requires and cross-checks
question-ID, deadline, and arbitrator agreement between the market and the
oracle before emitting anything. `--governance-module` defaults to the
ADR-017 v1 verdict authority (the Juno Agents DAO core;
`juno18k65at7fkf8elhece0fnhsvuxggqg6cved6trp5fyk3lftfn93xsmpeaac`) and can be
overridden for a rehearsal-only `x/gov` profile.

The emitted `request.json` is consumed unmodified by the existing tool:

```sh
python3 scripts/governance/prepare_rehearsal.py build request.json packet.json
python3 scripts/governance/prepare_rehearsal.py validate packet.json
```

`preflight` only narrows what `prepare_rehearsal.py` already validates — it
adds pre-fetch consistency checks, it does not relax any existing check. It
does not choose the answer or payee (those remain a human/DAO decision), and
it does not build the proposal packet, submit a proposal, vote, or execute.

## What this does not do

- No transaction is ever signed or broadcast; no private key material is
  read, generated, or required.
- No default is silently trusted: `preflight` fails closed if the market and
  oracle disagree on question ID, deadline, or arbitrator, or if either side
  is not actually `pending_arbitration`.
- No accepted ADR, protocol parameter, generated schema, or release artifact
  is changed. This is additive operational tooling plus its own test file
  (`tests/governance/test_liveness_keeper.py`, wired into `scripts/validate.sh`).

## Tests

`tests/governance/test_liveness_keeper.py` covers the pure classification and
request-assembly functions with fixture data matching the golden wire schema
in `contracts/binary-market/tests/wire_schema_golden.rs`, mocks LCD HTTP
calls to verify request construction and error handling, and includes an
end-to-end check that `build_preflight_request`'s output is accepted by the
real `prepare_rehearsal.py build`/`validate_packet` and produces the exact
expected `governance_verdict` execute message.
