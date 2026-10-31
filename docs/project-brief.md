# Project Brief

Author: Divyansh Yadav

## Scope

Classify English text into anger, disgust, fear, joy, neutral, sadness or surprise. Return confidence, an uncertainty flag, an approximate sarcasm assessment and an explanation. This is linguistic analysis, not a psychological diagnosis.

## Models

The emotion model is j-hartmann/emotion-english-distilroberta-base. Sarcasm uses cardiffnlp/twitter-roberta-base-irony. Semantic retrieval uses sentence-transformers/all-MiniLM-L6-v2.

## Frontend

Flask serves Jinja templates, custom CSS and vanilla JavaScript. Chart.js is bundled locally with its license; textual score rendering remains available if the chart library fails. The audit view reads saved results and offers CSV export.

## Implementation scope

Flask is the chosen framework for this implementation. The supplied specification named FastAPI; this is an explicit implementation deviation. Flask provides the HTTP API and existing web interface. It does not implement FastAPI or automatic OpenAPI documentation.

Common Hindi/Hinglish phrases are normalized for the English models. 17/18 curated demonstration inputs matched their expected emotion. These examples exercise supported phrases; they do not establish general multilingual accuracy. Adapted and other non-English outputs always require review. Hindi/Hinglish sarcasm was not benchmarked.

Experimental temperature scaling uses 700 GoEmotions development examples and 350 disjoint test examples, with temperature 1.751. Validation calibration error fell from 17.4% to 4.2%; label accuracy remained 47.1%. The upstream model used GoEmotions, so training overlap is unknown. This is domain-specific calibration, not independent proof of general accuracy. Sarcasm and non-English scores remain uncalibrated.

The measured warm mean is 139.2 ms; the under-150 ms target is passed on this host. Startup, HTTP, database writes and concurrent traffic are excluded. Hosted performance needs separate measurement.
