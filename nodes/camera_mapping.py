import bpy
from ..core import utilities

external_inputs = [
    ('NodeSocketFloat', {'name':'resolution X', 'default_value':1920.000, 'hide': True}),
    ('NodeSocketFloat', {'name':'resolution Y', 'default_value':1080.000, 'hide': True}),
    ('NodeSocketFloat', {'name':'focal length', 'default_value':50, 'hide': True}),
    ('NodeSocketFloat', {'name':'sensor width', 'default_value':36, 'hide': True}),
    ('NodeSocketVector', {'name':'mapping', 'default_value': (.5,.5,.5), 'hide_value': True}),
]

external_outputs = [
    ('NodeSocketVector', {'name':'mapping', 'default_value': (.5,.5,.5)}),
    ('NodeSocketFloat', {'name':'mask', 'default_value': 1.0}),
]

internal_nodes = [
    ('NodeGroupInput', {'name':'Group Input'}),
    ('NodeGroupOutput', {'name':'Group Output'}),
    ('ShaderNodeTexCoord', {'name':'object mapping in'}), # object pointer will get set when the parent node gets set
    ('ShaderNodeSeparateXYZ', {'name':'separate object mapping'}),
    ('ShaderNodeCombineXYZ', {'name':'combine camera mapping', 'inputs[2].default_value': 0.0}),
    ('ShaderNodeVectorMath', {'name':'scale camera mapping', 'operation': 'SCALE'}), # SCALE
    ('ShaderNodeVectorMath', {'name':'offset camera mapping', 'operation': 'ADD', 'inputs[1].default_value': (.5,.5,.5)}), # ADD
    ('ShaderNodeMath', {'name':'divide resolution', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeMath', {'name':'divide focal sensor', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeMath', {'name':'invert camera mapping z', 'operation': 'MULTIPLY', 'inputs[1].default_value': -1}), # mult by -1
    ('ShaderNodeMath', {'name':'multiply resolution', 'operation': 'MULTIPLY'}),
    ('ShaderNodeMath', {'name':'divide x component', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeMath', {'name':'divide y component', 'operation': 'DIVIDE'}), # DIV
    ('ShaderNodeCombineXYZ', {'name':'camera position'}),
    ('ShaderNodeVectorMath', {'name':'facing mask dot product', 'operation': 'DOT_PRODUCT'}), # DOT_PRODUCT
    ('ShaderNodeNewGeometry', {'name':'geometry input'}),
    ('ShaderNodeMixRGB', {'name':'front or back facing'}),
    ('ShaderNodeInvert', {'name':'facing toggle'}),
    ('ShaderNodeSeparateXYZ', {'name':'separate for mask'}),
    ('ShaderNodeMath', {'name':'mask greater than A', 'operation': 'GREATER_THAN', 'inputs[1].default_value': 1}),
    ('ShaderNodeMath', {'name':'mask greater than B', 'operation': 'GREATER_THAN','inputs[1].default_value': 1}),
    ('ShaderNodeMath', {'name':'mask less than A', 'operation': 'LESS_THAN','inputs[1].default_value': 0}),
    ('ShaderNodeMath', {'name':'mask less than B', 'operation': 'LESS_THAN','inputs[1].default_value': 0}),
    ('ShaderNodeMath', {'name':'mask max A', 'operation': 'MAXIMUM'}),
    ('ShaderNodeMath', {'name':'mask max B', 'operation': 'MAXIMUM'}),
    ('ShaderNodeMath', {'name':'mask max C', 'operation': 'MAXIMUM'}),
]

internal_links = [
    ('inputs[0]', 'nodes["divide resolution"].inputs[0]'),
    ('inputs[1]', 'nodes["divide resolution"].inputs[1]'),
    ('inputs[2]', 'nodes["divide focal sensor"].inputs[0]'),
    ('inputs[3]', 'nodes["divide focal sensor"].inputs[1]'),
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
    ('nodes["combine camera mapping"].outputs[0]','nodes["scale camera mapping"].inputs[0]'),
    ('nodes["divide focal sensor"].outputs[0]','nodes["scale camera mapping"].inputs[3]'),
    ('nodes["scale camera mapping"].outputs[0]', 'nodes["offset camera mapping"].inputs[0]'),
    ('nodes["offset camera mapping"].outputs[0]', 'nodes["front or back facing"].inputs[1]'),
    ('inputs[4]', 'nodes["front or back facing"].inputs[2]'),
    ('nodes["camera position"].outputs[0]', 'nodes["facing mask dot product"].inputs[0]'),
    ('nodes["geometry input"].outputs[1]', 'nodes["facing mask dot product"].inputs[1]'),
    ('nodes["facing mask dot product"].outputs[1]', 'nodes["facing toggle"].inputs[1]'),
    ('nodes["facing toggle"].outputs[0]', 'nodes["front or back facing"].inputs[0]'),
    ('nodes["front or back facing"].outputs[0]', 'outputs[0]' ),
    ('nodes["offset camera mapping"].outputs[0]', 'nodes["separate for mask"].inputs[0]'),
    ('nodes["separate for mask"].outputs[0]', 'nodes["mask greater than A"].inputs[0]'),
    ('nodes["separate for mask"].outputs[0]', 'nodes["mask less than A"].inputs[0]'),
    ('nodes["separate for mask"].outputs[1]', 'nodes["mask greater than B"].inputs[0]'),
    ('nodes["separate for mask"].outputs[1]', 'nodes["mask less than B"].inputs[0]'),
    ('nodes["mask greater than A"].outputs[0]', 'nodes["mask max A"].inputs[0]'),
    ('nodes["mask less than A"].outputs[0]', 'nodes["mask max A"].inputs[1]'),
    ('nodes["mask greater than B"].outputs[0]', 'nodes["mask max B"].inputs[0]'),
    ('nodes["mask less than B"].outputs[0]', 'nodes["mask max A"].inputs[1]'),
    ('nodes["mask max A"].outputs[0]', 'nodes["mask max C"].inputs[0]'),
    ('nodes["mask max B"].outputs[0]', 'nodes["mask max C"].inputs[1]'),
    ('nodes["mask max C"].outputs[0]', 'outputs[1]'),
]

class CameraMappingShaderNode(bpy.types.ShaderNodeCustomGroup, utilities.NodeHelper):

    bl_name = 'CameraMappingShaderNode'
    bl_label = 'Camera Mapping'
    bl_width_default = 400
    bl_description = "Testing node with unique nodetree"

    def camera_update(caller, context):
        for node in caller.node_tree.nodes:
            if 'object mapping in' in node.name:
                node.object = caller.camera
    
    camera: bpy.props.PointerProperty(type=bpy.types.Object, poll=utilities.camera_poll, update=camera_update, name='camera')
    use_scene_resolution: bpy.props.BoolProperty(default=True, )#update=use_camera_values_update)
    use_camera_values: bpy.props.BoolProperty(default=True, )#update=use_camera_values_update)

    facing_options = [
        ("both", 'both', '',1 ),
        ("front", 'front', '',2),
        ("back",'back', '',3),
    ]
    facing: bpy.props.EnumProperty(items=facing_options, default='both')

    def _new_node_tree(self):
        nt_name= '.' + self.bl_name + '_nodetree'
        
        self.node_tree=bpy.data.node_groups.new(nt_name, 'ShaderNodeTree')
        self.addNodes(internal_nodes)
        self.addInputs(external_inputs)
        self.addOutputs(external_outputs)
        self.addLinks(internal_links)

    
    def init(self, context):
        self._new_node_tree()

    def draw_buttons(self, context, layout):
        if not self.camera:
            box = layout.box()
            box.alert = True
            box.label(text='a camera is required')
        layout.prop(self, 'camera')
        layout.prop(self, 'facing')
        layout.prop(self, 'use_scene_resolution')
        layout.prop(self, 'use_camera_values')


    def copy(self, node):
        if node.node_tree:
            self.node_tree=node.node_tree.copy()
        else:
            self._new_node_tree()

    def free(self):
        nt = self.node_tree
        bpy.data.node_groups.remove(nt, do_unlink=True)