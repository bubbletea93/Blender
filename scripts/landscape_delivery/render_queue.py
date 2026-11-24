"""Resume the Bossa landscape renders and package each completed shot."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import uuid
import zlib

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from package_bossa import SHOTS

ROOT = HERE.parents[1]
ORDER = (6, 7, 10, 1, 2, 5)
STATE = ROOT / "renders" / "hero_landscape_queue"
DELIVERY = ROOT / "renders" / "hero_landscape_shots"
DEFAULT_BLENDER = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Blender Foundation/Blender 5.3/blender.exe"


def utc():
    return datetime.now(timezone.utc).isoformat()


def shot_paths(shot):
    _, first, last = SHOTS[shot]
    stem = f"gel_polish_bossa_shot{shot:02}_landscape_{first}_{last}"
    return ROOT / "scenes" / (stem + ".blend"), ROOT / "renders" / stem / "frames"


def blender_setup(shot):
    """Executed in Blender's process after file load, before -s/-e/-a."""
    import bpy

    source, frames = shot_paths(shot)
    _, first, last = SHOTS[shot]
    scene = bpy.context.scene
    render = scene.render
    image = render.image_settings
    checks = {
        "Blender 5.3": bpy.app.version[:2] == (5, 3),
        "scene file": Path(bpy.data.filepath).resolve() == source,
        "frame range and step": (scene.frame_start, scene.frame_end, scene.frame_step) == (first, last, 1),
        "Cycles camera": render.engine == "CYCLES" and scene.camera is not None,
        "full landscape frame": (render.resolution_x, render.resolution_y, render.resolution_percentage) == (3840, 2160, 100)
            and render.pixel_aspect_x == render.pixel_aspect_y and not render.use_border,
        "25 fps": render.fps == 25 and render.fps_base == 1,
        "PNG image sequence": (image.file_format, image.color_mode, image.color_depth) == ("PNG", "RGB", "16")
            and render.use_file_extension,
        "frame location": Path(bpy.path.abspath(render.frame_path(frame=first))).resolve() == frames / f"frame_{first:04}.png",
    }
    failures = [key for key, ok in checks.items() if not ok]
    if failures:
        raise RuntimeError(f"{source.name} failed preflight: {', '.join(failures)}")
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "OPTIX"
    preferences.refresh_devices()
    cards = [device for device in preferences.devices if device.type == "OPTIX"]
    if not cards:
        raise RuntimeError("No OptiX GPU available for this render.")
    for device in preferences.devices:
        device.use = device.type == "OPTIX"
    scene.cycles.device = "GPU"
    render.use_overwrite = render.use_placeholder = False
    print(f"Verified {source.name}, {scene.cycles.samples} samples, OptiX: "
          + ", ".join(card.name for card in cards), flush=True)


