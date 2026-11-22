"""Resume the approved portrait queue in an interactive Blender session.

Loaded through Blender MCP as module ``lapohka_portrait_render_queue``; call
``start()`` once. Progress is written by render events, with no external polling.
Scene files are never saved. Esc cancels the current render and stops the queue.
"""

import hashlib
import json
import os
from pathlib import Path
import struct
import time
from datetime import datetime, timezone

import bpy
from bpy.app.handlers import persistent


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "renders" / "lapohka_portrait_production_queue.json"
RANGES = [(1, 0, 82), (2, 57, 198), (3, 199, 284), (4, 285, 375)]
items = []
status = {}
owned_render = False
advance_scheduled = False
wait_started = None


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def png_valid(path):
    if not path.exists():
        return False
    if path.stat().st_size < 100:
        raise RuntimeError(f"Incomplete image: {path}")
    with path.open("rb") as stream:
        header = stream.read(33)
        stream.seek(-12, 2)
        tail = stream.read(12)
    if (header[:8] != b"\x89PNG\r\n\x1a\n"
            or header[12:16] != b"IHDR"
            or struct.unpack(">II", header[16:24]) != (2160, 3840)
            or header[24:26] != bytes([16, 2])
            or tail != b"\x00\x00\x00\x00IEND\xaeB\x60\x82"):
        raise RuntimeError(f"Invalid production PNG: {path}")
    return True


def frame_path(item, frame):
    return Path(item["output_prefix"] + f"{frame:04d}.png")


def missing_frames(item):
    return [f for f in range(item["start"], item["end"] + 1)
            if not png_valid(frame_path(item, f))]


def check_source(item):
    stem = (f"gel_polish_lapohka_shot{item['shot']}_portrait_"
            f"{item['start']}_{item['end']}")
    scene = ROOT / "scenes" / f"{stem}.blend"
    output = ROOT / "renders" / stem / "frames" / "frame_"
    if (Path(item["scene"]).resolve() != scene.resolve()
            or Path(item["output_prefix"]).resolve() != output.resolve()):
        raise RuntimeError("Queue paths do not match the approved portrait scenes")
    if hashlib.sha256(scene.read_bytes()).hexdigest() != item["source_sha256"]:
        raise RuntimeError(f"Scene changed after render approval: {scene}")


def write_status():
    status["updated_utc"] = utc_now()
    status["completed_frames_total"] = sum(i["completed_frames"] for i in items)
    status["remaining_frames_total"] = 402 - status["completed_frames_total"]
    temporary = STATUS_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(status, indent=2), encoding="utf-8")
    os.replace(temporary, STATUS_PATH)


def fail(error):
    global owned_render
    owned_render = False
    status.update(status="error", error=str(error))
    if 0 <= status["index"] < len(items):
        items[status["index"]]["status"] = "error"
    write_status()
    print("LAPOHKA PORTRAIT QUEUE STOPPED:", error, flush=True)


def schedule_advance():
    global advance_scheduled, wait_started
    if not advance_scheduled:
        advance_scheduled = True
        wait_started = time.monotonic()
        bpy.app.timers.register(advance, first_interval=1.0, persistent=True)


@persistent
def on_pre(scene, *_args):
    if owned_render:
        status.update(status="rendering", current_frame=scene.frame_current)
        write_status()


@persistent
def on_write(scene, *_args):
    if not owned_render:
        return
    try:
        item = items[status["index"]]
        path = frame_path(item, scene.frame_current)
        if not png_valid(path):
            raise RuntimeError(f"Render write event without saved image: {path}")
        item["completed_frames"] += 1
        status["frames_written_this_run"] += 1
        status.update(last_saved_frame=scene.frame_current, last_saved_file=str(path))
        write_status()
    except Exception as error:
        fail(error)


@persistent
def on_cancel(_scene, *_args):
    global owned_render
    if owned_render:
        owned_render = False
        status["status"] = "cancelled"
        items[status["index"]]["status"] = "cancelled"
        write_status()


