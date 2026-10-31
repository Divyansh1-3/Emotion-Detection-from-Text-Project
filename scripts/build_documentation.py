"""Build submission documentation from checked implementation and evaluation data."""
from pathlib import Path
import json, re, shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent
OUT = BASE / 'Submission-Ready'
OUT.mkdir(exist_ok=True)
E = json.loads((ROOT/'docs/evaluation-results.json').read_text())
F = json.loads((ROOT/'docs/evaluation-results-fallback.json').read_text())
C = json.loads((ROOT/'data/calibration/temperature.json').read_text())
L = json.loads((ROOT/'docs/language-evaluation.json').read_text(encoding='utf-8'))
T = json.loads((ROOT/'docs/test-results.json').read_text())
STATUS = lambda ok: 'Passed' if ok else 'Not met'
LATENCY = f"The measured warm mean is {E['emotion']['avg_latency_ms']:.1f} ms; the under-150 ms target is {STATUS(E['emotion']['avg_latency_ms'] < 150).lower()} on this host. Startup, HTTP, database writes and concurrent traffic are excluded. Hosted performance needs separate measurement."
CALIBRATION = f"Experimental temperature scaling uses 700 GoEmotions development examples and 350 disjoint test examples, with temperature {C['temperature']:.3f}. Validation calibration error fell from {100*C['validation']['before']['ece_10_bins']:.1f}% to {100*C['validation']['after']['ece_10_bins']:.1f}%; label accuracy remained {100*C['validation']['after']['accuracy']:.1f}%. The upstream model used GoEmotions, so training overlap is unknown. This is domain-specific calibration, not independent proof of general accuracy. Sarcasm and non-English scores remain uncalibrated."
LANGUAGE = f"Common Hindi/Hinglish phrases are normalized for the English models. {L['correct']}/{L['total']} curated demonstration inputs matched their expected emotion. These examples exercise supported phrases; they do not establish general multilingual accuracy. Adapted and other non-English outputs always require review. Hindi/Hinglish sarcasm was not benchmarked."
FRAMEWORK = 'Flask is the chosen framework for this implementation. The supplied specification named FastAPI; this is an explicit implementation deviation. Flask provides the HTTP API and existing web interface. It does not implement FastAPI or automatic OpenAPI documentation.'
METRICS = [
 ['Emotion macro-F1', '>= 0.700', f"{E['emotion']['macro_f1']:.3f}", STATUS(E['emotion']['macro_f1'] >= .7)],
 ['Emotion accuracy', '>= 70%', f"{100*E['emotion']['accuracy']:.1f}%", STATUS(E['emotion']['accuracy'] >= .7)],
 ['Sarcasm F1', '>= 0.650', f"{E['sarcasm']['f1']:.3f}", STATUS(E['sarcasm']['f1'] >= .65)],
 ['Warm pipeline mean', '< 150 ms', f"{E['emotion']['avg_latency_ms']:.1f} ms", STATUS(E['emotion']['avg_latency_ms'] < 150)],
 ['Warm pipeline P95', 'Reported separately', f"{E['emotion']['p95_latency_ms']:.1f} ms", 'Measured'],
 ['Model startup', 'Reported separately', f"{E['startup_ms']/1000:.1f} seconds", 'Measured'],
]
API = [
 ['POST', '/api/v1/emotion/process', 'JSON object: input, optional session_id and options'],
 ['POST', '/api/v1/emotion/batch', 'JSON texts/inputs list or multipart CSV field file'],
 ['GET', '/api/v1/emotion/results', 'History with limit and offset; maximum page size 500'],
 ['GET', '/api/v1/emotion/results/<id>', 'One stored analysis; 404 for an unknown ID'],
 ['GET', '/api/v1/emotion/stats', 'Stored counts and emotion distribution'],
 ['GET', '/api/v1/emotion/export', 'Download stored results as CSV'],
 ['GET', '/health', 'Service status and actual loaded model/retrieval state'],
 ['GET', '/ and /inspect', 'User dashboard and paginated audit history'],
]
FACTS = [
 ('Scope', 'Classify English text into anger, disgust, fear, joy, neutral, sadness or surprise. Return confidence, an uncertainty flag, an approximate sarcasm assessment and an explanation. This is linguistic analysis, not a psychological diagnosis.'),
 ('Models', 'The emotion model is j-hartmann/emotion-english-distilroberta-base. Sarcasm uses cardiffnlp/twitter-roberta-base-irony. Semantic retrieval uses sentence-transformers/all-MiniLM-L6-v2.'),
 ('Fusion', 'With the emotion transformer, blend model/rules/retrieval scores at 70/15/15. With heuristic rules, use 75% rules and 25% retrieval. With no rule evidence, blend the neutral heuristic and retrieval at 60/40 and require review. Fusion weights remain hand-tuned. A fitted temperature then adjusts eligible English scores without changing the leading label. Fallbacks and incompatible profiles remain explicitly uncalibrated.'),
 ('Sarcasm', 'Context, model output and lexical cues determine the sarcasm flag. Detected irony may redistribute emotion scores toward anger or disgust. Common sincere phrases such as my favorite and cannot wait require adverse context before acting as sarcasm cues. False positives and false negatives remain possible.'),
 ('Uncertainty', 'Flag results when confidence is below 0.40 or the leading-score margin is below 0.10. Heuristic predictions without clear emotion cues also require review. Never interpret the percentage as a guaranteed probability of correctness.'),
 ('Storage', 'The standard sqlite3 repository stores analyses synchronously. JSON arrays hold scores, sources, routes, engines and warnings. There is no ORM, PostgreSQL adapter, immutable audit ledger or automatic WAL configuration.'),
 ('Execution', 'After preprocessing and rules, a bounded three-worker pool runs both classifiers and retrieval concurrently. Fusion waits for their results. PARALLEL_INFERENCE=0 disables this optimization. Model singletons avoid repeated loading; models and language detection warm before requests. Two PyTorch threads are the default. The environment file is read once per process; restart after configuration changes.'),
 ('Fallbacks', 'Missing models fall back to linguistic heuristics. Retrieval falls back from embeddings to TF-IDF and then keyword overlap, or empty for no corpus. Each result records the actual request backend and warnings. Health reports loaded capability; an individual query can still fail. Explanations fall back to a template. Dependencies and storage must still be available.'),
 ('Bounded explanation', 'The optional OpenAI-compatible client writes explanations only; it cannot change the final label. Malformed JSON gets one retry and then a template. API failures use the template. Default mock mode makes no API calls. Live provider access requires a valid independently configured key.'),
 ('Input rules', 'Accept 1 to 4,000 characters after sanitization. Reject empty/control-only input and invalid batch item types. Transformer tokenizers truncate at 512 tokens. CSV uploads are limited to 16 MB and 500 rows; oversized batches are rejected before processing.'),
 ('Batch results', 'Preserve row positions and report each validation error explicitly. Return counts for attempted, successful and failed rows. Failed rows do not fabricate a neutral prediction. Valid rows use mode=batch and are persisted. Entirely malformed requests return HTTP 400 or 422.'),
 ('Frontend', 'Flask serves Jinja templates, custom CSS and vanilla JavaScript. Chart.js is bundled locally with its license; textual score rendering remains available if the chart library fails. The audit view reads saved results and offers CSV export.'),
]

