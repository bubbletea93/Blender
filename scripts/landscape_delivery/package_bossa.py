"""Package a completed Bossa landscape PNG sequence as its native 25 fps editing master."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile


# Shot ID, delivery order and inclusive Blender frame range.
SHOTS = {
    1: (1, 0, 125),
    2: (2, 126, 170),
    6: (7, 404, 425),
    7: (8, 426, 450),
    5: (9, 316, 403),
    10: (10, 657, 749),
}
FRAME_NAME = re.compile(r"frame_(\d{4})\.png")
COLOR_FILTER = (
    "scale=in_range=full:out_range=tv:out_color_matrix=bt709:"
    "flags=accurate_rnd+full_chroma_int,format=yuv444p10le,setsar=1,"
    "setparams=range=limited:color_primaries=bt709:color_trc=iec61966-2-1:colorspace=bt709"
)


def read_sequence(folder, start, end):
    """Accept the full native range or a full shot numbered locally from 0 or 1."""
    paths = sorted(folder.glob("frame_*.png"))
    indices = []
    fingerprint = hashlib.sha256()
    states = []
    for path in paths:
        match = FRAME_NAME.fullmatch(path.name)
        if not match:
            raise ValueError(f"Unexpected frame name: {path}")
        indices.append(int(match[1]))
        before = path.stat()
        with path.open("rb") as stream:
            header = stream.read(33)
            if len(header) != 33 or header[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
                raise ValueError(f"Missing PNG header: {path}")
            width, height, depth, color = struct.unpack_from(">IIBB", header, 16)
            if (width, height) != (3840, 2160) or depth not in (8, 16) or color not in (2, 6):
                raise ValueError(f"Expected 3840x2160 RGB/RGBA PNG, got {width}x{height}, depth {depth}, color type {color}: {path}")
            stream.seek(0)
            fingerprint.update(hashlib.file_digest(stream, "sha256").digest())
        states.append((path, before.st_size, before.st_mtime_ns))

    count = end - start + 1
    if not indices or indices[0] not in (0, 1, start) or indices != list(range(indices[0], indices[0] + count)):
        raise ValueError(f"Expected {count} consecutive PNG frames in {folder} (native range {start}–{end}, or local numbering from 0 or 1).")
    return indices[0], fingerprint.hexdigest(), states


def verify(path, count, fps, provenance):
    report = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path),
    ], text=True)
    data = json.loads(report)
    expected = {
        "codec_name": "prores", "profile": "XQ", "codec_tag_string": "ap4x",
        "width": 3840, "height": 2160, "sample_aspect_ratio": "1:1", "pix_fmt": "yuv444p12le",
        "color_range": "tv", "color_space": "bt709", "color_transfer": "iec61966-2-1",
        "color_primaries": "bt709", "r_frame_rate": f"{fps}/1", "avg_frame_rate": f"{fps}/1",
        "nb_frames": str(count),
    }
    if len(data["streams"]) != 1:
        raise ValueError(f"Expected a single video stream in {path}.")
    stream = data["streams"][0]
    for key, value in expected.items():
        if stream.get(key) != value:
            raise ValueError(f"{path}: expected {key}={value}, found {stream.get(key)}.")
    if data["format"]["tags"].get("source_sequence") != provenance:
        raise ValueError(f"Source fingerprint differs or is missing in {path}.")
    decoded = subprocess.check_output([
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(path), "-map", "0:v:0",
        "-fps_mode", "passthrough", "-progress", "pipe:1", "-nostats", "-f", "null", "-",
    ], text=True)
    totals = re.findall(r"^frame=(\d+)$", decoded, flags=re.MULTILINE)
    if not totals or int(totals[-1]) != count:
        raise ValueError(f"Expected {count} decoded frames in {path}, found {totals[-1:]}.")


def package(shot, frames, out, fps=25):
    if fps != 25:
        raise ValueError("All six Bossa source shots run at 25 fps.")
    order, start, end = SHOTS[shot]
    count = end - start + 1
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(f"Missing executable on PATH: {tool}")
    frames = Path(frames).resolve()
    out = Path(out).resolve()
    first, digest, states = read_sequence(frames, start, end)
    provenance = f"bossa-landscape-v1/{shot:02}/{fps}/{digest}"
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{order:02}_Bossa_{shot:02}_4K_{fps}fps.mov"
    if target.exists():
        verify(target, count, fps, provenance)
        print(f"Verified existing master: {target}", flush=True)
        return target

    with tempfile.TemporaryDirectory(dir=out, prefix=f".{target.stem}.") as staging:
        pending = Path(staging) / target.name
        subprocess.run([
            "ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-xerror", "-n",
            "-framerate", str(fps), "-start_number", str(first), "-start_number_range", "1",
            "-i", str(frames / "frame_%04d.png"), "-frames:v", str(count), "-an",
            "-vf", COLOR_FILTER, "-c:v", "prores_ks", "-profile:v", "5", "-vendor", "apl0",
            "-threads:v", "8", "-color_range", "tv", "-colorspace", "bt709",
            "-color_primaries", "bt709", "-color_trc", "iec61966-2-1",
            "-metadata", f"source_sequence={provenance}", "-movflags", "+faststart+use_metadata_tags+write_colr",
            str(pending),
        ], check=True)
        verify(pending, count, fps, provenance)
        for path, size, mtime_ns in states:
            current = path.stat()
            if (size, mtime_ns) != (current.st_size, current.st_mtime_ns):
                raise ValueError(f"Source changed while packaging: {path}")
        try:
            # Both operations atomically publish without replacing a concurrent writer.
            if os.name == "nt":
                pending.rename(target)
            else:
                os.link(pending, target)
        except FileExistsError:
            verify(target, count, fps, provenance)
    print(f"Verified master: {target}", flush=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shot", type=int, choices=SHOTS, required=True)
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fps", type=int, choices=(25,), default=25)
    args = parser.parse_args()
    try:
        package(args.shot, args.frames, args.out, args.fps)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(f"Packaging stopped: {error}")


if __name__ == "__main__":
    main()
