"""Extend the animated opposing bottle arrays in a working landscape scene."""

import bpy


def extend_array(scene, shot):
    """Return the collection of side instances for landscape Bossa shot 06 or 07."""
    number = int(shot)
    if number not in (6, 7):
        return None

    prefix = f"BOSSA{number:02d}"
    source = scene.collection.children[f"{prefix}_01_PRODUCTS"]
    name = f"{prefix}_LandscapeArrayWings"
    wings = scene.collection.children.get(name)
    if wings is None:
        wings = bpy.data.collections.new(name)
        scene.collection.children.link(wings)

    # At the middle of these shots a two-column group spans about 176 mm.
    # Moving adjacent groups by a native row pitch selects different shades
    # at eye level while preserving the original stagger and the 06-to-07 cut.
    pair_pitch = 0.172
    row_pitch = 0.126
    for lane, row in ((-2, 0), (-1, -1), (1, 1), (2, 0)):
        side = "Left" if lane < 0 else "Right"
        name = f"{prefix}_Landscape{side}Pair_{abs(lane):02d}"
        instance = wings.objects.get(name)
        if instance is None:
            instance = bpy.data.objects.new(name, None)
            wings.objects.link(instance)
        instance.instance_type = "COLLECTION"
        instance.instance_collection = source
        instance.location = (lane * pair_pitch, 0.0, row * row_pitch)
        instance.empty_display_size = 0.01
    return wings
