import bpy
import nodeitems_utils
from nodeitems_builtins import ShaderNodeCategory


def getCategory(catid, catname):
    nc=nodeitems_utils._node_categories
    for ident in nc:
        for idx, category in enumerate(nc[ident][0]):
            if category.identifier==catid and category.name==catname:
                return idx, ident, category, nc[ident][2][idx]
    return None, None, None, None


def delCat(catid, catname):
    index, ident, cat, mt=getCategory(catid, catname)
    if cat:
        bpy.utils.unregister_class(mt)
        nodeitems_utils._node_categories[ident][0].remove(cat)
        nodeitems_utils._node_categories[ident][2].remove(mt)


def addCat(category, ident='SHADER', index=None):
    def draw_node_item(self, context):
        layout = self.layout
        col = layout.column()
        for item in self.category.items(context):
            item.draw(item, col, context)
    mt = type("NODE_MT_category_" + category.identifier, (bpy.types.Menu,), {
        "bl_space_type": 'NODE_EDITOR',
        "bl_label": category.name,
        "category": category,
        "poll": category.poll,
        "draw": draw_node_item,
        })
    bpy.utils.register_class(mt)
    if index:
        nodeitems_utils._node_categories[ident][0].insert(index, category)
        nodeitems_utils._node_categories[ident][2].insert(index, mt)
    else:
        nodeitems_utils._node_categories[ident][0].append(category)
        nodeitems_utils._node_categories[ident][2].append(mt)


def node_menu_include(catid, catname, node):
    only_cycles=True
    index, ident, cat, mt=getCategory(catid, catname)
    if cat:
        itemslist=list(cat.items(context=None))
        for item in itemslist:
            if item.nodetype==node.bl_name:
                return
            if item.poll:
                if item.poll.__code__.co_name in _eevee_polls:
                    only_cycles=False
            else:
                only_cycles=False
        itemslist.append(nodeitems_utils.NodeItem(node.bl_name))
        delCat(catid, catname)
    else:
        itemslist=[nodeitems_utils.NodeItem(node.bl_name)]

    category=ShaderNodeCategory(catid, catname, items=itemslist)
    addCat(category, index=index)

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


# def append_group_node(data=bpy.data, name='GroupNode', use_fake_user=False, in_sockets=[], out_sockets=[]):
    
#     # Create group.
#     group = data.node_groups.new(name, 'ShaderNodeTree')

#     # Create input and output nodes within group.
#     group.nodes.new('NodeGroupInput')
#     group.nodes.new('NodeGroupOutput')

#     # If the group has a fake user, then it will be retained in memory after all other
#     # instances that use it are removed.
#     group.use_fake_user = use_fake_user

#     # Inputs
#     inputs = group.inputs()
    
#     # Loop through list.
#     for in_socket in in_sockets:
        
#         # Create new input.
#         curr = inputs.new(in_socket.get('data_type', 'NodeSocketFloat'), in_socket.get('name', 'Value'))

#         # Assign default value.
#         if curr.bl_socket_idname == 'NodeSocketFloat':
#             curr.default_value = in_socket.get('default_value', 0.0)
            
#         # Default vector value is 1.0 / sqrt(3.0), where vector has magnitude of 1.0.
#         elif curr.bl_socket_idname == 'NodeSocketVector':
#             curr.default_value = in_socket.get('default_value', (0.57735, 0.57735, 0.57735))
            
#         # Colors include alpha/transparency as the fourth component.
#         elif curr.bl_socket_idname == 'NodeSocketColor':
#             curr.default_value = in_socket.get('default_value', (0.0, 0.0, 0.0, 0.0))

#         # Assign min and max values to nodes which contain them.
#         if curr.bl_socket_idname == 'NodeSocketFloat' or curr.bl_socket_idname == 'NodeSocketVector':
#             curr.min_value = in_socket.get('min_value', -10000.0)
#             curr.max_value = in_socket.get('max_value', 10000.0)

#     # Outputs.
#     outputs = group.outputs
    
#     # Loop through list.
#     for out_socket in out_sockets:
        
#         # Create new output.
#         curr = outputs.new(out_socket.get('data_type', 'NodeSocketFloat'), out_socket.get('name', 'Value'))

#         # Assign default value.
#         if curr.bl_socket_idname == 'NodeSocketFloat':
#             curr.default_value = out_socket.get('default_value', 0.0)
#         elif curr.bl_socket_idname == 'NodeSocketVector':
#             curr.default_value = out_socket.get('default_value', (0.57735, 0.57735, 0.57735))
#         elif curr.bl_socket_idname == 'NodeSocketColor':
#             curr.default_value = out_socket.get('default_value', (0.0, 0.0, 0.0, 0.0))

#         # Assign min and max values to nodes which contain them.
#         if curr.bl_socket_idname == 'NodeSocketFloat' or curr.bl_socket_idname == 'NodeSocketVector':
#             curr.min_value = out_socket.get('min_value', -10000.0)
#             curr.max_value = out_socket.get('max_value', 10000.0)

#     return group

