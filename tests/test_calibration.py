import json
import math

import pytest

from backend.app.engines.calibration import (temperature_scale, calibrate_scores, calibration_profile,
                                            configuration_signature, pipeline_fingerprint)


def test_temperature_preserves_label_and_normalization():
    raw = {'joy': .8, 'sadness': .15, 'anger': .05}
    fitted = temperature_scale(raw, 2)
    assert max(fitted, key=fitted.get) == 'joy'
    assert fitted['joy'] < raw['joy']
    assert sum(fitted.values()) == pytest.approx(1)
    assert all(math.isfinite(score) and score >= 0 for score in fitted.values())


@pytest.mark.parametrize('temperature', [0, -1, float('nan'), float('inf')])
def test_invalid_temperature_is_rejected(temperature):
    with pytest.raises(ValueError):
        temperature_scale({'joy': 1}, temperature)


def test_profile_is_used_only_for_eligible_matching_pipeline(tmp_path, monkeypatch):
    profile = {'schema_version': 1, 'temperature': 2, 'validation_passed': True,
               'pipeline_fingerprint': pipeline_fingerprint(), 'configuration': configuration_signature()}
    path = tmp_path / 'temperature.json'
    path.write_text(json.dumps(profile))
    monkeypatch.setenv('CALIBRATION_ENABLED', '1')
    monkeypatch.setenv('CALIBRATION_FILE', str(path))
    scores = {'joy': .8, 'sadness': .2}
    assert calibrate_scores(scores, True)[1] == 'temperature_scaled'
    assert calibrate_scores(scores, False) == (scores, 'uncalibrated_fusion')
    monkeypatch.setenv('EMOTION_MODEL', 'different-model')
    assert calibration_profile()[1] == 'incompatible'
    assert calibrate_scores(scores, True) == (scores, 'uncalibrated_fusion')


def test_bad_profile_degrades_without_breaking_analysis(tmp_path, monkeypatch):
    path = tmp_path / 'bad.json'
    path.write_text('{broken')
    monkeypatch.setenv('CALIBRATION_ENABLED', '1')
    monkeypatch.setenv('CALIBRATION_FILE', str(path))
    assert calibration_profile() == (None, 'invalid')
