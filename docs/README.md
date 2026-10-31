# Transformer submission documents

The report, SRS and synopsis were revised on 1 November 2026 for application
commit `7f159b6`. Use these files for the transformer version:

- [Project report](P_098_Emotion_Detector_Documentation.docx) — six pages.
- [Software requirements specification](BTech_3rd_Year_SRS_Emotion_Detector.docx) — six pages.
- [Project synopsis](P_098_Emotion_Detector_Synopsis.docx) — one page.

All 13 rendered pages were visually checked. Academic identity, document
structure, styles and reviewer/signature fields were preserved. Matching copies
are available in the workspace's `Submission-Ready` folder.

The documents describe the two pretrained models, seven emotions, separate irony
assessment, first-use downloads and current regression results. The 91.4% emotion
and 85.7% raw irony accuracy figures come from previously reviewed development
examples, not an independent benchmark. The known dry-humor miss and unmet
150 ms inference target remain documented.

The application commit is published and its GitHub workflow passed. The owner
reported testing the updated public app successfully; independent live browser
verification remains unavailable. These revised documents accompany the current
local runtime verification in this repository.

See [deployment instructions](deployment.md), [regression evidence](transformer-evaluation.json)
and [verification status](verification.json). Earlier ZIPs and backup documents
describe historical versions and should not be used as the current submission.
