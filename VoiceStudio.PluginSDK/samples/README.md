# Plugin Samples
- DSP Filter: `python samples\sample_dsp_filter.py` (listens on 127.0.0.1:59112)
  POST JSON: {"op":"highpass","options":{"f":140},"in":"C:\path\in.wav","out":"C:\path\out.wav"}
- Exporter:  `python samples\sample_exporter.py` (127.0.0.1:59113)