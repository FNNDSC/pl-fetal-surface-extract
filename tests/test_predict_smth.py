"""
Property testing would be coolio!
"""

from extract_cp.predict_smth import predict_aom


def test_curve():
    assert predict_aom(0.25, 0.10) < predict_aom(0.25, 0.07)


def test_no_smoothing_needed():
    assert predict_aom(0.20, 0.30) == 0


def test_across_horizontal_asymptote():
    assert predict_aom(0.30, 0.00001, max_iters=99) > 50


def test_across_vertical_asymptote():
    assert predict_aom(1.00, 0.20, max_iters=99) > 90
