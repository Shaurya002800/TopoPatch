# TopoPatch migration lab

TopoPatch is a local research prototype for selective migration between vector representations. It materializes proposed membership changes, measures their effects on protected retrieval queries, and commits only admissible states. It includes a browser workbench, a Python API, a reproducible experiment runner, SQLite history, rollback, and exported evidence.

## Run

Python 3.11 or later is sufficient for the default offline demo. Run from this directory:

```sh
python3 -m topopatch serve
```

Open http://127.0.0.1:8765. State persists in `artifacts_private/demo.sqlite`. Use `--db artifacts_private/another.sqlite --port 8766` for a fresh independent experiment. The service binds only to loopback and serializes requests. It is a local lab tool, not a hosted service.

```sh
python3 -m unittest discover -s tests -v
python3 -m topopatch benchmark
```

The benchmark writes `artifacts_private/benchmark.json`. The full migration controller is `topopatch.trajectory.migrate`; its saved run is `artifacts_private/trajectory.json`.

## Demonstration

1. Click **Analyze candidates**. Discovery encodings are charged even for candidates that are never committed.
2. Open a rejected action such as `car-guide`. Inspect the failing protected query and disabled commit button.
3. Open the admissible `password-policy` action and commit it. The target membership count and epoch change only after the server independently rechecks the barrier.
4. Search the mixed state, export JSON evidence, or roll back the latest commit.
5. Select any remaining documents to preview a custom bundle. Repeated analysis proposes additional monotonic migration steps.

The optional legacy fallback button validates the original route for the selected registered query. API clients must supply that query's exact ID and text to use its fallback. Arbitrary free-text searches use the mixed state. The safety table reports the raw mixed state, independent of fallback.

## Models and datasets

The default model pair is an actual, deterministic lexical hashing implementation: 128-dimensional raw tokens and 256-dimensional synonym-normalized tokens. It is intentionally lightweight and is **not** a trained semantic model. Its authored 40-document fixture tests functionality; it is not a published benchmark.

A local Sentence Transformers snapshot can be used as target B. This optional path requires an installed `sentence-transformers` package. It was exercised here with version 3.0.0 and the cached all-MiniLM-L6-v2 snapshot `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` (384 dimensions). A remains lexical in the CLI; the Python `Engine(model_a=..., model_b=...)` accepts two encoder objects with `identity`, `dimension`, and `encode(text)`.

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 -m topopatch benchmark \
  --target-snapshot /absolute/path/to/local/snapshot \
  --output artifacts_private/neural_target_benchmark.json