@persistent
def on_complete(_scene, *_args):
    global owned_render
    if not owned_render:
        return
    owned_render = False
    try:
        item = items[status["index"]]
        if missing_frames(item):
            raise RuntimeError("Animation completed with missing frames")
        item.update(completed_frames=item["expected_frames"], status="completed",
                    finished_utc=utc_now())
        status["status"] = "between_shots"
        write_status()
        schedule_advance()
    except Exception as error:
        fail(error)


def configure_loaded_scene(item, first_frame):
    scene = bpy.context.scene
    render = scene.render
    if not scene.camera or scene.camera.name != f"SHOT{item['shot']:02d}_PortraitCamera":
        raise RuntimeError("Unexpected portrait camera")
    if (render.resolution_x, render.resolution_y, render.resolution_percentage) != (2160, 3840, 100):
        raise RuntimeError("Unexpected portrait resolution")
    if render.engine != "CYCLES" or scene.cycles.samples != 1024:
        raise RuntimeError("Unexpected render quality")
    if render.fps != 30 or render.fps_base != 1:
        raise RuntimeError("Unexpected frame rate")
    image = render.image_settings
    if (image.file_format, image.color_mode, image.color_depth) != ("PNG", "RGB", "16"):
        raise RuntimeError("Unexpected output image format")
    if Path(bpy.path.abspath(render.filepath)).resolve() != Path(item["output_prefix"]).resolve():
        raise RuntimeError("Unexpected image output path")
    for datablocks in (bpy.data.libraries, bpy.data.cache_files, bpy.data.images):
        for data in datablocks:
            reference = getattr(data, "filepath", "")
            if (not reference or getattr(data, "packed_file", None)
                    or getattr(data, "source", "") in {"GENERATED", "VIEWER"}):
                continue
            if not Path(bpy.path.abspath(reference, library=data.library)).exists():
                raise RuntimeError(f"Missing dependency: {reference}")

    # OSL was the crashing component. Built-in nodes can use the standard
    # shader compiler; preserve OSL if any Script node actually needs it.
    script_nodes = []
    owners = (list(bpy.data.materials) + list(bpy.data.worlds)
              + list(bpy.data.lights) + list(bpy.data.node_groups))
    for owner in owners:
        tree = owner if hasattr(owner, "nodes") else getattr(owner, "node_tree", None)
        if tree:
            script_nodes.extend(owner.name + "/" + node.name for node in tree.nodes
                                if node.bl_idname == "ShaderNodeScript")
    item["saved_osl_enabled"] = scene.cycles.shading_system
    if not script_nodes:
        scene.cycles.shading_system = False
    item.update(render_osl_enabled=scene.cycles.shading_system,
                osl_script_nodes=script_nodes,
                shader_backend_note="Bypass OSL compiler for built-in nodes after oslexec.dll crash; saved scenes and node graphs unchanged.")
    preferences = bpy.context.preferences.addons["cycles"].preferences
    # Shot 3 crashed in nvrtum64.dll on its first OptiX frame. Use the
    # already-discovered CUDA device for this shot; keep its render settings.
    backend = "CUDA" if item["shot"] == 3 else "OPTIX"
    preferences.compute_device_type = backend
    for device in preferences.devices:
        device.use = device.type == backend
    if not any(d.use and d.type == backend for d in preferences.devices):
        raise RuntimeError(f"No enabled {backend} device")
    item["render_compute_backend"] = backend
    item["render_device_names"] = [d.name for d in preferences.devices if d.use]
    if item["shot"] == 3:
        item["compute_backend_note"] = (
            "CUDA fallback after first-frame nvrtum64.dll crash on OptiX; "
            "saved scene and render quality unchanged.")
    scene.cycles.device = "GPU"
    render.use_overwrite = False
    render.use_placeholder = False
    scene.frame_start = first_frame
    scene.frame_end = item["end"]
    scene.frame_set(first_frame)


