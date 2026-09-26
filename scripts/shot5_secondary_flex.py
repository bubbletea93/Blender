"""Shot-local, editable follow-through for the finale's brush and swatch props.

Call apply_secondary_flex(scene, impact_frame=432) from the scene builder.
The function neither loads/saves files nor invokes Blender operators. It
copies object containers only: production meshes and materials stay shared.
All motion is authored choreography, not a physics simulation.
"""
import math

import bpy
from mathutils import Matrix, Vector


SHADES = ('Aubergine', 'PetrolTeal', 'PearlIvory', 'Raspberry', 'MidnightBlue')
ROOT_NAMES = ('SHOT05_SwatchFan', 'SHOT05_ManicureBrushHolder')


def _realize_objects(root, destination):
    """Match collection-instance transforms without touching the source IDs."""
    source = root.instance_collection
    assert root.instance_type == 'COLLECTION' and source is not None, root.name
    offset = Matrix.Translation(-Vector(source.instance_offset))
    copies = {}
    for original in tuple(source.all_objects):
        # Flatten the source hierarchy under the existing shot root. This is
        # equivalent to its collection instance, including instance_offset.
        local_matrix = offset @ original.matrix_world.copy()
        duplicate = original.copy()
        duplicate.name = 'SHOT05_FlexPart_' + original.name
        duplicate.animation_data_clear()
        duplicate.parent = root
        duplicate.matrix_parent_inverse = Matrix.Identity(4)
        duplicate.matrix_basis = local_matrix
        duplicate['secondary_flex_source'] = original.name
        destination.objects.link(duplicate)
        assert duplicate.data == original.data
        copies[original.name] = duplicate
    # Keep the original root's name, transform, animation and parent intact.
    root.instance_type = 'NONE'
    root.instance_collection = None
    root['secondary_flex_realized'] = True
    return copies, offset


def _pivot(name, root, destination, position):
    obj = bpy.data.objects.new(name, None)
    destination.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = position
    obj.rotation_mode = 'XYZ'
    obj.empty_display_type = 'PLAIN_AXES'
    obj.empty_display_size = .004
    obj['motion_type'] = 'Authored delayed, damped follow-through'
    return obj


def _reparent_at_rest(obj, pivot):
    # Both matrices are in the prop root's local space, so the rest geometry
    # survives realization and pivot insertion exactly (within float error).
    root_local = obj.matrix_basis.copy()
    obj.parent = pivot
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = pivot.matrix_basis.inverted() @ root_local


def _animate(pivot, axis, impact_frame, delay, amplitude_degrees, sign):
    first = impact_frame + delay
    end = impact_frame + 38
    frames_and_weights = [
        (min(376, first - 1), 0),
        (first, 0),
        (first + 4, 1),
        (first + 11, -.43),
        (first + 18, .17),
        (first + 25, -.055),
        (end, 0),
        (max(528, end + 1), 0),
    ]
    amplitude = math.radians(amplitude_degrees) * sign
    for frame, weight in frames_and_weights:
        pivot.rotation_euler[axis] = amplitude * weight
        pivot.keyframe_insert('rotation_euler', index=axis, frame=frame,
                              group='Secondary follow-through')
    ad = pivot.animation_data
    for layer in ad.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                if bag.slot_handle != ad.action_slot_handle:
                    continue
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = 'BEZIER'
                        key.handle_left_type = 'AUTO_CLAMPED'
                        key.handle_right_type = 'AUTO_CLAMPED'
    pivot['impact_frame'] = impact_frame
    pivot['response_delay_frames'] = delay
    pivot['maximum_angle_degrees'] = amplitude_degrees
    pivot['settled_frame'] = end
    return {'name': pivot.name, 'axis': 'XYZ'[axis], 'delay_frames': delay,
            'amplitude_degrees': amplitude_degrees, 'settled_frame': end,
            'keyframes': [frame for frame, weight in frames_and_weights]}


