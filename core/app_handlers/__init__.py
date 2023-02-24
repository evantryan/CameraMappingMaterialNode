import bpy
from ...nodes.camera_mapping import CameraMappingShaderNode

def update_camera_mapping_node(node, depsgraph):
    use_scene_resolution_input = node.inputs.get('use scene resolution')
    if use_scene_resolution_input:
        use_scene_res = use_scene_resolution_input.default_value
        print('scene res', use_scene_res)
        print('HIDE!')

        res_x = node.inputs.get('resolution X')
        res_y = node.inputs.get('resolution Y')
        if use_scene_res:
            res_x.hide = True
            res_y.hide = True
            res_x.default_value = depsgraph.scene.render.resolution_x
            res_y.default_value = depsgraph.scene.render.resolution_y
        else:
            res_x.hide = False
            res_y.hide = False
    use_camera_values_input = node.inputs.get('use camera values')
    if use_camera_values_input:
        print('cam val', use_camera_values_input.default_value)


@bpy.app.handlers.persistent
# @override_nodes_app_handler
def depsgraph_update_post(scene, depsgraph):
    dg = bpy.context.evaluated_depsgraph_get()
    for thing in depsgraph.updates:
        if type(thing.id) == bpy.types.ShaderNodeTree:
            node_tree = thing.id.evaluated_get(dg)
            for node in node_tree.nodes:
                if type(node) == CameraMappingShaderNode:
                    print('update from depsgraph update post')
                    update_camera_mapping_node(node, depsgraph)
    # for thing in depsgraph.updates:
    #     print(type(thing.id))
    #     if type(thing.id) == bpy.types.ShaderNodeTree:
    #         for material in bpy.data.materials:
    #             if material.node_tree:
    #                 if type(material.node_tree) == bpy.types.ShaderNodeTree:
    #                     for node in material.node_tree.nodes:
    #                         if type(node) == CameraMappingShaderNode:
    #                             update_camera_mapping_node(node, depsgraph)

@bpy.app.handlers.persistent
def frame_change_post(scene, depsgraph):
    for material in bpy.data.materials:
        if material.node_tree:
            if type(material.node_tree) == bpy.types.ShaderNodeTree:
                for node in material.node_tree.nodes:
                    if type(node) == CameraMappingShaderNode:
                        print('update from frame change post')
                        update_camera_mapping_node(node, depsgraph)

def register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)
    bpy.app.handlers.frame_change_post.append(frame_change_post)

def unregister():
    bpy.app.handlers.frame_change_post.remove(frame_change_post)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)


if __name__ == "__main__":
    try:
        unregister()
    except Exception as e:
        print(e)
    
    register()