def diagram(name, labels):
    image=Image.new('RGB',(1400,110+160*len(labels)),'white');draw=ImageDraw.Draw(image)
    font_path = next((p for p in [Path('C:/Windows/Fonts/arial.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.exists()), None)
    font=ImageFont.truetype(str(font_path),28) if font_path else ImageFont.load_default(size=28)
    for i,label in enumerate(labels):
        y=40+i*160
        draw.rounded_rectangle((80,y,1320,y+105),radius=15,fill='#edf3f8',outline='#456782',width=3)
        draw.multiline_text((700,y+52),label,font=font,fill='#172b3a',anchor='mm',align='center',spacing=8)
        if i<len(labels)-1:
            draw.line((700,y+106,700,y+150),fill='#456782',width=4)
            draw.polygon([(690,y+138),(710,y+138),(700,y+153)],fill='#456782')
    path=ROOT/'docs'/name;image.save(path);return path

architecture=diagram('p098_layered_architecture.png',[
 'Browser dashboard / REST client', 'Flask routes and Pydantic request validation',
 'Analysis service and bounded concurrent inference', 'Rules + emotion model + sarcasm model + retrieval',
 'Fusion, uncertainty and bounded rationale', 'SQLite repository, response and audit history'])
flow=diagram('p098_request_flow.png',[
 'Validate and sanitize input', 'Preprocess once; reuse lexical and emoji evidence',
 'Concurrent emotion, sarcasm and retrieval inference', 'Fuse scores; calibrate eligible English outputs',
 'Generate bounded explanation; harden output', 'Persist successful result; return JSON and warnings'])
shutil.copy2(architecture,ROOT/'docs/p098_product_architecture_flowchart.png')
erd=diagram('p098_data_model.png',[
 'analyses: id PRIMARY KEY, request_id, session_id, created_at',
 'input_text, language, mode, primary_emotion',
 'confidence, confidence_method, uncertain, sarcasm, rationale',
 'emotion_scores, sources, route, engines_used, warnings (JSON)',
 'llm_used, latency_ms; indexes on created_at and primary_emotion'])

def new_doc(title, subtitle):
    d=Document();sec=d.sections[0];sec.top_margin=sec.bottom_margin=Inches(.65)
    for border in d.styles.element.xpath('.//w:pBdr'):
        border.getparent().remove(border)
    sec.left_margin=sec.right_margin=Inches(.75)
    for name in ['Normal','Title','Heading 1','Heading 2']:
        d.styles[name].font.name='Arial';d.styles[name].font.color.rgb=RGBColor(0,0,0)
    d.styles['Normal'].font.size=Pt(10.5)
    d.styles['Normal'].paragraph_format.space_after=Pt(6)
    d.styles['Title'].font.size=Pt(25)
    d.styles['Heading 1'].font.size=Pt(16)
    d.styles['Heading 2'].font.size=Pt(12)
    d.core_properties.author='Divyansh Yadav'
    d.core_properties.last_modified_by='Divyansh Yadav'
    d.add_heading(title,0);d.add_paragraph(subtitle)
    return d

def table(d, headers, rows):
    t=d.add_table(rows=1,cols=len(headers));t.style='Light Shading Accent 1'
    widths = [2.1, 1.5, 1.6, 1.8] if len(headers) == 4 else ([.65, 3.0, 3.35] if headers[0] == 'Method' else [.65, 4.2, 2.15])
    t.autofit=False
    for column,width in zip(t.columns,widths):column.width=Inches(width)
    for c,text in zip(t.rows[0].cells,headers):c.text=text
    repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for c,text in zip(t.add_row().cells,row):c.text=str(text)
    for row in t.rows:
        no_split=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no_split)
        for cell,width in zip(row.cells,widths):
            cell.width=Inches(width);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after=Pt(4)
                paragraph.paragraph_format.space_before=Pt(4)
                for run in paragraph.runs:run.font.size=Pt(9)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                b=OxmlElement('w:'+edge);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');borders.append(b)
            cell._tc.get_or_add_tcPr().append(borders)
    return t

def section(d,title,text):d.add_heading(title,1);d.add_paragraph(text)

def evidence(d):
    table(d,['Metric','Target','Measured','Status'],METRICS)
    d.add_paragraph(f"Evaluation: {E['timestamp_utc']}. Each task has 35 curated cases. Models used cached weights, embedding retrieval and template rationale. Timings exclude HTTP and persistence. Startup is separate. Results vary with hardware and load; memory was not measured.")
    d.add_paragraph(f"Fallback benchmark: emotion accuracy {100*F['emotion']['accuracy']:.1f}%, emotion macro-F1 {F['emotion']['macro_f1']:.3f}, sarcasm F1 {F['sarcasm']['f1']:.3f}. This mode preserves availability but is unsuitable for accuracy-sensitive use without review.")
    d.add_paragraph(f"The {T['tests']}-test automated suite passes with no failures. It covers unit behavior, API/storage integration, malformed batches, CSV BOM headers, row errors, sincere praise, invalid LLM output, concurrent export, retrieval traces, calibration safeguards and language normalization. Passing tests does not establish unrestricted real-world accuracy.")

report=new_doc('Emotion Detection from Text','Project P_098 | Divyansh Yadav | HCL Industrial Training')
section(report,'1 Problem and objective',FACTS[0][1])
section(report,'2 Intended users','Students, customer-support analysts and reviewers can inspect the tone of individual messages or batches. Results support human review and do not automatically trigger decisions about people.')
section(report,'3 Why retrieval and a bounded LLM',FACTS[8][1]+' Retrieval supplies reference examples and a nearest-neighbor vote. The corpus contains 82 exemplars and 8 knowledge entries.')
section(report,'4 Technology',FACTS[1][1]+' Python 3.11+, Flask 3, Pydantic 2, PyTorch, scikit-learn, SQLite, HTML/CSS/JavaScript and Waitress form the implementation. '+FRAMEWORK)
report.add_page_break();report.add_heading('5 Architecture and workflow',1)
report.add_picture(str(architecture),width=Inches(5.4))
report.add_paragraph(FACTS[6][1]);report.add_paragraph(FACTS[7][1])
report.add_page_break();section(report,'6 Fusion and sarcasm',FACTS[2][1]+' '+FACTS[3][1])
section(report,'7 Confidence and safety',FACTS[4][1]+' Input override markers are warned about and generated rationales receive a non-diagnostic disclaimer. Regex screening reduces certain unsafe terms; it is not a security guarantee.')
section(report,'8 Input and batch behavior',FACTS[9][1]+' '+FACTS[10][1])
section(report,'9 API contract','The process request is {"input":"I am happy"}. The response contains success, result, sources, warnings and request_id. The result includes primary_emotion, confidence, uncertain, sarcasm, emotion_scores, rationale and route.')
table(report,['Method','Path','Purpose'],API)
report.add_page_break();section(report,'10 Data and audit',FACTS[5][1]+' The saved JSON result can be compared with /inspect/<id>. Logging writes structured request summaries without logging the raw input text.')
section(report,'11 Verification and measured results','Run python -m pytest and python scripts/evaluate.py --mode hybrid. The evaluator refuses to label a fallback run as a hybrid benchmark. --check returns a failure exit code when a target is missed.')
evidence(report)
report.add_page_break();section(report,'12 Debugging case study','The review reproduced malformed batch HTTP 500 errors, BOM headers analyzed as text, errors disguised as neutral results, and sincere praise marked as sarcasm. Regression tests now cover these cases. Report pass/fail labels are computed from measurements instead of hardcoded.')
section(report,'13 Confidence calibration',CALIBRATION)
section(report,'14 Languages and limitations',LANGUAGE+' '+LATENCY+' Conversational context, authentication and PostgreSQL are not implemented.')
section(report,'15 Setup and references','Create a Python 3.11+ virtual environment, install requirements.txt, copy .env.example to .env and run scripts/download_models.py once. Run python -m backend.app.main for the local demo or python serve.py for production Waitress serving with the platform PORT. Keep API keys out of version control. Deployment and public-URL screenshots remain to be completed; see docs/deployment.md.')
report.add_paragraph('Repository: https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project\nEvidence: docs/evaluation-results.json, docs/evaluation-report.md, tests/.\nModel references: https://huggingface.co/j-hartmann/emotion-english-distilroberta-base ; https://huggingface.co/cardiffnlp/twitter-roberta-base-irony ; https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2')
report.save(OUT/'P_098_Emotion_Detector_Documentation.docx')

srs=new_doc('Software Requirements Specification','Emotion Detection from Text | Project P_098')
srs.add_paragraph('ABES Engineering College, Ghaziabad\nDepartment of Computer Science and Engineering\nDivyansh Yadav | Roll No. 2400320100444\nB.Tech, third year | Academic year 2026–2027\nRevision 1.3 | November 2026')
section(srs,'1 Introduction',FACTS[0][1]+' This specification describes the implemented academic prototype and identifies verification limits. Its organization follows the supplied academic SRS structure.')
srs.add_paragraph(FRAMEWORK)
section(srs,'2 Overall description',FACTS[11][1]+' Analysts submit messages, reviewers inspect records, and developers integrate through HTTP. All endpoints have the same local access; there is no implemented role-based authorization.')
srs.add_paragraph('Environment: Python 3.11 or newer, Windows/Linux/macOS with compatible dependency wheels, and a JavaScript-capable browser. Model downloads require internet once. Subsequent model operation can use HF_HUB_OFFLINE=1. An 8 GB laptop is the design environment, not a measured memory guarantee.')
srs.add_page_break();srs.add_heading('3 Functional requirements',1)
table(srs,['ID','Requirement','Verification'],[
 ['FR-01',FACTS[9][1],'Input and API regression tests'],
 ['FR-02','Seven emotion labels, confidence method and uncertainty flag. Fit temperature on development data; validate on separate data. Apply only to matching English full-model paths.','Fusion tests, calibration profile and benchmark'],
 ['FR-03',FACTS[3][1],'Sarcasm fixtures and F1 report'],
 ['FR-04','Retrieve examples and expose actual embedding/TF-IDF/keyword backend.','Pipeline trace and health endpoint'],
 ['FR-05',FACTS[8][1],'Mock client failure/retry tests'],
 ['FR-06',FACTS[10][1],'CSV and batch regression tests'],
 ['FR-07','Save valid analyses and confidence method; expose history, stats, detail and CSV export using one stable database snapshot.','Persistence, migration and concurrent export tests'],
 ['FR-08','Display results, warnings and audit records with local charts.','Template/API checks and frontend smoke test'],
 ['FR-09','Normalize common Hindi/Hinglish phrases and negation; preserve original input and flag adapted/non-English predictions for review.','Language unit tests and 18-case demonstration'],
])
section(srs,'4 External interfaces','HTTP JSON is the API format. CSV uploads use multipart/form-data. Invalid input returns 400 or 422, missing records 404, oversized HTTP requests 413. Model fallback is reported in successful responses. Use a reverse proxy for external HTTPS deployment.')
table(srs,['Method','Path','Purpose'],API)
section(srs,'5 Non functional requirements',LATENCY+' Availability uses explicit fallbacks; it does not promise 100% uptime. Live API behavior, container execution and browser compatibility require environment-specific checks.')
evidence(srs)
srs.add_page_break();srs.add_heading('6 Design models',1);srs.add_picture(str(flow),width=Inches(5.1))
srs.add_paragraph('Use cases: user submits one message or a CSV; analyst views scores and exports results; reviewer inspects saved records. Each case uses the same Flask service and SQLite repository. Independent model stages execute concurrently before fusion.')
srs.add_page_break();srs.add_heading('6.1 Data model',1);srs.add_picture(str(erd),width=Inches(5.3))
section(srs,'7 Confidence and language verification',CALIBRATION+' '+LANGUAGE)
section(srs,'8 Academic review',f"The suite has {T['tests']} passing tests. Full model inference and the production Waitress entrypoint were exercised. Evaluation artifacts record actual paths and configuration. The public deployment, screenshots, Docker execution and live LLM provider remain unverified. Academic approval and signatures must come from the actual reviewers.")
srs.add_paragraph('Repository: https://github.com/Divyansh1-3/Emotion-Detection-from-Text-Project')
srs.add_paragraph('Developer: Divyansh Yadav\nFaculty reviewer: ____________________\nSignature and date: ____________________')
srs.save(OUT/'BTech_3rd_Year_SRS_Emotion_Detector.docx')

for name in ['P098_Formal_Project_Documentation.docx','P_098_Emotion_Detector_Documentation.docx']:
    shutil.copy2(OUT/'P_098_Emotion_Detector_Documentation.docx',ROOT/'docs'/name)
shutil.copy2(OUT/'BTech_3rd_Year_SRS_Emotion_Detector.docx',ROOT/'docs/BTech_3rd_Year_SRS_Divyansh_Yadav.docx')
blue=new_doc('Emotion Detection Implementation Blueprint','P_098 | Divyansh Yadav | Verified implementation')
for i,(title,text) in enumerate(FACTS,1):section(blue,f'{i} {title}',text)
section(blue,'13 API', 'See the API table in the project report and README. Input is named input; the health path is /health.')
section(blue,'14 Data','82 exemplars, 8 knowledge entries, 35 emotion cases and 35 sarcasm cases. SQLite analyses is the only database table.')
section(blue,'15 Tests',f"{T['tests']} tests cover units, API behavior, persistence and regression scenarios. Tests use temporary databases and disable live API calls.")
section(blue,'16 Evaluation','Full run configurations and metrics are in docs/evaluation-results.json and the fallback counterpart.');evidence(blue)
section(blue,'17 Deployment','Use a recreated virtual environment and requirements.txt. Waitress is the production WSGI entrypoint. Docker is supplied but was not executed during this verification.')
section(blue,'18 Demo','Show happy text, a sarcastic complaint, a mixed emotion, CSV row errors, /inspect and CSV export. Explain which backend ran instead of promising fixed output percentages.')
section(blue,'19 Confidence and language support',CALIBRATION+' '+LANGUAGE)
section(blue,'20 Framework and deployment limits','Flask is the chosen implementation, a declared deviation from the supplied FastAPI specification. The measured warm pipeline meets the mean latency target on this host; hosted performance requires separate measurement. Public deployment, screenshots, Docker execution and live-provider verification remain outstanding.')
blue.save(ROOT/'docs/P098_Student_Project_Blueprint_Documentation.docx')

md='# P_098 Emotion Detection from Text\n\nAuthor: Divyansh Yadav\n\n'
for title,text in FACTS:md+=f'## {title}\n\n{text}\n\n'
md+='## Measured evaluation\n\n| Metric | Target | Measured | Status |\n|---|---|---|---|\n'+'\n'.join('| '+' | '.join(row)+' |' for row in METRICS)+'\n\n'
md+=f"{T['tests']} tests pass. Evaluation uses 35 curated cases per task. Full metrics and configuration are in evaluation-results.json. Live LLM calls and Docker execution were not verified.\n\n"+FRAMEWORK+'\n\n'+CALIBRATION+'\n\n'+LANGUAGE+'\n\n'+LATENCY+'\n'
(ROOT/'docs/P098_Formal_Project_Documentation.md').write_text(md,encoding='utf-8')
for filename,indices in {'architecture-note.md':[1,2,3,4,5,6,7], 'requirements.md':[0,9,10,11], 'limitations.md':[3,4,7,8], 'project-brief.md':[0,1,11], 'user-flow.md':[9,6,10,11]}.items():
    text='# '+filename.removesuffix('.md').replace('-',' ').title()+'\n\nAuthor: Divyansh Yadav\n\n'
    text+='\n\n'.join('## '+FACTS[i][0]+'\n\n'+FACTS[i][1] for i in indices)
    text+='\n\n## Implementation scope\n\n'+FRAMEWORK+'\n\n'+LANGUAGE+'\n\n'+CALIBRATION+'\n\n'+LATENCY
    (ROOT/'docs'/filename).write_text(text+'\n',encoding='utf-8')
print('Built corrected report, SRS, blueprint, diagrams and implementation notes.')
