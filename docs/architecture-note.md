# Architecture Note

Author: Divyansh Yadav

## Models

The emotion model is j-hartmann/emotion-english-distilroberta-base. Sarcasm uses cardiffnlp/twitter-roberta-base-irony. Semantic retrieval uses sentence-transformers/all-MiniLM-L6-v2.

## Fusion

With the emotion transformer, blend model/rules/retrieval scores at 70/15/15. With heuristic rules, use 75% rules and 25% retrieval. With no rule evidence, blend the neutral heuristic and retrieval at 60/40 and require review. Fusion weights remain hand-tuned. A fitted temperature then adjusts eligible English scores without changing the leading label. Fallbacks and incompatible profiles remain explicitly uncalibrated.

## Sarcasm

Context, model output and lexical cues determine the sarcasm flag. Detected irony may redistribute emotion scores toward anger or disgust. Common sincere phrases such as my favorite and cannot wait require adverse context before acting as sarcasm cues. False positives and false negatives remain possible.

## Uncertainty

Flag results when confidence is below 0.40 or the leading-score margin is below 0.10. Heuristic predictions without clear emotion cues also require review. Never interpret the percentage as a guaranteed probability of correctness.

## Storage

The standard sqlite3 repository stores analyses synchronously. JSON arrays hold scores, sources, routes, engines and warnings. There is no ORM, PostgreSQL adapter, immutable audit ledger or automatic WAL configuration.

## Execution

After preprocessing and rules, a bounded three-worker pool runs both classifiers and retrieval concurrently. Fusion waits for their results. PARALLEL_INFERENCE=0 disables this optimization. Model singletons avoid repeated loading; models and language detection warm before requests. Two PyTorch threads are the default. The environment file is read once per process; restart after configuration changes.

## Fallbacks

Missing models fall back to linguistic heuristics. Retrieval falls back from embeddings to TF-IDF and then keyword overlap, or empty for no corpus. Each result records the actual request backend and warnings. Health reports loaded capability; an individual query can still fail. Explanations fall back to a template. Dependencies and storage must still be available.

## Implementation scope

Flask is the chosen framework for this implementation. The supplied specification named FastAPI; this is an explicit implementation deviation. Flask provides the HTTP API and existing web interface. It does not implement FastAPI or automatic OpenAPI documentation.

Common Hindi/Hinglish phrases are normalized for the English models. 17/18 curated demonstration inputs matched their expected emotion. These examples exercise supported phrases; they do not establish general multilingual accuracy. Adapted and other non-English outputs always require review. Hindi/Hinglish sarcasm was not benchmarked.

Experimental temperature scaling uses 700 GoEmotions development examples and 350 disjoint test examples, with temperature 1.751. Validation calibration error fell from 17.4% to 4.2%; label accuracy remained 47.1%. The upstream model used GoEmotions, so training overlap is unknown. This is domain-specific calibration, not independent proof of general accuracy. Sarcasm and non-English scores remain uncalibrated.

The measured warm mean is 139.2 ms; the under-150 ms target is passed on this host. Startup, HTTP, database writes and concurrent traffic are excluded. Hosted performance needs separate measurement.
