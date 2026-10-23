# TopoPatch fresh verification - 17 October 2026

## Delivered result

`output/pdf/TopoPatch_IDF_B_verified_proof.pdf` is the supplied 17-page disclosure
with its two old screenshot pages replaced by 13 fresh proof pages (28 total).
The new section contains the current verification record, 11 actual browser
captures covering the complete control flow, and separately labelled neural and
SciFact reruns. The original source remains in the evidence directory. Earlier
25-test statements and experiment tables are historical; the fresh record reports
30 tests. The previously noted external-writer rollback race is addressed by this
revision within the tested local SQLite scope.

## Improvements and validation

- Rollback obtains `BEGIN IMMEDIATE` before reading the commit or checking the
  epoch. A second SQLite connection is denied a write during the eligibility
  check. Injected rollback failure preserves membership, epoch and events.
- Preview responses report admission eligibility independently of retrieval
  barrier status. Strict mode disables commit for unbounded evidence, while the
  server independently rechecks current policy, snapshot, digest and constraints.
- The dashboard displays evidence mode and fusion policy. Development and
  packaged web assets remain synchronized.
- 30 automated tests pass, including original engine, continuity, exhaustive,
  public-data and new rollback/admission regression checks.
- 15 grouped browser/API checks pass, including direct unsafe HTTP commit refusal,
  malformed JSON, cross-origin write refusal, invalid IDs, stale preview refusal,
  actual server-process restart, browser evidence download, fallback and rollback.
- No browser JavaScript errors occurred in the exercised flow.

## Fresh observed results

| Run | Result |
| --- | --- |
| Browser lexical fixture | 40 documents / 4 protected queries; discovery charges 14 B vectors; unsafe `car-guide` refused; `password-policy` commits; epoch 1 / B active 1; restart persists; rollback reaches epoch 2 / B active 0 and retains 14 encodings. |
| Exhaustive strict browser | 40 B encodings; recommended 4-document protected bundle commits; all declared constraints pass. |
| Full lexical trajectory | All 40 documents migrated through passing commits; 40 B encodings. |
| Lexical fixture benchmark | Selective full-B top-5 overlap 0.80; legacy 0.95; protected violations 0. |
| Neural target fixture | Selective overlap 0.50; 1 migrated object; 14 charged B encodings; protected violations 0. |
| SciFact RRF | 160 documents; 6 protected / 6 development / 6 held-out queries; 301 candidates refused; 0 migrated; 80 charged B encodings; held-out nDCG@10 unchanged at 0.8889. |
| SciFact continuity | Same sampled split; 1 migrated; 80 charged B encodings; held-out nDCG@10 unchanged at 0.8889. |
| SciFact full-B reference | nDCG@10 0.8978; 160 additional evaluator-only B encodings per run. |

The public sample is relevance-aware and previously inspected. It is not a full
BEIR benchmark or an independent confirmation set. These measurements strengthen
the record of an implemented, tested admission mechanism. They do not establish
better general retrieval quality, an equal-quality compute saving, ANN topology
repair, production crash recovery, novelty or patentability. Existing prior-art
and legal discussion was retained, not re-researched in this engineering task.

## Reproduction

From the project root, with Python 3.11 or later:

```sh
python3 -m unittest discover -s tests -v
python3 -m scripts.prove_prototype
python3 -m topopatch benchmark --output artifacts_private/new-benchmark.json
python3 -m topopatch serve --db artifacts_private/new-demo.sqlite --port 8765
```

For the full trajectory, call `topopatch.trajectory.migrate(fixture())` as in
`tests/test_engine.py`. The saved trace contains assertions for refusal,
preview/commit parity, reopen persistence, rollback and failure injection.

The browser capture script requires Node and Playwright with Chromium installed:

```sh
TOPOPATCH_PROOF_DIR=/absolute/path/to/new-empty-evidence-folder \
PLAYWRIGHT_MODULE=/absolute/path/to/node_modules/playwright \
node scripts/capture_proof.cjs
```

It starts and stops its own three loopback servers on ports 8875-8877, refuses to
overwrite existing evidence databases, and saves state JSON, raw screenshots and
`browser-report.json`. The screenshots in this delivery come from the completed
run only. An earlier capture attempt stopped when the test assumed exhaustive
mode recommended a singleton; the completed script correctly uses the actual
recommended four-object bundle. No project failure is hidden by that correction.

Neural reruns use the locally cached MiniLM L6 snapshot
`c9745ed1d9f207416be6d2e6f8de32d1f16199bf` and L12 snapshot
`a50ef00143b4d5391434df20ae11632588ac25be`, offline. `model-provenance.json`
records file-level SHA-256 hashes for the cached snapshots. Execute
`python3 -m topopatch research --model-a <L6-snapshot> --model-b <L12-snapshot>
--corpus-limit 160 --query-limit 18 --fusion rrf --output <new-report.json>`;
repeat with `--fusion continuity`. Set `HF_HUB_OFFLINE=1` and
`TRANSFORMERS_OFFLINE=1`. The optional path requires sentence-transformers;
the default fixture does not.

To regenerate the revised PDF from saved evidence, install Pillow, pypdf and
reportlab and run `python3 scripts/refresh_proof_pdf.py`. Model weights are not
included in the archive. Evidence hashes establish byte identity, not independent
authentication or legal priority.
