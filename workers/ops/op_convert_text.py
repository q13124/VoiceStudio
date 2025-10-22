import json, os
from .op_asr_whisper import run as _whisper
def run(src, dst_json, options_json):
    return _whisper(src, dst_json, options_json)
