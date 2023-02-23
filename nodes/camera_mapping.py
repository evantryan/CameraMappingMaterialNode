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
    ('NodeSocketVector', {'name':'mapping', 'default_value': (.5,.5,.5)}),
]

external_outputs = [
    ('NodeSocketVector', {'name':'mapping', 'default_value': (.5,.5,.5)}),
]

internal_nodes = [
    ('NodeGroupInput', {'name':'Group Input'}),
    ('NodeGroupOutput', {'name':'Group Output'}),
    ('ShaderNodeTexCoord', {'name':'object mapping in'}), # object pointer will get set when the parent node gets set
    ('ShaderNodeSeparateXYZ', {'name':'separate object mapping'}),
    ('ShaderNodeCombineXYZ', {'name':'combine camera mapping'}),
    ('ShaderNodeVectorMath', {'name':'scale camera mapping'}), # SCALE
    ('ShaderNodeVectorMath', {'name':'offset camera mapping'}), # ADD
    ('ShaderNodeMath', {'name':'divide resolution'}), # DIV
    ('ShaderNodeMath', {'name':'divide focal sensor'}), # DIV
    ('ShaderNodeMath', {'name':'invert camera mapping z'}), # mult by -1

    

]

class CameraMappingShaderNode(bpy.types.ShaderNodeCustomGroup, utilities.NodeHelper):

    bl_name = 'CameraMappingShaderNode'
    bl_label = 'Camera Mapping'
    bl_width_default = 400
    bl_description = "Testing node with unique nodetree"
    
    camera: bpy.props.PointerProperty(type=bpy.types.Object, poll=utilities.camera_poll, name='camera')

    def _new_node_tree(self):
        #nt_name= '.' + self.bl_name + '_nodetree'
        nt_name= self.bl_name + '_nodetree'
        
        self.node_tree=bpy.data.node_groups.new(nt_name, 'ShaderNodeTree')
        self.addNodes(internal_nodes)
        self.addInputs(external_inputs)
        self.addOutputs(external_outputs)
        self.addLinks([])
        # self.addLinks([('inputs[0]', 'nodes["Ramp"].inputs[0]'),
        #             ('nodes["Ramp"].outputs[0]', 'outputs[0]')])
    
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