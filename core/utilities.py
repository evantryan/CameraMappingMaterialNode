import bpy


class NodeHelper():
    def __path_resolve__(self, obj, path):
        if "." in path:
            extrapath, path= path.rsplit(".", 1)
            obj = obj.path_resolve(extrapath)
        return obj, path
            
    def value_set(self, obj, path, val):
        obj, path=self.__path_resolve__(obj, path)
        setattr(obj, path, val)                

    def addNodes(self, nodes):
        for nodeitem in nodes:
            node=self.node_tree.nodes.new(nodeitem[0])
            for attr in nodeitem[1]:
                self.value_set(node, attr, nodeitem[1][attr])

    def addLinks(self, links):
        for link in links:
            if isinstance(link[0], str):
                if link[0].startswith('inputs'):
                    socketFrom=self.node_tree.path_resolve('nodes["Group Input"].outputs' + link[0][link[0].rindex('['):])
                else:
                    socketFrom=self.node_tree.path_resolve(link[0])
            else:
                socketFrom=link[0]
            if isinstance(link[1], str):
                if link[1].startswith('outputs'):
                    socketTo=self.node_tree.path_resolve('nodes["Group Output"].inputs' + link[1][link[1].rindex('['):])
                else:
                    socketTo=self.node_tree.path_resolve(link[1])
            else:
                socketTo=link[1]
            self.node_tree.links.new(socketFrom, socketTo)

    def addInputs(self, inputs):
        for inputitem in inputs:
            name = inputitem[1].pop('name')
            socketInterface=self.node_tree.inputs.new(inputitem[0], name)
            socket=self.path_resolve(socketInterface.path_from_id())
            for attr in inputitem[1]:
                if attr in ['default_value', 'hide', 'hide_value', 'enabled']:
                    self.value_set(socket, attr, inputitem[1][attr])
                else:
                    self.value_set(socketInterface, attr, inputitem[1][attr])
            
    def addOutputs(self, outputs):
        for outputitem in outputs:
            name = outputitem[1].pop('name')
            socketInterface=self.node_tree.outputs.new(outputitem[0], name)
            socket=self.path_resolve(socketInterface.path_from_id())
            for attr in outputitem[1]:
                if attr in ['default_value', 'hide', 'hide_value', 'enabled']:
                    self.value_set(socket, attr, outputitem[1][attr])
                else:
                    self.value_set(socketInterface, attr, outputitem[1][attr])

def camera_poll(self, obj):
    return obj.type == "CAMERA"

def append_math_node(nodes, operation='ADD', name=None, a_default=0.0, b_default=0.0, use_clamp=False, parent=None, custom_color=None):
    math = nodes.new('ShaderNodeMath')
    
    # Options: 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'SINE',
    # 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT',
    # 'POWER', 'LOGARITHM', 'MINIMUM', 'MAXIMUM', 'ROUND',
    # 'LESS_THAN', 'GREATER_THAN', 'MODULO', 'ABSOLUTE'
    math.operation = operation
    math.parent = parent
    
    # Clamp to range 0 .. 1.
    math.use_clamp = use_clamp
 
    # Default to operation if no name provided.
    if name:
        math.name = name
    else:
        math.name = operation.replace('_', ' ').capitalize()

    if custom_color:
        math.use_custom_color = True
        math.color = custom_color
        
    # Left operand.
    math.inputs[0].default_value = a_default

    # Right operand.
    math.inputs[1].default_value = b_default

    return math