def launch():
    global owned_render
    if status["status"] != "ready":
        return None
    try:
        item = items[status["index"]]
        if Path(bpy.data.filepath).resolve() != Path(item["scene"]).resolve():
            raise RuntimeError("Active file changed before rendering")
        if bpy.app.is_job_running("RENDER"):
            raise RuntimeError("Another render started")
        owned_render = True
        status["status"] = "starting"
        write_status()
        outcome = bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
        status["operator_result"] = sorted(outcome)
        if not {"RUNNING_MODAL", "FINISHED"}.intersection(outcome):
            raise RuntimeError(f"Render did not start: {outcome}")
        write_status()
    except Exception as error:
        fail(error)
    return None


def advance():
    global advance_scheduled
    if status["status"] in {"cancelled", "error", "completed"}:
        advance_scheduled = False
        return None
    # A completion event can precede UI job teardown. Never load a new file
    # until Blender has released the previous scene.
    if bpy.app.is_job_running("RENDER"):
        if time.monotonic() - wait_started > 30:
            advance_scheduled = False
            fail("Previous render did not release its scene")
            return None
        return 0.5
    advance_scheduled = False
    try:
        index = status["index"] + 1
        while index < len(items):
            item = items[index]
            check_source(item)
            missing = missing_frames(item)
            item["completed_frames"] = item["expected_frames"] - len(missing)
            if not missing:
                item["status"] = "completed"
                index += 1
                continue
            status.update(index=index, active_shot=item["shot"], status="loading")
            write_status()
            bpy.ops.wm.open_mainfile(filepath=item["scene"], load_ui=False, use_scripts=False)
            configure_loaded_scene(item, min(missing))
            item.update(resume_frame=min(missing), status="rendering")
            status.update(current_frame=min(missing), status="ready")
            write_status()
            bpy.app.timers.register(launch, first_interval=0.5, persistent=True)
            return None
        status.update(index=len(items), active_shot=None, status="completed",
                      finished_utc=utc_now())
        write_status()
        print("LAPOHKA PORTRAIT PRODUCTION COMPLETE", flush=True)
    except Exception as error:
        fail(error)
    return None


def start():
    global items, status
    if bpy.app.is_job_running("RENDER"):
        raise RuntimeError("An active render must not be duplicated")
    if bpy.data.is_dirty:
        raise RuntimeError("Current scene has unsaved edits")
    if status:
        raise RuntimeError("This queue was already started; inspect its state")
    prior = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    items = prior["items"]
    if [(i["shot"], i["start"], i["end"]) for i in items] != RANGES:
        raise RuntimeError("Unexpected queue shot ranges")
    for item in items:
        check_source(item)
        count = item["expected_frames"] - len(missing_frames(item))
        item.update(existing_frames=count, completed_frames=count,
                    status="completed" if count == item["expected_frames"] else "pending")
    status = dict(status="prepared", order=[i["shot"] for i in items],
                  total_frames=402, items=items, index=-1, active_shot=None,
                  current_frame=None, last_saved_frame=prior.get("last_saved_frame"),
                  last_saved_file=prior.get("last_saved_file"), frames_written_this_run=0,
                  error=None, pid=os.getpid(), created_utc=prior["created_utc"],
                  resumed_utc=utc_now(), settings=(
                      "2160x3840 / 30fps / Cycles RTX4090 "
                      "(Shot3 CUDA; others OptiX) / 1024 samples / RGB16 PNG"),
                  stop_policy=prior["stop_policy"], status_file=str(STATUS_PATH),
                  resume_script=str(Path(__file__).resolve()),
                  resumed_from={k: prior.get(k) for k in (
                      "status", "pid", "active_shot", "current_frame",
                      "last_saved_frame", "updated_utc")})
    for collection, handler in (
        (bpy.app.handlers.render_pre, on_pre),
        (bpy.app.handlers.render_write, on_write),
        (bpy.app.handlers.render_cancel, on_cancel),
        (bpy.app.handlers.render_complete, on_complete),
    ):
        if handler not in collection:
            collection.append(handler)
    write_status()
    schedule_advance()
    return {key: status[key] for key in (
        "status", "completed_frames_total", "remaining_frames_total", "pid", "status_file")}
