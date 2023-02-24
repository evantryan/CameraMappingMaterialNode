import bpy
from ..core import utilities

external_inputs = [
    #('NodeSocketFloat', {'name':'Value', 'default_value':0.500, 'min_value':0.0, 'max_value':1.0})
    ('NodeSocketBool', {'name':'use scene resolution', 'default_value':True}),
    ('NodeSocketFloat', {'name':'resolution X', 'default_value':1920.000}),
    ('NodeSocketFloat', {'name':'resolution Y', 'default_value':1080.000}),
    ('NodeSocketBool', {'name':'use camera values', 'default_value':True}),
    ('NodeSocketFloat', {'name':'focal length', 'default_value':50}),
    ('NodeSocketFloat', {'name':'sensor width', 'default_value':36}),
    ('NodeSocketVector', {'name':'mapping', 'default_value': (.5,.5,.5), 'hide_value': True}),
]

external_outputs = [
    ('NodeSocketVector', {'name':'mapping', 'default_value': (.5,.5,.5)}),
]

internal_nodes = [
    ('NodeGroupInput', {'name':'Group Input'}),
    ('NodeGroupOutput', {'name':'Group Output'}),
    ('ShaderNodeTexCoord', {'name':'object mapping in'}), # object pointer will get set when the parent node gets set
    ('ShaderNodeSeparateXYZ', {'name':'separate object mapping'}),
    ('ShaderNodeCombineXYZ', {'name':'combine camera mapping', 'inputs[2].default_value': 1}),
    ('ShaderNodeVectorMath', {'name':'scale camera mapping', 'operation': 'SCALE'}), # SCALE
    ('ShaderNodeVectorMath', {'name':'offset camera mapping', 'operation': 'ADD', 'inputs[1].default_value': (.5,.5,.5)}), # ADD
    ('ShaderNodeMath', {'name':'divide resolution', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeMath', {'name':'divide focal sensor', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeMath', {'name':'invert camera mapping z', 'operation': 'MULTIPLY', 'inputs[1].default_value': -1}), # mult by -1
    ('ShaderNodeMath', {'name':'multiply resolution', 'operation': 'MULTIPLY'}),
    ('ShaderNodeMath', {'name':'divide x component', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeMath', {'name':'divide y component', 'operation': 'DIVIDE'}), # DIV
]

internal_links = [
    ('inputs[1]', 'nodes["divide resolution"].inputs[0]'),
    ('inputs[2]', 'nodes["divide resolution"].inputs[1]'),
    ('inputs[4]', 'nodes["divide focal sensor"].inputs[0]'),
    ('inputs[5]', 'nodes["divide focal sensor"].inputs[1]'),
    ('nodes["object mapping in"].outputs[3]', 'nodes["separate object mapping"].inputs[0]'),
    ('nodes["separate object mapping"].outputs[0]', 'nodes["divide x component"].inputs[0]'),
    ('nodes["separate object mapping"].outputs[1]', 'nodes["divide y component"].inputs[0]'),
    ('nodes["separate object mapping"].outputs[2]', 'nodes["invert camera mapping z"].inputs[0]'),
    ('nodes["divide x component"].outputs[0]', 'nodes["combine camera mapping"].inputs[0]'),
    ('nodes["divide y component"].outputs[0]', 'nodes["multiply resolution"].inputs[0]'),
    ('nodes["divide resolution"].outputs[0]', 'nodes["multiply resolution"].inputs[1]'),
    ('nodes["invert camera mapping z"].outputs[0]', 'nodes["divide x component"].inputs[1]'),
    ('nodes["invert camera mapping z"].outputs[0]', 'nodes["divide y component"].inputs[1]'),
    ('nodes["multiply resolution"].outputs[0]', 'nodes["combine camera mapping"].inputs[1]'),
    ('nodes["combine camera mapping"].outputs[0]','nodes["scale camera mapping"].inputs[0]' ),
    ('nodes["divide focal sensor"].outputs[0]','nodes["scale camera mapping"].inputs[3]' ),
    ('nodes["scale camera mapping"].outputs[0]', 'nodes["offset camera mapping"].inputs[0]' ),
    ('nodes["offset camera mapping"].outputs[0]', 'outputs[0]' ),
    # will need to create options for only projecting on the back or front faces. 
    #     camera position dot product with geometry normal can provide the switch

]

class CameraMappingShaderNode(bpy.types.ShaderNodeCustomGroup, utilities.NodeHelper):

    bl_name = 'CameraMappingShaderNode'
    bl_label = 'Camera Mapping'
    bl_width_default = 400
    bl_description = "Testing node with unique nodetree"

    def camera_update(self, context):
        for node in self.node_tree.nodes:
            if 'object mapping in' in node.name:
                node.object = self.camera
    
    camera: bpy.props.PointerProperty(type=bpy.types.Object, poll=utilities.camera_poll, update=camera_update, name='camera')

    def _new_node_tree(self):
        nt_name= '.' + self.bl_name + '_nodetree'
        #nt_name= self.bl_name + '_nodetree'
        
        self.node_tree=bpy.data.node_groups.new(nt_name, 'ShaderNodeTree')
        self.addNodes(internal_nodes)
        self.addInputs(external_inputs)
        self.addOutputs(external_outputs)
        self.addLinks(internal_links)

    
    def init(self, context):
        self._new_node_tree()

    def draw_buttons(self, context, layout):
        # layout.template_color_ramp(self.node_tree.nodes['Ramp'], 'color_ramp' , expand = True) 
        layout.prop(self, 'camera')       

    def copy(self, node):
        if node.node_tree:
            self.node_tree=node.node_tree.copy()
        else:
            self._new_node_tree()

    def free(self):
        nt = self.node_tree
        bpy.data.node_groups.remove(nt, do_unlink=True)