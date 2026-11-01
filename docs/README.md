# Submission documents

- [Current project report](P_098_Emotion_Detector_Documentation.docx) — seven pages,
  updated for batch application commit `c751330`, with a dataset appendix.
- [Software requirements specification](BTech_3rd_Year_SRS_Emotion_Detector.docx) —
  six pages, retained from transformer revision `7f159b6`.
- [Project synopsis](P_098_Emotion_Detector_Synopsis.docx) — one page, retained
  from transformer revision `7f159b6`.

The current report records single and batch workflows, all 37 local tests,
the successful GitHub workflow and anonymous public browser checks. Every page
of the revised report was rendered and visually reviewed. Academic identity,
styles and page geometry were preserved. Existing reviewer/signature fields
in the SRS remain unfilled.

The emotion macro F1 of 0.913 and raw irony macro F1 of 0.844 come from previously
reviewed development regression examples, not an independent benchmark.
Known sarcasm errors and the unmet 150 ms inference target remain documented.

The workspace's `Submission-Ready/Final-Submission-2026-11-01` directory contains
the matching report, sourced dataset package and a source archive. The dataset
has 18,000 historical examples and 70 current regression cases; historical data
was not used to train the current pretrained models.

See [deployment instructions](deployment.md), [regression evidence](transformer-evaluation.json),
[browser checks](public-browser-verification.json) and [verification status](verification.json).