@contextmanager
def queue_lock(path):
    """The OS releases the lock only when the runner and its worker have closed it."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        import msvcrt

        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        api.CreateFileW.restype = wintypes.HANDLE
        # OPEN_ALWAYS; other processes may read the owner PID but cannot acquire write access.
        handle = api.CreateFileW(str(path), 0xC0000000, 1, None, 4, 0x80, None)
        if handle == ctypes.c_void_p(-1).value:
            error = ctypes.get_last_error()
            if error == 32:
                raise RuntimeError(f"A landscape queue or its worker holds {path}.")
            raise ctypes.WinError(error)
        stream = os.fdopen(msvcrt.open_osfhandle(handle, os.O_RDWR), "r+b")
    else:
        import fcntl

        stream = path.open("a+b")
    with stream:
        if os.name == "nt":
            start = subprocess.STARTUPINFO()
            start.lpAttributeList = {"handle_list": [handle]}
            os.set_handle_inheritable(handle, True)
            child_options = {"startupinfo": start, "creationflags": subprocess.CREATE_NO_WINDOW}
        else:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError(f"A landscape queue or its worker holds {path}.") from error
            child_options = {"pass_fds": (stream.fileno(),)}
        stream.seek(0)
        stream.truncate()
        stream.write(f"{os.getpid()} {utc()}\n".encode())
        stream.flush()
        yield child_options


def valid_png(path):
    """Check every PNG chunk, its CRC and the complete final IEND."""
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            return False
        size = path.stat().st_size
        saw_header = saw_image = False
        while header := stream.read(8):
            if len(header) != 8:
                return False
            length, kind = struct.unpack(">I4s", header)
            if length > size - stream.tell() - 4:
                return False
            body = stream.read(length)
            if stream.read(4) != struct.pack(">I", zlib.crc32(body, zlib.crc32(kind))):
                return False
            if not saw_header:
                if kind != b"IHDR" or len(body) != 13 or struct.unpack(">IIBB", body[:10]) != (3840, 2160, 16, 2):
                    return False
                saw_header = True
            if kind == b"IDAT" and length:
                saw_image = True
            if kind == b"IEND":
                return saw_image and length == 0 and stream.tell() == size
    return False


def contiguous(numbers):
    ranges = []
    for number in numbers:
        if ranges and number == ranges[-1][1] + 1:
            ranges[-1][1] = number
        else:
            ranges.append([number, number])
    return ranges


def event(state, event_name, shot=None, **detail):
    entry = {"time": utc(), "stage": event_name, **detail}
    if shot is not None:
        entry["shot"] = shot
        state["shots"].setdefault(str(shot), {}).update(entry)
    state["latest"] = entry
    state["events"].append(entry)
    temporary = STATE / "status.pending"
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(state, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, STATE / "status.json")
    print(json.dumps(entry), flush=True)


def worker(command, log, child_options, **options):
    with log.open("a", encoding="utf-8") as stream:
        stream.write(f"\n{utc()} {subprocess.list2cmdline(list(map(str, command)))}\n")
        stream.flush()
        subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=True, **child_options, **options)


def process_shot(shot, blender, state, child_options):
    order, first, last = SHOTS[shot]
    source, frames = shot_paths(shot)
    frames.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    previous = state["shots"].get(str(shot), {}).get("scene_sha256")
    if previous and previous != digest and any(frames.glob("frame_*.png")):
        raise RuntimeError(f"Scene changed while existing frames remain: {source}")
    expected = {f"frame_{n:04}.png" for n in range(first, last + 1)}
    extra = sorted(path.name for path in frames.glob("frame_*.png") if path.name not in expected)
    if extra:
        raise RuntimeError(f"Unexpected sequence frames in {frames}: {extra}")
    log = STATE / f"shot{shot:02}.log"
    event(state, "checking_frames", shot, scene=str(source), scene_sha256=digest, log=str(log))
    missing = []
    for number in range(first, last + 1):
        path = frames / f"frame_{number:04}.png"
        if path.exists():
            if valid_png(path):
                continue
            preserved = frames.parent / "invalid_frames" / f"{path.stem}_{uuid.uuid4().hex}.png"
            preserved.parent.mkdir(exist_ok=True)
            path.rename(preserved)
            event(state, "preserved_invalid_frame", shot, frame=number, preserved=str(preserved))
        missing.append(number)
    environment = {**os.environ, "BOSSA_QUEUE_BLENDER_SHOT": str(shot)}
    for start, end in contiguous(missing):
        event(state, "rendering", shot, first=start, last=end)
        worker([
            str(blender), "--factory-startup", "-b", str(source), "--python-exit-code", "15",
            "-P", str(Path(__file__).resolve()), "-s", str(start), "-e", str(end), "-a",
            "--", "--cycles-device", "OPTIX",
        ], log, child_options, env=environment)
        for number in range(start, end + 1):
            path = frames / f"frame_{number:04}.png"
            if not path.is_file() or not valid_png(path):
                raise RuntimeError(f"Blender exited with an incomplete frame: {path}. See {log}.")
        event(state, "range_complete", shot, first=start, last=end)
    event(state, "packaging", shot, frames=last - first + 1)
    worker([sys.executable, str(HERE / "package_bossa.py"), "--shot", str(shot), "--frames", str(frames),
            "--out", str(DELIVERY), "--fps", "25"], log, child_options)
    master = DELIVERY / f"{order:02}_Bossa_{shot:02}_4K_25fps.mov"
    if not master.is_file():
        raise RuntimeError(f"Packaging finished without {master}.")
    event(state, "shot_complete", shot, master=str(master))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default=str(DEFAULT_BLENDER) if DEFAULT_BLENDER.exists() else "blender")
    parser.add_argument("--shots", nargs="+", type=int, choices=ORDER, default=ORDER,
                        help="Shot IDs to run (default: 6 7 10 1 2 5).")
    args = parser.parse_args()
    blender = shutil.which(args.blender)
    if not blender:
        raise FileNotFoundError(f"Blender 5.3 executable not found: {args.blender}")
    selected = list(dict.fromkeys(args.shots))
    STATE.mkdir(parents=True, exist_ok=True)
    with queue_lock(STATE / "queue.lock") as child_options:
        status = STATE / "status.json"
        state = json.loads(status.read_text("utf-8")) if status.exists() else {"shots": {}, "events": []}
        event(state, "queue_started", pid=os.getpid(), order=selected)
        active = None
        try:
            absent = [str(shot_paths(s)[0]) for s in selected if not shot_paths(s)[0].is_file()]
            if absent:
                raise FileNotFoundError("Missing prepared landscape scene(s): " + ", ".join(absent))
            for active in selected:
                process_shot(active, blender, state, child_options)
        except (Exception, KeyboardInterrupt) as error:
            event(state, "queue_stopped", active, error=str(error) or type(error).__name__)
            raise
        event(state, "queue_complete", order=selected)


if __name__ == "__main__":
    if "--cycles-device" in sys.argv and "BOSSA_QUEUE_BLENDER_SHOT" in os.environ:
        blender_setup(int(os.environ["BOSSA_QUEUE_BLENDER_SHOT"]))
    else:
        main()
