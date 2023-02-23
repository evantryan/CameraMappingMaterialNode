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

class CameraMappingNodeGroup(bpy.types.ShaderNodeCustomGroup, NodeHelper):
    bl_label = "Node Group"
    bl_width_default = 500
    bl_description = 'Camera mapping'

    camera: bpy.props.PointerProperty(type=bpy.types.Object, poll=camera_poll, name='camera')


    def draw_buttons(self, context, layout):
        col = layout.column()
        row = col.row()
        row.prop(self, 'camera')


    def pass_through_override_data(self, from_socket, to_socket):
        utilities.assign_entity_list_to_socket(from_socket.entity_list, to_socket)


    def pass_through_default_values(self, from_socket, to_socket):
        if from_socket.is_linked and from_socket.links:
            for link in from_socket.links:
                default_value = link.from_socket.default_value
        else:
            default_value = from_socket.default_value

        to_socket.default_value = default_value


    def pass_input_values(self):
        for input_socket in self.inputs:
            group_input_node = utilities.get_input_node_from_group_node_inner_tree(self)
            inner_socket = utilities.get_node_output_socket_by_identifier(group_input_node, input_socket.identifier)

            if input_socket.bl_idname == 'IDListSocket':
                # default value here will just be the count of items. the override data is held in config
                entity_list = utilities.get_entity_list_from_socket(input_socket)
                utilities.assign_entity_list_to_socket(entity_list, input_socket)
                self.pass_through_override_data(input_socket, inner_socket)

            else:
                # this method only supports one input link
                self.pass_through_default_values(input_socket, inner_socket)


    def pass_output_values(self):
        for output_socket in self.outputs:
            group_output_node = utilities.get_output_node_from_group_node_inner_tree(self)
            inner_socket = utilities.get_node_input_socket_by_identifier(group_output_node, output_socket.identifier)

            if output_socket.bl_idname == 'IDListSocket':
                entity_list = utilities.get_entity_list_from_socket(inner_socket)
                utilities.assign_entity_list_to_socket(entity_list, inner_socket)
                self.pass_through_override_data(inner_socket, output_socket)

            else:
                # this method only supports one input link
                self.pass_through_default_values(inner_socket, output_socket)


    def run(self):
        if not self.mute:
            self.pass_input_values()
            self.pass_output_values()
                
                
    def draw_label(self):
        return "Override Node Group"


    def copy(self, node):
        #print("Copying from node ", node)
        pass


    def free(self):
        #print("Removing node ", self, ", Goodbye!")
        pass


class ShaderTestingNode1(bpy.types.ShaderNodeCustomGroup, NodeHelper):

    bl_name = 'ShaderTestingNode1'
    bl_label = 'Simple Color Ramp'
    bl_width_default = 500
    bl_description = "Testing node with unique nodetree"
    
    camera: bpy.props.PointerProperty(type=bpy.types.Object, poll=camera_poll, name='camera')

    def _new_node_tree(self):
        nt_name= '.' + self.bl_name + '_nodetree'
        self.node_tree=bpy.data.node_groups.new(nt_name, 'ShaderNodeTree')
        self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
                    ('NodeGroupOutput', {'name':'Group Output'}),
                    ('ShaderNodeValToRGB', {'name':'Ramp'})])
        self.addInputs([('NodeSocketFloat', {'name':'Value', 'default_value':0.500, 'min_value':0.0, 'max_value':1.0})])
        self.addOutputs([('NodeSocketColor', {'name':'Color'})])
        self.addLinks([('inputs[0]', 'nodes["Ramp"].inputs[0]'),
                    ('nodes["Ramp"].outputs[0]', 'outputs[0]')])
        
    def update(self):
        print('ShaderTestNodeUpdate')
    
    def init(self, context):
        self._new_node_tree()

    def draw_buttons(self, context, layout):
        layout.template_color_ramp(self.node_tree.nodes['Ramp'], 'color_ramp' , expand = True) 
        layout.prop(self, 'camera')       

    def copy(self, node):
        if node.node_tree:
            self.node_tree=node.node_tree.copy()
        else:
            self._new_node_tree()

    def free(self):
        nt = self.node_tree
        bpy.data.node_groups.remove(nt, do_unlink=True)