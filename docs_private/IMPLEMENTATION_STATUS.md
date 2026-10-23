# Implementation evidence and remaining research

Date: 15 October 2026

The runnable prototype implements native-space retrieval, a heuristic candidate envelope, counterfactual action effects, immutable identified previews, exact registered-query checks, transactional guarded commits, source invalidation, rollback, validated legacy fallback, reproducible benchmarks, and a browser dashboard. Twenty-two automated tests cover functional and failure paths. A real MiniLM L6 to L12 model-pair evaluation on a relevance-aware SciFact sample was also exercised. The negative results and alternative serving tests are detailed in SCIFACT_RESEARCH_GATE.md and RESEARCH_DECISION.md.

## Evidence captured

- `artifacts_private/test-results.txt`: automated test output.
- `artifacts_private/benchmark.json`: default single-step benchmark and all action witnesses.
- `artifacts_private/neural_target_benchmark.json`: lexical-to-MiniLM experiment with actual model identity.
- `artifacts_private/trajectory.json`: full 40-document migration history.
- `artifacts_private/scifact-research.json`: public-data neural model-pair experiment.
- `artifacts_private/unsafe-preview.jpg`: UI inspection of a rejected migration.
- `artifacts_private/committed-state.jpg`: UI after the inspected safe commit.

Screenshots illustrate behavior. JSON history and tests support the factual claims. The fixture was authored for software testing, and neither its scale nor its quality results support production claims.

## Requirements not yet demonstrated

1. A rigorous exclusion bound for the candidate envelope. The current method cannot certify that unseen target-model competitors are absent; that part of the proposed mechanism remains a research gap.
2. Selective migration that approaches full-B quality while reducing total computation at equal quality. The first-step measured overlap is worse than legacy for the lexical fixture. A safe state must not be described as a successful quality upgrade.
3. Two independently trained neural models on a published retrieval corpus with relevance judgments, disjoint selection/progress/test queries and multiple seeds.
4. ANN backend integration and measured local repair costs. Exact search is implemented; graph topology claims remain untested.
5. Equal total embedding-budget baselines, no-barrier ablation, latency distributions, physical write/storage accounting, and scale measurements.
6. A substantive claim-level prior-art search and faculty review. No patentability score or grant prediction is supported by this implementation.

The project is a working functional research prototype. It is not completion of every mechanism in the master specification. TRL must be assessed from validated evidence and the intended technology scope; no TRL 4 declaration is made here. The faculty's exact template remains absent and has not been filled. The final disclosure should describe the implemented embodiment and its measured limitations without manufactured results or intentional spelling mistakes.


## Final disclosure package 15 October 2026

The completed VIT IDF-B and editable continuation are in `deliverables/`. The package describes an implemented TRL 3 proof of concept, not completion of all research requirements in the frozen specification. Exhaustive evidence mode now resolves candidate coverage by encoding all current sources, charges the full cost, and permits strict commits that pass the declared barrier. Source changes invalidate this coverage and clear previously validated fallback routes. The efficient bounded-envelope method and ANN topology mechanism remain unimplemented. Historical notes above describe earlier stages.
