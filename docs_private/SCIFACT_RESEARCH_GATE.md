# SciFact research gate

Date: 15 October 2026

The IDF-B supplied by the inventor asks for experimental validation, drawings or photographs, and technology readiness evidence. The current evidence establishes a working software control loop, but the public-data result does not establish the proposed savings at comparable retrieval quality.

## Reproducible experiment

Source: BEIR SciFact, https://github.com/beir-cellar/beir and https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip. Source ZIP SHA-256: `536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165`. The local source copy is `data/scifact.zip`.

A fixed seed sampled 18 SciFact test queries. Six served as protected control queries, and twelve served as held-out evaluation queries. All judged relevant articles for those queries were retained, then random distractors were added to reach 160 articles. This relevance-aware corpus is easier than the complete SciFact benchmark and cannot be presented as a BEIR leaderboard score. The two actual encoder models were all-MiniLM-L6-v2 and all-MiniLM-L12-v2, loaded from immutable local snapshot directories. Their full identities and all query IDs are in the JSON evidence.

The result is in `artifacts_private/scifact-research.json`. TopoPatch discovered 61 B vectors, committed one, and preserved all six registered constraints. The current selective state's held-out nDCG@10 was **0.5771**. The original A index was **0.8874**; full B was **0.8933**. A separate offline full-B reference encoded 160 documents and was excluded from the algorithm's charged work. The candidate envelope missed **0.20** of the true full-B top-10 items on protected queries. This is a negative result for the proposed quality-at-lower-cost hypothesis.

The current default demo operates in heuristic research mode and labels its envelope `HEURISTIC_UNBOUNDED`. An opt-in strict mode (`Engine(require_bounded_evidence=True)`) now fails closed and rejects both proposal and commit because no certified envelope is implemented. The strict-mode test passes. A patent submission must not describe the heuristic mode as bounded or production safe.

## Next engineering gate

1. Replace the current rank fusion behavior with a measured mixed-serving strategy that avoids large quality loss when only a few target vectors are active. Preserve separate native spaces and evaluate it on development queries before touching the held-out set.
2. Design a candidate acquisition method with a defensible exclusion bound, or explicitly narrow the claimed guarantee to a measured statistical scope. Record ground-truth miss curves as envelope size changes.
3. Repeat on the full SciFact corpus with disjoint selection, validation, and test queries, several seeds, a no-barrier ablation, equal total B-computation baselines, latency, physical writes, and storage use.
4. Only after those results show a credible technical benefit should the IDF-B experimental-validation and TRL boxes be filled as a patent-strength disclosure. A professional claim chart is still required to assess novelty and inventive step.

This file records a research gate, not a legal determination of patentability.