```

The same `--target-snapshot` option is accepted by `serve`; use a new database when switching models. No model downloads are performed by the default workflow. The UI's offline fixture header refers to the default demo; custom model experiment identity is authoritative in the exported manifest.

Both commands accept `--dataset /path/to/dataset.json` with this schema:

```json
{
  "documents": [{"id": "doc-1", "text": "source text"}],
  "protected_queries": [{"id": "query-1", "text": "source", "required": "doc-1", "max_rank": 1}],
  "progress_queries": ["a held-out evaluation query"]
}
```

Source updates are available through `Engine.update_source`. They invalidate affected target vectors, increment the epoch and reject old previews. Do not edit the database manually.

## Implementation boundaries

- Exact flat search in each native space. No cross-space cosine comparisons. Rank fusion uses constant 60; ties favor B, then stable document ID. This policy is explicit and fixed before each reported run.
- Safety checks required-document maximum ranks for registered queries. This does not establish safety for unseen queries or full-B equivalence. Empty protected sets provide no meaningful safety coverage and should not be used for evidence.
- Candidate selection is a heuristic envelope. It explicitly reports `HEURISTIC_UNBOUNDED`. The prototype does not implement the specification's proposed bound on unseen B competitors.
- The optimizer enumerates singleton and pair actions over at most 24 candidates, expanding to a bundle of protected objects if needed. Minimum cost means minimum number of migrated objects among inspected actions, not a globally optimal repair or minimum total CPU cost.
- The trajectory runner advances safe actions to full migration, expanding to all remaining objects if necessary. It halts if even that state fails the declared constraints.
- B document encodings are cached by source hash within each experiment. Discovery and preview work count. B query encodings are separately counted and queries cached per process. Full-B evaluator vectors are created independently and are not supplied to the optimizer.
- The baseline named `random_equal_migration_count` matches committed objects, **not** total discovery cost. It is illustrative, not evidence of equal-budget superiority.
- SQLite commits protect active membership, epoch, write ledger and commit history atomically. A failed write rolls these back. Original A vectors are retained for fallback, so storage is not claimed to shrink.
- No ANN graph repair or topology savings is claimed. Index writes are logical object updates, not physical bytes or internal graph operations.

## Current measured evidence

The default single-step run migrated 1 of 40 objects after encoding 14 candidate documents. All four protected constraints passed; 13 of 14 singleton previews were rejected. Held-out full-B top-5 overlap was 0.80, versus 0.95 for legacy A and 1.00 for full B. The random action violated one protected constraint. This demonstrates gate behavior, not overall retrieval improvement.

The neural target run also passed protected constraints, with 0.50 held-out overlap for the selective state and legacy state. Full migration of the default fixture completed in 40 safe commits and encoded all 40 documents. No final full-migration compute saving is claimed.

The completed disclosure and evidence package are in `deliverables/`. See `docs_private/IMPLEMENTATION_STATUS.md` for remaining research limitations. The original specification remains unchanged in `doc/`.

## Public-data research gate

A SciFact-based neural model-pair experiment is in `artifacts_private/scifact-research.json`. The 160-document relevance-aware sample showed a large held-out quality drop under the current mixed-state rank fusion. See `docs_private/SCIFACT_RESEARCH_GATE.md` before using any result in a disclosure. The source archive is retained at `data/scifact.zip` for reproducibility.

To repeat with the same locally installed model snapshots, run:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 -m topopatch research \
  --model-a /absolute/path/to/all-MiniLM-L6-v2/snapshot \
  --model-b /absolute/path/to/all-MiniLM-L12-v2/snapshot \
  --corpus-limit 160 --query-limit 18
```

The default demo permits heuristic exploratory commits. For a fail-closed research run, instantiate `Engine(require_bounded_evidence=True)` in Python. With the present unbounded envelope this will refuse proposal and commit; the capability is an honesty gate, not a complete bounded candidate method.

An experimental `--fusion continuity` policy keeps retained A vectors available as a shadow ranking signal and gradually increases B rank weight with B membership. It converges to a pure B ranking when all documents are migrated. This adds legacy search and storage costs, departs from the frozen A-removal preview embodiment, and must be evaluated as a separate design variant. The first exploratory SciFact run preserved A quality but did not improve it; see `artifacts_private/scifact-continuity-exploratory.json`. Its held-out queries were inspected while designing the variant, so this is not independent confirmation.

## Evidence modes and completed disclosure

`serve --evidence heuristic` is the default exploratory mode. `serve --evidence strict` refuses unbounded commits. `serve --evidence exhaustive` computes and charges every current target document embedding, then permits commits satisfying declared retrieval constraints. Exhaustive coverage does not guarantee full-B-equivalent mixed results and offers no embedding-compute saving. A source update invalidates coverage until its target vector is refreshed.

Use `--fusion continuity` with a fresh database for the experimental shadow-A variant. The default RRF implementation remains the frozen-style A-removal path. Both variants use the same preview and commit checks.

The server uses packaged assets in `topopatch/web/`; `web/` is a synchronized development copy. Current regression suite (17 October 2026): 30 tests passed. See `deliverables/DEMO_GUIDE.md` for faculty presentation steps and the evidence archive for machine-readable results.


## Fresh verification - 17 October 2026

The current proof run passed 30 automated tests and 15 browser/API workflow checks.
`output/pdf/TopoPatch_IDF_B_verified_proof.pdf` replaces the two old screenshot
pages in the supplied disclosure with 11 fresh flow captures, a current verification
record and separate neural/SciFact rerun results. Historical text and experiments
remain explicitly identified as historical.

Rollback now acquires its SQLite write lock before reading commit history and
checking eligibility. Preview admission exposes strict evidence-policy refusals to
the browser, which disables commit even when rank checks alone pass. Commit still
independently revalidates policy and state.

Fresh results are in `artifacts_private/proof-2026-10-17/`. See
`deliverables/VERIFICATION_2026-10-17.md` for commands, interpretation and scope.
The source disclosure is retained as `source-disclosure.pdf` in that evidence folder.
