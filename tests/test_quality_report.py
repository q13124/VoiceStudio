def test_quality_report_symbols():
    import app.core.pipelines.quality_report as qr
    assert hasattr(qr, "AudioIn")
    assert hasattr(qr, "analyze")