def apply_secondary_flex(scene, impact_frame=432):
    """Realize the two prop assemblies and add eight independent hinge controls.

    Existing prop roots remain available for the caller's stage bounce and
    weight-dependent whole-object motion. Fixed cup, fan base, rear support,
    gold ring and pivot pin remain directly parented to their prop root.
    """
    roots = {name: scene.objects.get(name) for name in ROOT_NAMES}
    assert all(roots.values()), 'Shot 5 fan and brush-holder roots are required.'
    assert all(not root.get('secondary_flex_realized', False) for root in roots.values()), \
        'Secondary flex is already installed; edit its existing pivot controls.'
    # Validate names before changing the scene, so a different asset revision
    # fails with the two original instances still intact.
    fan_names = set(roots[ROOT_NAMES[0]].instance_collection.all_objects.keys())
    brush_names = set(roots[ROOT_NAMES[1]].instance_collection.all_objects.keys())
    expected_fan = {prefix + shade for shade in SHADES
                    for prefix in ('SwatchStem_', 'NailSwatch_')}
    expected_brushes = {prefix + str(i) for i in range(3)
                        for prefix in ('NailBrush_Handle_', 'NailBrush_GoldFerrule_',
                                       'NailBrush_FineTip_')}
    assert expected_fan <= fan_names, sorted(expected_fan - fan_names)
    assert expected_brushes <= brush_names, sorted(expected_brushes - brush_names)

    destination = next((c for c in roots[ROOT_NAMES[0]].users_collection
                        if c.name == 'SHOT05_02_MANICURE_PROPS'),
                       roots[ROOT_NAMES[0]].users_collection[0])
    fan, fan_offset = _realize_objects(roots[ROOT_NAMES[0]], destination)
    brushes, brush_offset = _realize_objects(roots[ROOT_NAMES[1]], destination)
    controls = []

    # Fan stems rotate in their fan plane about the fixed gold pin. The tiny
    # Y offsets preserve the authored stacked stem slots around that pin.
    fan_settings = [(2, 2.0, -1), (3, 2.7, 1), (4, 3.4, -1),
                    (3, 2.5, 1), (5, 2.1, -1)]
    for i, (shade, (delay, amplitude, sign)) in enumerate(zip(SHADES, fan_settings)):
        position = fan_offset @ Vector((0, .0015 + i * .00015, .017))
        pivot = _pivot('SHOT05_SwatchFlex_' + shade, roots[ROOT_NAMES[0]],
                       destination, position)
        for prefix in ('SwatchStem_', 'NailSwatch_'):
            _reparent_at_rest(fan[prefix + shade], pivot)
        controls.append(_animate(pivot, 1, impact_frame, delay, amplitude, sign))

    # The brushes sway front/back about their authored lower ends. Keeping
    # this on X avoids adding more outward lean toward the cup's side walls.
    brush_positions = [(-.009, 0, .006), (0, .003, .006), (.009, -.002, .006)]
    brush_settings = [(2, 2.4, 1), (4, 2.0, -1), (5, 2.8, 1)]
    for i, (position, (delay, amplitude, sign)) in enumerate(zip(brush_positions,
                                                               brush_settings)):
        pivot = _pivot('SHOT05_BrushFlex_' + str(i + 1).zfill(2),
                       roots[ROOT_NAMES[1]], destination,
                       brush_offset @ Vector(position))
        for prefix in ('NailBrush_Handle_', 'NailBrush_GoldFerrule_', 'NailBrush_FineTip_'):
            _reparent_at_rest(brushes[prefix + str(i)], pivot)
        # The source's outer handles crossed the inner cup rim at rest. Keep
        # their lower ends fixed and correct only the shot-local resting lean
        # from -9/+10 degrees to -6/+6; shared geometry stays untouched.
        rest_correction = (3, 0, -4)[i]
        pivot.rotation_euler.y = math.radians(rest_correction)
        pivot['rest_lean_correction_degrees'] = rest_correction
        control = _animate(pivot, 0, impact_frame, delay, amplitude, sign)
        control['rest_lean_correction_degrees'] = rest_correction
        controls.append(control)

    scene.frame_set(scene.frame_current, subframe=scene.frame_subframe)
    return {
        'authored_motion': True, 'impact_frame': impact_frame,
        'controls': controls, 'control_names': [c['name'] for c in controls],
        'realized_roots': list(ROOT_NAMES),
        'local_object_count': len(fan) + len(brushes),
        'mesh_and_material_data_shared': True,
        'fixed_fan_parts': sorted(name for name, obj in fan.items()
                                 if obj.parent == roots[ROOT_NAMES[0]]),
        'fixed_holder_parts': sorted(name for name, obj in brushes.items()
                                    if obj.parent == roots[ROOT_NAMES[1]]),
    }
