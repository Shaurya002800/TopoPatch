# TopoPatch patentability and disclosure review

Reviewed on 15 October 2026 for a proposed Indian filing through VIT Vellore.

## Assessment

**The current record does not establish that TopoPatch is patentable. The largest risk is an obvious combination of known model-validation, selective-indexing and transaction techniques.** The prototype demonstrates useful control behaviour, but useful software and a successful demonstration are not enough to establish an inventive step.

This review covers the supplied disclosure, the current implementation, saved experiments, selected patent publications, research literature, VIT policy and Indian patent guidance. It is a focused screening, not an exhaustive prior-art search, a legal opinion, or a freedom-to-operate analysis. Unpublished applications, foreign-language material and unsearched patent families may matter. No rejection probability is assigned.

The revised Part B is suitable for a candid faculty discussion. I would not present the original broad efficiency claim as proven or the current document as ready-to-file patent claims.

## Issues that matter most

| Priority | Issue | What the present evidence says | Action needed |
|---|---|---|---|
| High | Inventive step and prior-art overlap | Model-specific validation before migration, selective reindexing, and atomic updates are already known. Their combination may be a predictable engineering choice. | Have the VIT attorney map the exact proposed claim to the references below and explain the interaction that would not have been obvious. Renaming familiar steps does not establish novelty. |
| High | Software exclusion under Section 3(k) | The implementation is software using standard ranking and database operations. A dashboard or a ranking rule alone is a weak basis. | Identify and support the particular technical effect on index operation. Do not merely add processor and memory language to an abstract method. |
| High for the broad claim | Intended efficiency is not demonstrated | RRF degraded held-out quality; continuity mostly preserved legacy quality without useful target progress. Exhaustive coverage costs a full B encoding pass. | Limit current statements to the observed admission-control behaviour. Test any claimed savings against a cost-matched baseline with independent queries. |
| High if included in claims | Missing enabling detail | The low-cost certified envelope and ANN topology repair from the frozen plan are absent. | Explain an implementable method with its assumptions before claiming those features, or exclude them from the current protection request. |
| Lower on the reported facts; confirm before filing | Public disclosure and priority | The user answered “no” when asked whether any part had been publicly shared. No independent history audit was performed. | Record that declaration with the faculty and keep the technical material confidential until filing advice is received. Confirm any existing application separately. |
| High, unresolved | Inventorship and entitlement | This workspace contains substantial AI-assisted implementation and drafting. Human contributions and institutional rights have not been documented here. | Record who conceived each proposed inventive feature and when. Distinguish the original frozen idea from later AI-suggested variants. Confirm inventors, applicant and assignments with VIT. |
| Material to credibility | Evidence and claim scope differ | Only declared queries are checked; the sample is small and relevance-aware. A hash is not an authenticated or immutable audit log. | Keep the limits explicit. Preserve raw results and add reproducible policy/model configuration before making broader statements. |
| Administrative, unresolved | VIT submission is incomplete as a filing package | Part B is prepared. Part A, contributor details and institutional approvals are outside the supplied material. | Complete the institutional process with the faculty and IPR Cell. Part B does not establish a patent filing date. |

