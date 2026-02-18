"""Contract tests for parameter validation and processor expectations."""

import pytest
from parameters import EffectParameters


def test_effect_parameters_default_contract():
    params = EffectParameters()
    assert params.normalize_output is True
    assert params.target_peak > 0.0


def test_effect_parameters_reject_out_of_range_gain():
    with pytest.raises(Exception):
        EffectParameters(gain_db=100.0)