def create_camera_mapping_group():
    group = bpy.data.node_groups.new('camera projection mapping', 'ShaderNodeTree')

    # Create input and output nodes within group.
    group_input = group.nodes.new('NodeGroupInput')
    group_input.location = (-2000,0)
    group_output = group.nodes.new('NodeGroupOutput')

    group.use_fake_user = False

    # create inputs
    use_scene_resolution = group.inputs.new('NodeSocketBool', 'use scene resolution')
    use_scene_resolution.default_value = True

    group.inputs.new('NodeSocketInt', 'resolution X')
    group.inputs.new('NodeSocketInt', 'resolution Y')
    
    use_camera_settings = group.inputs.new('NodeSocketBool', 'use camera settings')
    use_camera_settings.default_value = True

    group.inputs.new('NodeSocketFloat', 'focal length')
    group.inputs.new('NodeSocketFloat', 'sensor width')

    include_back_face = group.inputs.new('NodeSocketBool', 'include back face')
    include_back_face.default_value = True

    group.inputs.new('NodeSocketVector', 'mapping') # this is mapping for front of back facing normals that aren't mapped with the camera

    # create outputs
    group.outputs.new('NodeSocketVector', 'mapping')

    # create nodes and connections
    tex_coordinate = group.nodes.new('ShaderNodeTexCoord') # this will get input from the camera itself
    tex_coordinate.location = (group_input.location[0], group_input.location[1] + 300)

    sep_xyz = group.nodes.new('ShaderNodeSeparateXYZ')
    sep_xyz.location = (tex_coordinate.location[0] + 400, tex_coordinate.location[1])

    group.links.new(sep_xyz.inputs[0], tex_coordinate.outputs[3])

    div1 = append_math_node(group.nodes, operation='DIVIDE')
    div1.location = (group_input.location[0] + 200, group_input.location[1] + 100)

    div2 = append_math_node(group.nodes, operation='DIVIDE')
    div2.location = (group_input.location[0] + 200, group_input.location[1] - 100)

    group.links.new(div1.inputs[0], group_input.outputs[1])
    group.links.new(div1.inputs[1], group_input.outputs[2])

    group.links.new(div2.inputs[0], group_input.outputs[4])
    group.links.new(div2.inputs[1], group_input.outputs[5])

    div3 = append_math_node(group.nodes, operation='DIVIDE')
    div4 = append_math_node(group.nodes, operation='DIVIDE')

    mult1 =  append_math_node(group.nodes, operation='MULTIPLY')
    mult1.inputs[1].default_value = -1
    mult1.location = (sep_xyz.location[0]+200, sep_xyz.location[1]-50)

    div3.location = (mult1.location[0]+200, mult1.location[1]+100)
    div4.location = (mult1.location[0]+200, mult1.location[1]-100)

    group.links.new(mult1.inputs[0], sep_xyz.outputs[2])

    group.links.new(div3.inputs[0], sep_xyz.outputs[0])
    group.links.new(div3.inputs[1], mult1.outputs[0])

    group.links.new(div4.inputs[0], sep_xyz.outputs[1])
    group.links.new(div4.inputs[1], mult1.outputs[0])

    mult2 =  append_math_node(group.nodes, operation='MULTIPLY')
    mult2.location = (div4.location[0]+200, div4.location[1]-50)

    group.links.new(mult2.inputs[0], div4.outputs[0])
    group.links.new(mult2.inputs[1], div1.outputs[0])

    comb_xyz = group.nodes.new('ShaderNodeCombineXYZ')
    comb_xyz.inputs[2].default_value = 1
    comb_xyz.location = (div4.location[0]+400, mult1.location[1])

    group.links.new(comb_xyz.inputs[0], div3.outputs[0])
    group.links.new(comb_xyz.inputs[1], mult2.outputs[0])

    scale_mapping = group.nodes.new('ShaderNodeVectorMath')
    scale_mapping.operation = 'SCALE'
    scale_mapping.location = (comb_xyz.location[0]+200, comb_xyz.location[1]-200)

    group.links.new(scale_mapping.inputs[0], comb_xyz.outputs[0])
    group.links.new(scale_mapping.inputs[3], div2.outputs[0])

    offset_mapping = group.nodes.new('ShaderNodeVectorMath')
    offset_mapping.operation = 'ADD'
    offset_mapping.inputs[1].default_value = (.5,.5,.5)
    offset_mapping.location = (scale_mapping.location[0]+200, scale_mapping.location[1])

    group.links.new(offset_mapping.inputs[0], scale_mapping.outputs[0])

    # adding stuff to only project on backside can use these to switch between camera mapping and existing uvs
    geo_attrs = group.nodes.new('ShaderNodeNewGeometry')
    comb_xyz2 = group.nodes.new('ShaderNodeCombineXYZ') # this will get input from the addon/camera info
    comb_xyz2.name = 'camera_location_input'

    dot_prod = group.nodes.new('ShaderNodeVectorMath')
    dot_prod.operation = 'DOT_PRODUCT'

    mix_mapping = group.nodes.new('ShaderNodeMixRGB')
    mix_mapping.location = (offset_mapping.location[0]+200, offset_mapping.location[1])
    comb_xyz2.location = (comb_xyz.location[0], comb_xyz.location[1]-400)
    geo_attrs.location = (comb_xyz2.location[0], comb_xyz2.location[1]-200)
    dot_prod.location = (scale_mapping.location[0], scale_mapping.location[1]-300)

    group.links.new(dot_prod.inputs[0], comb_xyz2.outputs[0])
    group.links.new(dot_prod.inputs[1], geo_attrs.outputs[1])
    group.links.new(mix_mapping.inputs[0], dot_prod.outputs[1])

    group.links.new(group_output.inputs[0], offset_mapping.outputs[0])


    # would use these to mix in original UV if project all the way through isn't wanted

    return group


