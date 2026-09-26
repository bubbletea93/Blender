"""Shared lacquer finish: resolvable metallic flakes over the existing cat eye."""
import bpy
GROUP='Lacquer_RenderGlitter_SHARED'
VERSION='2026-09-15.2'

def build_group(existing=None):
    g=existing or bpy.data.node_groups.new(GROUP,'ShaderNodeTree');g.use_fake_user=True
    if existing:g.nodes.clear()
    else:
        for name,kind,direction in [('Base Shader','NodeSocketShader','INPUT'),('Base Color','NodeSocketColor','INPUT'),('UV','NodeSocketVector','INPUT'),('BSDF','NodeSocketShader','OUTPUT')]:
            g.interface.new_socket(name=name,in_out=direction,socket_type=kind)
    n,l=g.nodes,g.links
    inp=n.new('NodeGroupInput');inp.location=(-850,80)
    out=n.new('NodeGroupOutput');out.location=(850,100)
    vor=n.new('ShaderNodeTexVoronoi');vor.name='Coarse flake cells';vor.label='90 cells per UV unit — visible at final output';vor.voronoi_dimensions='2D';vor.feature='F1'
    vor.inputs['Scale'].default_value=90;vor.location=(-630,100);l.new(inp.outputs['UV'],vor.inputs['Vector'])
    edge=n.new('ShaderNodeMapRange');edge.name='Flake footprint';edge.clamp=True
    edge.inputs['From Min'].default_value=.14;edge.inputs['From Max'].default_value=.22;edge.inputs['To Min'].default_value=1;edge.inputs['To Max'].default_value=0
    l.new(vor.outputs['Distance'],edge.inputs['Value']);edge.location=(-400,280)
    sep=n.new('ShaderNodeSeparateColor');sep.mode='RGB';l.new(vor.outputs['Color'],sep.inputs[0]);sep.location=(-400,0)
    radius=n.new('ShaderNodeMapRange');radius.name='Vary individual flake size';radius.inputs['To Min'].default_value=.10;radius.inputs['To Max'].default_value=.28;l.new(sep.outputs['Green'],radius.inputs['Value'])
    inner=n.new('ShaderNodeMath');inner.operation='MULTIPLY';inner.inputs[1].default_value=.7;l.new(radius.outputs[0],inner.inputs[0])
    l.new(inner.outputs[0],edge.inputs['From Min']);l.new(radius.outputs[0],edge.inputs['From Max'])
    radius.location=(-400,550);inner.location=(-170,550);edge.location=(50,550)
    select=n.new('ShaderNodeMath');select.name='Occasional larger glints';select.operation='GREATER_THAN';select.inputs[1].default_value=.94;l.new(sep.outputs['Blue'],select.inputs[0]);select.location=(-200,200)
    mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(select.outputs[0],mask.inputs[0]);l.new(edge.outputs['Result'],mask.inputs[1]);mask.location=(0,280)
    mask.location=(280,350)
    tint=n.new('ShaderNodeMixRGB');tint.name='Silver flakes retain a little lacquer tint';tint.inputs[0].default_value=.35;tint.inputs[2].default_value=(.85,.88,.95,1)
    l.new(inp.outputs['Base Color'],tint.inputs[1]);tint.location=(0,-160)
    # Constant orientation per Voronoi cell, attached to the product's UVs.
    scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.40;l.new(vor.outputs['Color'],scale.inputs[0])
    add=n.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.30,.30,.80);l.new(scale.outputs[0],add.inputs[0])
    normal=n.new('ShaderNodeNormalMap');normal.name='Random flake orientation';normal.space='TANGENT';normal.inputs['Strength'].default_value=1;l.new(add.outputs[0],normal.inputs['Color'])
    scale.location=(-380,-350);add.location=(-170,-350);normal.location=(30,-350)
    flake=n.new('ShaderNodeBsdfPrincipled');flake.name='Metallic flakes';flake.inputs['Metallic'].default_value=1;flake.inputs['Roughness'].default_value=.10
    l.new(tint.outputs[0],flake.inputs['Base Color']);l.new(normal.outputs[0],flake.inputs['Normal']);flake.location=(270,-120)
    mix=n.new('ShaderNodeMixShader');mix.name='Sparse flakes over original lacquer';l.new(mask.outputs[0],mix.inputs[0]);l.new(inp.outputs['Base Shader'],mix.inputs[1]);l.new(flake.outputs['BSDF'],mix.inputs[2]);mix.location=(630,100)

    # Dense, fine pearlescent facets form the visible shimmer bed. The sparse
    # larger glints above are accents, rather than the primary texture.
    pv=n.new('ShaderNodeTexVoronoi');pv.name='Fine pearl facet density';pv.voronoi_dimensions='2D';pv.feature='F1';pv.inputs['Scale'].default_value=220
    l.new(inp.outputs['UV'],pv.inputs['Vector']);pv.location=(-650,-700)
    ps=n.new('ShaderNodeSeparateColor');ps.mode='RGB';l.new(pv.outputs['Color'],ps.inputs[0]);ps.location=(-430,-650)
    orient=n.new('ShaderNodeVectorMath');orient.operation='SCALE';orient.inputs['Scale'].default_value=.65;l.new(pv.outputs['Color'],orient.inputs[0]);orient.location=(-430,-850)
    center=n.new('ShaderNodeVectorMath');center.operation='ADD';center.inputs[1].default_value=(.175,.175,.85);l.new(orient.outputs[0],center.inputs[0]);center.location=(-200,-850)
    pn=n.new('ShaderNodeNormalMap');pn.name='Fine pearl orientations';pn.space='TANGENT';l.new(center.outputs[0],pn.inputs['Color']);pn.location=(30,-850)
    pt=n.new('ShaderNodeMixRGB');pt.name='Pearl pigment tint';pt.inputs[0].default_value=.16;pt.inputs[2].default_value=(.85,.88,.95,1);l.new(inp.outputs['Base Color'],pt.inputs[1]);pt.location=(-200,-600)
    brightness=n.new('ShaderNodeMapRange');brightness.name='Per-facet luster';brightness.inputs['To Min'].default_value=.22;brightness.inputs['To Max'].default_value=1.0;l.new(ps.outputs['Blue'],brightness.inputs['Value']);brightness.location=(-200,-400)
    pc=n.new('ShaderNodeVectorMath');pc.operation='SCALE';l.new(pt.outputs[0],pc.inputs[0]);l.new(brightness.outputs[0],pc.inputs['Scale']);pc.location=(40,-550)
    pearl=n.new('ShaderNodeBsdfPrincipled');pearl.name='Dense pearlescent shimmer';pearl.inputs['Metallic'].default_value=.88;pearl.inputs['Roughness'].default_value=.23;l.new(pc.outputs[0],pearl.inputs['Base Color']);l.new(pn.outputs[0],pearl.inputs['Normal']);pearl.location=(260,-700)
    fresnel=n.new('ShaderNodeFresnel');fresnel.name='Pearl edge emphasis';fresnel.inputs['IOR'].default_value=1.5;fresnel.location=(-420,-1100)
    whitening=n.new('ShaderNodeMath');whitening.name='Silver luster at grazing angles';whitening.operation='MULTIPLY_ADD';whitening.inputs[1].default_value=.85;whitening.inputs[2].default_value=.10;whitening.use_clamp=True;l.new(fresnel.outputs[0],whitening.inputs[0]);l.new(whitening.outputs[0],pt.inputs[0]);whitening.location=(-170,-1300)
    weight=n.new('ShaderNodeMath');weight.name='Shimmer coverage';weight.operation='MULTIPLY_ADD';weight.inputs[1].default_value=1.2;weight.inputs[2].default_value=.42;weight.use_clamp=True;l.new(fresnel.outputs[0],weight.inputs[0]);weight.location=(-170,-1100)
    bed=n.new('ShaderNodeMixShader');bed.name='Pearl bed over existing cat eye';l.new(weight.outputs[0],bed.inputs[0]);l.new(inp.outputs['Base Shader'],bed.inputs[1]);l.new(pearl.outputs[0],bed.inputs[2]);bed.location=(580,-500)
    l.new(bed.outputs[0],mix.inputs[1])
    l.new(mix.outputs[0],out.inputs['BSDF'])
    g['finish_version']=VERSION
    g['purpose']='Dense UV-locked pearlescent facets, brighter grazing edges and occasional larger glints. Existing base/cat-eye colors and animation retained.'
    return g

