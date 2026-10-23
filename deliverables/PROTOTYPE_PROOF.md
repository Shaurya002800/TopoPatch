# TopoPatch prototype proof record

## What was run

A fresh local run on 16 October 2026 used the authored 40-document, four-protected-query fixture, lexical A/B encoders, exact flat retrieval and SQLite. The command was:

```sh
python3 -m scripts.prove_prototype
python3 -m unittest discover -s tests -v
```

The first command writes `artifacts_private/prototype-proof-trace.json`. It asserts each transition and stops if an expected decision does not occur. The second command produced `artifacts_private/test-results.txt`: 25 tests passed. The raw JSON and transcript are included in the evidence archive.

## Observed sequence

| Step | Observation |
|---|---|
| Initial | Epoch 0; zero B-active documents; zero charged B document encodings. |
| Candidate analysis | Fourteen B document encodings charged; active membership remains zero. |
| Unsafe candidate | Moving `car-guide` fails the protected `q-policy` rank rule. The API denies commit; the state snapshot is unchanged. |
| Passing candidate | Moving `password-policy` passes all four declared rules. The preview top five for `password account policy` exactly matches the served top five after commit. |
| Commit and reopen | Epoch 1; one B-active document. Reopening the SQLite file preserves the same state snapshot. |
| Rollback | Epoch 2; zero B-active documents. The fourteen charged encodings remain counted. |
| Strict heuristic mode | Candidate evidence is labelled unbounded and the strict proposal is rejected. |
| Strict exhaustive mode | All 40 B document vectors are charged; an admissible action commits. |
| Injected write error | A SQLite trigger aborts the membership update; the transaction leaves the state snapshot unchanged. |

## How to read this proof

The trace supports the local preview, refusal, commit, persistence and rollback mechanism on the declared fixture. The browser captures in the disclosure show the interface; the JSON trace supplies independently rerunnable state assertions. The public SciFact results are separate experiments and do not follow from these screenshots.

This proof does not establish a general retrieval-quality gain, a cost advantage, ANN index repair, safety for unseen queries, production crash recovery or patentability. The candidate heuristic remains unbounded. In exhaustive mode the system pays the full target-encoding cost. These limitations are part of the evidence record.