def append_group_node(data=bpy.data, name='GroupNode', use_fake_user=False, in_sockets=[], out_sockets=[]):
    
    # Create group.
    group = data.node_groups.new(name, 'ShaderNodeTree')

    # Create input and output nodes within group.
    group.nodes.new('NodeGroupInput')
    group.nodes.new('NodeGroupOutput')

    # If the group has a fake user, then it will be retained in memory after all other
    # instances that use it are removed.
    group.use_fake_user = use_fake_user

    # Inputs
    inputs = group.inputs()
    
    # Loop through list.
    for in_socket in in_sockets:
        
        # Create new input.
        curr = inputs.new(in_socket.get('data_type', 'NodeSocketFloat'), in_socket.get('name', 'Value'))

        # Assign default value.
        if curr.bl_socket_idname == 'NodeSocketFloat':
            curr.default_value = in_socket.get('default_value', 0.0)
            
        # Default vector value is 1.0 / sqrt(3.0), where vector has magnitude of 1.0.
        elif curr.bl_socket_idname == 'NodeSocketVector':
            curr.default_value = in_socket.get('default_value', (0.57735, 0.57735, 0.57735))
            
        # Colors include alpha/transparency as the fourth component.
        elif curr.bl_socket_idname == 'NodeSocketColor':
            curr.default_value = in_socket.get('default_value', (0.0, 0.0, 0.0, 0.0))

        # Assign min and max values to nodes which contain them.
        if curr.bl_socket_idname == 'NodeSocketFloat' or curr.bl_socket_idname == 'NodeSocketVector':
            curr.min_value = in_socket.get('min_value', -10000.0)
            curr.max_value = in_socket.get('max_value', 10000.0)

    # Outputs.
    outputs = group.outputs
    
    # Loop through list.
    for out_socket in out_sockets:
        
        # Create new output.
        curr = outputs.new(out_socket.get('data_type', 'NodeSocketFloat'), out_socket.get('name', 'Value'))

        # Assign default value.
        if curr.bl_socket_idname == 'NodeSocketFloat':
            curr.default_value = out_socket.get('default_value', 0.0)
        elif curr.bl_socket_idname == 'NodeSocketVector':
            curr.default_value = out_socket.get('default_value', (0.57735, 0.57735, 0.57735))
        elif curr.bl_socket_idname == 'NodeSocketColor':
            curr.default_value = out_socket.get('default_value', (0.0, 0.0, 0.0, 0.0))

        # Assign min and max values to nodes which contain them.
        if curr.bl_socket_idname == 'NodeSocketFloat' or curr.bl_socket_idname == 'NodeSocketVector':
            curr.min_value = out_socket.get('min_value', -10000.0)
            curr.max_value = out_socket.get('max_value', 10000.0)

    return group

