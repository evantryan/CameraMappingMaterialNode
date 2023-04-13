import bpy
from ...nodes.camera_mapping import CameraMappingShaderNode


def update_all_camera_mapping_nodes(context):
    for material in bpy.data.materials:
        if isinstance(material.node_tree, bpy.types.ShaderNodeTree):
            for node in material.node_tree.nodes:
                if isinstance(node, CameraMappingShaderNode):
                    update_camera_mapping_node(node, context.scene)

        
def get_internal_node(group_node, node_name):
    for node in group_node.node_tree.nodes:
        if node_name in node.name:
            return node


def update_camera_mapping_node(node, scene):
    mapping_in = node.inputs.get('mapping')
    mapping_in.hide_value = True

    if node.camera:
        camera = node.camera

        # update location
        camera_position_node = get_internal_node(node, 'camera position')
        camera_world_postition = camera.matrix_world.to_translation()
        camera_position_node.inputs[0].default_value = camera_world_postition[0]
        camera_position_node.inputs[1].default_value = camera_world_postition[1]
        camera_position_node.inputs[2].default_value = camera_world_postition[2]

        # update facing
        facing_toggle = get_internal_node(node, 'facing toggle')
        front_or_back_facing = get_internal_node(node, 'front or back facing')
        if node.facing == 'both':
            front_or_back_facing.mute = True
        elif node.facing == 'front':
            facing_toggle.mute = False
            front_or_back_facing.mute = False
        elif node.facing == 'back':
            facing_toggle.mute = True
            front_or_back_facing.mute = False

        # update mapping
        res_x = node.inputs.get('resolution X')
        res_y = node.inputs.get('resolution Y')
        if node.use_scene_resolution:
            res_x.hide = True
            res_y.hide = True
            res_x.default_value = scene.render.resolution_x
            res_y.default_value = scene.render.resolution_y
        else:
            res_x.hide = False
            res_y.hide = False

        focal = node.inputs.get('focal length')
        sensor = node.inputs.get('sensor width')
        if node.use_camera_values:
            focal.hide = True
            focal.default_value = camera.data.lens
            sensor.hide = True

            # maybe the following should be internal nodes instead?
            if camera.data.sensor_fit == 'HORIZONTAL':
                sensor.default_value = camera.data.sensor_width
            elif camera.data.sensor_fit == 'VERTICAL':
                sensor.default_value = camera.data.sensor_height * scene.render.resolution_x / scene.render.resolution_y
            elif camera.data.sensor_fit == 'AUTO': 
                if scene.render.resolution_x >= scene.render.resolution_y: # square or wider
                    sensor.default_value = camera.data.sensor_width
                else:
                    sensor.default_value = camera.data.sensor_width * scene.render.resolution_x / scene.render.resolution_y

        else:
            focal.hide = False
            sensor.hide = False

    else:
        print(node.name, 'has no camera specified')


def update_camera_mapping_nodes_from_depsgraph(scene, depsgraph=None):
    if not depsgraph:
        depsgraph = bpy.context.evaluated_depsgraph_get()

    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.ShaderNodeTree):
            shader_tree = update.id.original
            for node in shader_tree.nodes:
                if isinstance(node, CameraMappingShaderNode):
                    update_camera_mapping_node(node, depsgraph.scene)


@bpy.app.handlers.persistent
def depsgraph_update_post(scene, depsgraph):
    update_camera_mapping_nodes_from_depsgraph(scene, depsgraph)


def register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)


if __name__ == "__main__":
    try:
        unregister()
    except Exception as e:
        print(e)
    
    register()