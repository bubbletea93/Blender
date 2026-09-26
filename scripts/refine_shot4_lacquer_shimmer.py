"""Refine Shot 4 lacquer and focus, preserving the shared product asset."""
import bpy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'scenes/gel_polish_lapohka_shot4_285_375_bottle_array_v004_fine_shimmer.blend'
s=bpy.context.scene
assert s.name=='SHOT04_BottleArray_285_375'
wrapper=bpy.data.node_groups['Glitter_UVFix.001'].copy()
wrapper.name='SHOT04_FineShimmer_Wrapper'
core=bpy.data.node_groups['Lacquer_RenderGlitter_SHARED'].copy()
core.name='SHOT04_FineShimmer_Core'
wrapper.nodes['Shared render glitter finish'].node_tree=core
for mat in bpy.data.materials:
    if mat.name.startswith('SHOT04_Lacquer_'):
        for node in mat.node_tree.nodes:
            if node.type=='GROUP' and node.node_tree and node.node_tree.name=='Glitter_UVFix.001':
                node.node_tree=wrapper
n=core.nodes
n['Fine pearl facet density'].inputs['Scale'].default_value=800
n['Coarse flake cells'].inputs['Scale'].default_value=400
n['Occasional larger glints'].inputs[1].default_value=.80
n['Dense pearlescent shimmer'].inputs['Roughness'].default_value=.14
n['Per-facet luster'].inputs['To Min'].default_value=.03
n['Shimmer coverage'].inputs[2].default_value=.68
core['purpose']='Dense fine UV-locked lacquer shimmer; roughly 1.2 pixel facets at a 600 pixel core diameter.'
core['finish_version']='SHOT04-2026-09-22-fine'
lens=bpy.data.materials['SHOT02_57_96_MAT_FrontLens_Glass']
assert lens.library is None
lens.node_tree.nodes['Glass BSDF'].inputs['Roughness'].default_value=.002
hero=next(o for o in s.objects if o.name.startswith('SHOT04_Bottle_R03_C04'))
focus=s.camera.data.dof.focus_object
focus.parent=hero
focus.matrix_parent_inverse.identity()
focus.location=(0,-.0283464,.0326)
focus.rotation_euler=(0,0,0)
focus.scale=(1,1,1)
focus.name='SHOT04_LacquerFocus'
focus['purpose']='Focus follows the lacquer front surface, rather than the stage plane.'
s.camera.data.dof.use_dof=True
s.camera.data.dof.aperture_fstop=64
s.cycles.samples=1024;s.cycles.use_adaptive_sampling=True
s.cycles.adaptive_threshold=.002;s.cycles.adaptive_min_samples=64
s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE'
s.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
s.cycles.denoising_prefilter='ACCURATE';s.cycles.denoising_quality='HIGH'
s.cycles.use_animated_seed=False
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16'
s.render.filepath='//../renders/shot4_fine_shimmer_v004/production_4k/frame_'
s.frame_set(348);bpy.context.view_layer.update()
s['shimmer_revision']='Finer local pearl shader, clear lens, and hero-core focus at f/64.'
notes=bpy.data.texts.get('SHOT04_README')
if notes:notes.write('\n\nv004 fine shimmer: local facet density 800, smaller glints 400, shimmer roughness .14. Focus follows hero lacquer front; f/64. Linked shared asset and all motion curves preserved.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(DEST))
print('FINE_SHIMMER_SCENE_SAVED',DEST,flush=True)