The legal requirements include novelty, inventive step, industrial applicability and avoidance of excluded subject matter. A low similarity score is not one of these requirements. See [IP India patent basics](https://www.ipindia.gov.in/basics-of-patents).

## Closest references and their implications

### Model validation before migration

[US11610143B1 — Amazon](https://patents.google.com/patent/US11610143B1/en), published as a grant on 21 March 2023, describes client-specific test data used to decide whether to migrate to an updated machine-learning model; claims 1–3 include admission and refusal based on validation. This is a closer reference than those listed in the previous disclosure. It makes a broad “validate, then migrate” proposition difficult to distinguish.

The narrower question is whether a **document-level mixed A/B preview tied to source state and rechecked at commit** differs sufficiently. This review does not conclude that the reference lacks every part of that combination.

### Model-aware and selective reindexing

[US20240303516A1 — HubSpot](https://patents.google.com/patent/US20240303516A1/en), published 12 September 2024, describes re-embedding stored material through a second model pipeline, with model identifiers and selection criteria. Generic A-to-B migration and selective model routing are therefore weak novelty positions.

[US20250342179A1 — Cloudera](https://patents.google.com/patent/US20250342179A1/en), published 6 November 2025, concerns source mutations and selective vector-index updates. Claim 1 addresses updating one portion without reindexing another; claim 2 includes checksum comparisons. Source checksums plus selective reindexing should not be presented as new by themselves.

[Qdrant’s migration guide](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/) is relevant operational background. The date of the exact web revision must be established before relying on it as prior art at a particular priority date.

### Local embedding and index repair

[US20260195572A1 — Embedding Patches for Localized Improvement of Embeddings](https://patents.justia.com/patent/20260195572), published 9 July 2026, includes training a subspace-specific model and an emulation model that maps its embeddings back into the original space. TopoPatch currently combines native-space ranks without training such a mapping. This is a technical distinction to investigate, not a novelty clearance. This reference's timing must be assessed against any actual priority claim.

[SPFresh, SOSP 2023](https://ustc-mlsys.github.io/publications/spfresh-sosp-2023/) already addresses incremental in-place vector-index updates through local partition rebalancing. The TopoPatch code does not currently implement an ANN graph or a new topology repair algorithm. Its name and frozen specification should not imply that those mechanisms have been demonstrated.

### Standard transaction protection

[SQLite’s isolation documentation](https://sqlite.org/isolation.html) establishes ordinary transaction isolation, and its [atomic commit documentation](https://www2.sqlite.org/atomiccommit.html) describes all-or-nothing commit behaviour. TopoPatch uses these existing facilities. An examiner could plausibly view adding freshness checks around model validation as an ordinary combination. That is an assessment of obviousness risk, not a finding that a single reference anticipates every feature.

A granted US patent is not automatically an enforceable Indian right. Published disclosures can nevertheless be relevant prior art. Patent-family status, Indian counterparts and any commercial freedom-to-operate question need a separate search.

## Indian filing considerations

The **final 2025 CRI Guidelines**, rather than the earlier draft, discuss technical contribution beyond incidental computer use. They do not require novel hardware. They also distinguish AI-assisted work from AI-generated invention and address human inventorship. AI assistance alone does not automatically disqualify an invention; concealing its role or inventing human contributions would be inappropriate. See [official CRI Guidelines 2025](https://ipindia.gov.in/frontend/pdf/patents/guidelines/GUIDELINES%20FOR%20EXAMINATION%20OF%20COMPUTER%20RELATED%20INVENTIONS%20%28CRIs%29%20-%202025.pdf), particularly Sections 4.5.4 and 5.2.1.

A complete specification must explain how the invention works, disclose the best method known to the applicant, and support clear claims linked by a single inventive concept. A requirement such as “bound unseen competitors efficiently” is an objective, not an enabling method. See [Section 10](https://ipindia.gov.in/acts/patent-act-1970/section-10).

Public disclosure can affect novelty. The Act contains specific anticipation provisions and exceptions; their applicability depends on the circumstances. The user reports no public sharing, so no specific prior-disclosure event has been identified. The attorney should confirm that history and any prior application before filing. See [Patents Act, Sections 29–34](https://ipindia.gov.in/acts/patent-act-1970). Applicant entitlement should also be checked under [Section 6](https://www.ipindia.gov.in/acts/patent-act-1970/section-6).

**TRL 3 is not, by itself, a reason to reject a patent.** Neither a production deployment nor TRL 4 is a universal statutory filing threshold. Conversely, reaching TRL 4 does not establish novelty. Negative results undermine claims to those particular benefits; they do not automatically rule out a different, adequately disclosed technical contribution.

VIT’s policy requires Parts A and B, allows domain-expert review and presentations, and refers approved cases to a panel attorney. It also calls for systematic records of relevant experiments. The current file hashes do not replace inventor and supervisor records. See [VIT policy, pages 12–14](https://vit.ac.in/files/IPR-and-Technology-Transfer-Policy.pdf).

## Technical accuracy audit

These findings come from the current local code and saved JSON reports. They affect the scope of the disclosure; they are not all independent legal grounds for refusal.

1. **Declared-query checks are limited.** `Engine.evaluate` checks required-result ranks and an optional development-set average. The latest lexical-to-neural experiment uses only six protected queries. Passing does not prove safety for all queries, every relevant document, or each development query individually.
2. **The full-B candidate bound is missing.** The heuristic uses old/mixed results, lexical overlap and required documents. Without a justified relation between model spaces, it cannot exclude arbitrary unseen B competitors. Exhaustive mode computes all B vectors, yet proposal enumeration still uses at most 24 candidates and singleton/pair actions before its fallback bundle.
3. **The economic argument is weak.** In the strict-rank RRF sample, 80 target encodings migrated six objects and held-out nDCG fell from 0.887 to 0.526. The continuity sample retained 0.887 while migrating one object. Neither establishes a superior cost-quality trade-off.
4. **The experimental variants must remain separate.** Continuity fusion retains shadow A rankings; it is not the frozen A-removal path. Earlier reports have different splits and policies. There are no confidence intervals, cost-matched scientific baselines, or independent replications supporting a general improvement claim.
5. **Evidence is digest-checked, not tamper-proof.** The SQLite preview and event tables remain writable to a database owner. A digest detects a changed payload under its stored identifier; it does not authenticate an author or protect an attacker-controlled database. The rewrite removes “immutable” as an unqualified claim.
6. **Model identity assumes unchanged files.** `SentenceEncoder.identity` uses the snapshot directory name and dimension, not a verified content hash of every weight/configuration file. A custom directory changed in place could retain its identity. Do not claim cryptographic model provenance.
7. **Policy binding and export are incomplete.** `snapshot()` includes the development gate and fusion but not the protected-query fixture or strict-evidence flags. Commit re-evaluates current constraints, which is useful, but is not the same as binding every policy input to the preview. `export()` omits the full development-gate configuration. Reproduction needs that configuration as well as metrics.
8. **Rollback has a narrower concurrency scope.** It reads the last commit and checks the epoch before starting its write transaction. The browser server serializes requests, but this does not establish safe rollback against a separate writer interleaving between check and write. The existing cross-connection test exercises stale commit rejection, not this rollback race.
9. **Performance is not fully measured.** Logical object writes do not measure ANN graph edits, bytes written, CPU/GPU time, p95 latency or memory cost. Some evaluation work is counted separately, so encoding counts must not be relabelled as complete runtime savings.
10. **The report is a proof of concept.** Exact flat search, authored fixtures and local SQLite are legitimate experimental tools. They do not substantiate claims about distributed deployment, large-scale ANN repair, crash behaviour beyond the tested cases, or universal convergence to a safe full-B state.

## What would strengthen the case

1. Have the faculty identify the intended inventive feature and its human conception history before adding more mechanisms. Changing the prose or adding screenshots cannot resolve an obviousness objection.
2. Build a feature-by-feature comparison against Amazon validation, HubSpot migration, Cloudera selective updates and standard transaction control. Distinguish a novelty inquiry about one reference from an inventive-step inquiry that may combine teachings.
3. If the proposed contribution survives that comparison, freeze a concrete implementation and protocol. Record all policy inputs and verified model identities, and address the rollback concurrency gap before claiming that behaviour.
4. Compare against ordinary validate-then-migrate with the same source checks and transaction protection. Removing all safeguards creates an artificially weak baseline and cannot show why the particular TopoPatch combination is inventive.
5. Test on independent queries and multiple model pairs. Count discovery, preview, evaluator and serving costs separately. Report failures, overhead and uncertainty. For a reliability claim, measure failures prevented and any added latency; for a savings claim, show the same quality at lower total measured cost.
6. Ask VIT’s attorney to determine claim scope and filing timing, including whether a sufficiently detailed provisional is appropriate. Do not delay legal review solely to chase a particular TRL, and do not treat a provisional as a placeholder that protects undisclosed future mechanisms.

## Wording changes made

The revised disclosure uses shorter sentences and explains the old/new model roles before introducing the mechanism. It replaces vague “action-effect witness” language where a plain description is clearer, distinguishes preview calculation from live activation, and replaces unqualified “immutable” evidence with digest-checked records. It adds the closer references and retains every negative measurement and material limit.

The intended author voice is clear and natural. Deliberate typos and detector-oriented phrasing were not added. No plagiarism or AI-detection score has been measured or promised. Original wording does not turn a known technical idea into a patentable one.

## Open facts requiring the inventor and faculty

- First conception and reduction-to-practice dates for each proposed feature.
- Confirmation with the faculty of the user’s report that nothing has been publicly shared; any exception should include date, audience and confidentiality terms.
- Any existing provisional or complete filing and its actual contents.
- Human contributions, co-inventors, institutional resources, sponsorship and ownership agreements.
- Part A information, intended applicant, relevant countries and any filing deadlines.

The no-public-sharing statement is **user-reported**. The remaining facts are **unverified**, not presumed favourable. A patent professional should assess them alongside the technical comparison before a filing decision.

## Additional supplied patent search report

The user supplied a 38-page Questel FAMPAT export dated 2 September 2026. Its listed documents concern semantic interpretation of user interface events, human-machine interaction, GUI automation, operation logs and keyboard/mouse scripts. Those topics do not disclose the partial embedding-model migration, mixed A/B retrieval preview and source-consistent commit sequence described here, based on the titles, abstracts and claims provided in that export. It is retained as a search artifact, not cited as close prior art in IDF-B. This topical mismatch does not establish novelty; a search targeted to vector indexing and model migration remains necessary.
