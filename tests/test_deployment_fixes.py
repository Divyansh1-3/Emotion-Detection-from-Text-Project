"""Regression checks for export snapshots, request traces and language handling."""
import csv
import io
import json
import sqlite3
from contextlib import closing

import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.app import create_app
from backend.app.engines import retrieval, router
from backend.app.engines.preprocess import preprocess
from backend.app.engines.language_support import adapt_language


def test_export_snapshot_survives_insert_between_pages(tmp_path, monkeypatch):
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'export.db'}"})
    repo = app.extensions['results_repository']
    with closing(sqlite3.connect(repo.db_path)) as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.executemany('INSERT INTO analyses (input_text) VALUES (?)', [(f'original {i}',) for i in range(501)])
        conn.commit()
    original_export = repo.iter_export

    def export_with_insert():
        for number, record in enumerate(original_export(), 1):
            yield record
            if number == 500:
                with closing(sqlite3.connect(repo.db_path)) as conn:
                    conn.execute("INSERT INTO analyses (input_text) VALUES ('arrived during export')")
                    conn.commit()

    monkeypatch.setattr(repo, 'iter_export', export_with_insert)
    response = app.test_client().get('/api/v1/emotion/export')
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert response.status_code == 200
    assert len(rows) == len({row['id'] for row in rows}) == 501
    assert {row['confidence_method'] for row in rows} == {'uncalibrated_fusion'}
    assert repo.count() == 502


def test_retrieval_records_query_fallback_not_cached_capability(monkeypatch):
    monkeypatch.setenv('USE_MODELS', '1')
    monkeypatch.setenv('PARALLEL_INFERENCE', '0')
    corpus = [dict(text='happy celebration', label='joy', source='exemplar'),
              dict(text='sad loss', label='sadness', source='exemplar')]
    vec = TfidfVectorizer()
    matrix = vec.fit_transform([item['text'] for item in corpus])
    monkeypatch.setattr(retrieval, '_index_cache', dict(ready=True, corpus=corpus,
                        embeddings=np.eye(2), tfidf_vectorizer=vec, tfidf_matrix=matrix))

    class Embedder:
        def encode(self, texts, **kwargs):
            if 'fail' in texts[0]:
                raise RuntimeError('query failed')
            return np.array([[1., 0.]])

    monkeypatch.setattr(retrieval, '_get_embedding_model', lambda name: Embedder())
    assert retrieval.retrieve_with_backend('happy fail')[1] == 'tfidf'
    assert retrieval.retrieve_with_backend('happy')[1] == 'embeddings'
    monkeypatch.setattr(router, 'predict_emotions', lambda *a: ({'joy': 1.0}, 'transformer'))
    monkeypatch.setattr(router, 'predict_sarcasm', lambda *a: (0.0, 'heuristic'))
    result = router.execute_pipeline('I am happy but please fail this embedding query')
    assert 'retrieval_rag_tfidf' in result.route
    assert any('used tfidf' in warning for warning in result.warnings)
    assert any('Sarcasm model unavailable' in warning for warning in result.warnings)
    assert result.confidence_method == 'uncalibrated_fusion'


def test_force_reload_does_not_retain_deleted_corpus(monkeypatch):
    monkeypatch.setattr(retrieval, '_index_cache', dict(ready=True, corpus=[{'text': 'old'}],
                        embeddings=np.ones((1, 2)), tfidf_vectorizer=object(), tfidf_matrix=object()))
    monkeypatch.setattr(retrieval, 'load_corpus', lambda directory: [])
    retrieval.initialize_index(force_reload=True)
    assert retrieval.retrieve_with_backend('anything') == ([], 'empty')
    assert retrieval.retrieval_backend() == 'empty'


@pytest.mark.parametrize('text, expected, language', [
    ('Main bahut khush hoon', 'joy', 'hi-Latn'),
    ('Main bahut udaas hoon', 'sadness', 'hi-Latn'),
    ('Mujhe gussa aa raha hai', 'anger', 'hi-Latn'),
    ('Mujhe darr lag raha hai', 'fear', 'hi-Latn'),
    ('Mujhe ghin aa rahi hai', 'disgust', 'hi-Latn'),
    ('Main hairan hoon', 'surprise', 'hi-Latn'),
    ('मैं बहुत खुश हूँ', 'joy', 'hi'),
    ('मैं बहुत उदास हूँ', 'sadness', 'hi'),
    ('मुझे गुस्सा आ रहा है', 'anger', 'hi'),
    ('मुझे डर लग रहा है', 'fear', 'hi'),
])
def test_common_language_phrases_preserve_input_and_require_review(text, expected, language):
    result = router.execute_pipeline(text)
    assert result.primary_emotion == expected
    assert result.input_text == text
    assert result.language == language and result.uncertain
    assert result.confidence_method == 'uncalibrated_fusion'
    assert 'hindi_hinglish_phrase_normalization' in result.route


@pytest.mark.parametrize('text', ['Main khush nahi hoon', 'मैं खुश नहीं हूँ'])
def test_language_normalization_preserves_negation(text):
    prep = preprocess(text)
    assert 'not happy' in prep.cleaned
    assert router.execute_pipeline(text).primary_emotion != 'joy'


def test_english_main_is_not_translated():
    assert adapt_language('The main road is clear.').text == 'The main road is clear.'
    assert not adapt_language('The main road is clear.').applied


def test_unsupported_language_is_uncertain():
    result = router.execute_pipeline('Je suis vraiment heureux de revoir tous mes amis.')
    assert result.uncertain and result.confidence_method == 'uncalibrated_fusion'


def test_existing_database_schema_is_migrated(tmp_path):
    from backend.app.repositories.results_repository import ResultsRepository, _SCHEMA
    path = tmp_path / 'old.db'
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript(_SCHEMA)
        conn.execute("INSERT INTO analyses (input_text) VALUES ('existing record')")
        conn.commit()
    repo = ResultsRepository(path)
    assert repo.get(1)['confidence_method'] == 'uncalibrated_fusion'
    assert repo.get(1)['input_text'] == 'existing record'
