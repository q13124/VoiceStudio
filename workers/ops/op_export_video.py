# op_export_video.py - mux audio + optional captions to MP4 (ffmpeg)
import json, subprocess, os, sys, tempfile, pathlib


def run(timeline_json, out_mp4, options_json):
    # timeline_json may describe a single audio path and optional captions .srt/.vtt
    try:
        tl = (
            json.loads(timeline_json)
            if timeline_json.strip().startswith("{")
            else json.loads(pathlib.Path(timeline_json).read_text(encoding="utf-8"))
        )
    except Exception:
        tl = {}
    audio = tl.get("audio") or ""
    captions = tl.get("captions")  # path to .srt/.vtt
    vf = "scale=1280:720:force_original_aspect_ratio=decrease,format=yuv420p"
    # use black background if no video track; create from color
    if not os.path.isfile(audio):
        raise RuntimeError("audio file missing")
    args = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=1280x720:d=5",
        "-i",
        audio,
    ]
    if captions and os.path.isfile(captions):
        args += [
            "-i",
            captions,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-map",
            "2:0",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            "-vf",
            vf,
            "-preset",
            "fast",
            "-crf",
            "23",
            "-movflags",
            "+faststart",
            out_mp4,
        ]
    else:
        args += [
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            "-vf",
            vf,
            "-preset",
            "fast",
            "-crf",
            "23",
            "-movflags",
            "+faststart",
            out_mp4,
        ]
    subprocess.run(args, check=True)
    print(
        json.dumps(
            {
                "jobId": "adhoc",
                "state": "done",
                "progress": 1.0,
                "message": "ok",
                "artifactPath": out_mp4,
            }
        )
    )
