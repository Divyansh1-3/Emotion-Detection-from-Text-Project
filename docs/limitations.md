# Limitations

Author: Divyansh Yadav

## Sarcasm

Context, model output and lexical cues determine the sarcasm flag. Detected irony may redistribute emotion scores toward anger or disgust. Common sincere phrases such as my favorite and cannot wait require adverse context before acting as sarcasm cues. False positives and false negatives remain possible.

## Uncertainty

Flag results when confidence is below 0.40 or the leading-score margin is below 0.10. Heuristic predictions without clear emotion cues also require review. Never interpret the percentage as a guaranteed probability of correctness.

## Fallbacks

Missing models fall back to linguistic heuristics. Retrieval falls back from embeddings to TF-IDF and then keyword overlap, or empty for no corpus. Each result records the actual request backend and warnings. Health reports loaded capability; an individual query can still fail. Explanations fall back to a template. Dependencies and storage must still be available.

## Bounded explanation

The optional OpenAI-compatible client writes explanations only; it cannot change the final label. Malformed JSON gets one retry and then a template. API failures use the template. Default mock mode makes no API calls. Live provider access requires a valid independently configured key.

## Implementation scope

Flask is the chosen framework for this implementation. The supplied specification named FastAPI; this is an explicit implementation deviation. Flask provides the HTTP API and existing web interface. It does not implement FastAPI or automatic OpenAPI documentation.

Common Hindi/Hinglish phrases are normalized for the English models. 17/18 curated demonstration inputs matched their expected emotion. These examples exercise supported phrases; they do not establish general multilingual accuracy. Adapted and other non-English outputs always require review. Hindi/Hinglish sarcasm was not benchmarked.

Experimental temperature scaling uses 700 GoEmotions development examples and 350 disjoint test examples, with temperature 1.751. Validation calibration error fell from 17.4% to 4.2%; label accuracy remained 47.1%. The upstream model used GoEmotions, so training overlap is unknown. This is domain-specific calibration, not independent proof of general accuracy. Sarcasm and non-English scores remain uncalibrated.

The measured warm mean is 139.2 ms; the under-150 ms target is passed on this host. Startup, HTTP, database writes and concurrent traffic are excluded. Hosted performance needs separate measurement.
