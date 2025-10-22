import importlib

def test_mastering_pipeline_symbols():
    mp = importlib.import_module("pipelines.mastering_pipeline")
    for name in ["AudioBuffer","denoise","eq_opt","compress","loudness_normalize","deess","limit","process_chain"]:
        assert hasattr(mp, name), f"missing: {name}"
