# Research decision after first public dataset

The frozen specification expects a candidate envelope whose uncertainty can be bounded and a selective state with retrieval quality close to full B at materially lower total B work. The implemented heuristic currently has no rigorous exclusion bound. In strict mode it therefore denies durable migration.

The first public SciFact result showed 0.577 held-out nDCG@10 for the original RRF mixed state versus 0.887 for A and 0.893 for B, after 61 charged B document encodings to commit one object. This is a substantive contradiction of the project's initial quality-and-cost hypothesis under that serving policy.

A separately implemented continuity-weighted variant kept the old-model ranking as a shadow signal. On the same exploratory split, it retained 0.887 held-out nDCG@10, with the same 61 charged B encodings. It preserved quality but produced no measured quality gain. It is an alternative embodiment and must not silently replace the frozen A-removal claim.

The work now needs an independent validation split, cost-matched comparisons, and a bounded or honestly statistical candidate acquisition method. The VIT IDF-B technical description could accurately describe the mechanism today, but Section 8 cannot honestly state that its intended efficiency and quality benefit has been experimentally validated. Do not infer patentability from a passing protected-query test or from the dashboard.

## Further implementation and experiments

An independent lexical candidate source was added to the old-index retrieval envelope. An optional continuity-weighted native-space fusion policy was also tested. It retains the old vector as a shadow ranking signal while the object's active representation is B. That makes it a distinct embodiment from the frozen A-removal query path and adds temporary storage and query work.

On the original 160-document MiniLM L6 to L12 sample, this variant preserved old-index quality at 0.887 nDCG@10, but did not improve toward full B (0.893). It encoded 80 target documents and committed one. The envelope still missed 15% of full-B top-10 items on protected queries. A separate sampled seed produced 1.0 legacy nDCG, an unusually easy set that is weak confirmation. These are exploratory results, not evidence of a superior cost-quality frontier.

With stricter rank-preservation constraints, the frozen-style RRF path rejected 300 candidate previews and then admitted a six-object bundle. Held-out nDCG remained poor at 0.526. This demonstrates that protected-query safety can alter decisions, while also showing that the protected set is too small to secure broad quality.

A development-query quality floor was added to the barrier. Development and held-out queries are now separate. On an easier-to-distinguish lexical-to-MiniLM-L12 upgrade, A nDCG@10 was 0.384 and full B was 0.898, but the one-object selective state stayed at 0.384 after 83 target encodings. The candidate envelope missed 28% of full-B top-10 items on protected queries. This is a failed progress gate for the economic claim despite a much stronger target model.

There is a fundamental limitation: without evaluating an unseen object's B embedding or imposing a justified relation between A and B spaces, old-model and lexical retrieval alone cannot provide a deterministic bound excluding that object from B's top-k. The specification's bounded-envelope requirement needs an additional verifiable assumption, an exhaustive B computation, or a narrower statistical guarantee. Until that is resolved, strict mode correctly refuses durable migration.


## Exhaustive fallback implemented 15 October 2026

An explicit exhaustive evidence mode now materializes all current-source B embeddings and allows strict commits after coverage and retrieval checks. The 40-object fixture charges 40 B encodings. This resolves candidate coverage at full cost; it does not establish the intended selective efficiency or full-B-equivalent mixed ranking. The IDF-B is completed with this distinction and with the negative public-data results retained.