def attach_finish(wrapper,shared):
    """Wrap a local Glitter_UVFix group without changing its external interface."""
    if wrapper.library:raise ValueError('Wrapper must be local')
    existing=wrapper.nodes.get('Shared render glitter finish')
    if existing:
        existing.node_tree=shared;return False
    output=next(n for n in wrapper.nodes if n.type=='GROUP_OUTPUT' and n.is_active_output)
    source=next(link.from_socket for link in wrapper.links if link.to_node==output and link.to_socket.name=='BSDF')
    group_input=next(n for n in wrapper.nodes if n.type=='GROUP_INPUT')
    uv=next((n for n in wrapper.nodes if n.type=='TEX_COORD'),None)
    if uv is None:uv=wrapper.nodes.new('ShaderNodeTexCoord')
    node=wrapper.nodes.new('ShaderNodeGroup');node.name='Shared render glitter finish';node.label='Shared finish • edit in product asset';node.node_tree=shared
    node.location=(output.location.x-250,output.location.y+240)
    wrapper.links.new(source,node.inputs['Base Shader'])
    wrapper.links.new(group_input.outputs['Glitter Color 1'],node.inputs['Base Color'])
    wrapper.links.new(uv.outputs['UV'],node.inputs['UV'])
    wrapper.links.new(node.outputs['BSDF'],output.inputs['BSDF'])
    wrapper['shared_glitter_finish']=VERSION
    return True
