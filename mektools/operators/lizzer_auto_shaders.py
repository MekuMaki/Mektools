import bpy
from os import path

# Define shader type mappings for automatic material fixes
shaderType = {
    "_skin_": "Dawntrail Skin Shader Skul Version",
    "_fac_": "Dawntrail Face Shader Skul Version",
    "_hir_": "Dawntrail Hair Shader Skul Version",
    "_hair_": "Dawntrail Hair Shader Skul Version",
    "_iri_": "Dawntrail Eye Shader Skul Version",
    "_etc_a_": "Dawntrail etc_a Shader Skul Version",
    "_etc_b_": "Dawntrail etc_b Shader Skul Version",
    "_etc_c_": "Dawntrail etc_c Skul version"
}

# Define node properties to map material properties to shader nodes
nodeProperty = {
    "Skin Color": "SkinColor",
    "Lip Color": "LipColor",
    "Lip Color Strength": "LipStick",
    "Eye Color": "LeftIrisColor",
    "Second Eye Color": "RightIrisColor",
    "Hair Color": "MainColor",
    "Highlights Color": "MeshColor",
    "Enable Highlights": "Highlights",
    "Limbal Color": "OptionColor"
}

class AutoMatFixOperator(bpy.types.Operator):
    """Automatically fix materials for selected objects after appending shaders"""
    bl_idname = "material.material_fixer_auto"
    bl_label = "Material Fix Auto"
    
    def execute(self, context):
        # Ensure shaders are appended before fixing materials
        bpy.ops.mektools.append_shaders()

        for obj in bpy.context.selected_objects:
            if obj.data is not None and hasattr(obj.data, 'materials'):
                for mat in obj.data.materials:
                    material_name = mat.name
                    shader = 'empty'
                    
                    # Determine shader type based on material name
                    for key in shaderType.keys():
                        if key in material_name:
                            shader = shaderType.get(key)
                        
                    # Apply the shader fix if a matching shader is found
                    if shader != 'empty':
                        materialFixer(material_name, shader)
        return {'FINISHED'}


def materialFixer(mat, group):
    material = bpy.data.materials[mat].node_tree
    properties = bpy.data.materials[mat]

    # Remove all nodes except textures to simplify construction
    for node in material.nodes:
        if node.type != "TEX_IMAGE":
            material.nodes.remove(node)
        
    # Set Normal Map and Mask Textures to Non-Color
    for node in material.nodes:
        if node.label == 'NORMAL MAP' or node.label == 'SPECULAR':
            node.image.colorspace_settings.name = 'Non-Color'

    # Add Material Output
    output = material.nodes.new('ShaderNodeOutputMaterial')
    output.location = (500, 300)

    # Add appropriate shader node group
    if group in bpy.data.node_groups:
        groupNode = material.nodes.new('ShaderNodeGroup')
        groupNode.node_tree = bpy.data.node_groups[group]
        groupNode.location = (10, 300)
        groupNode.width = 300
        material.links.new(groupNode.outputs[0], output.inputs['Surface'])

        # Configure the shader node group with custom properties
        for setting in groupNode.inputs:
            if setting.name in nodeProperty.keys():
                groupNode.inputs[setting.name].default_value = getProperty(setting, properties)

    # Connect Image Texture Nodes
    for node in material.nodes:
        if node.label == "BASE COLOR":
            if 'Diffuse Texture' in groupNode.inputs:
                material.links.new(node.outputs['Color'], groupNode.inputs['Diffuse Texture'])
            if 'Diffuse Alpha' in groupNode.inputs:
                material.links.new(node.outputs['Alpha'], groupNode.inputs['Diffuse Alpha'])
        if node.label == "NORMAL MAP":
            if 'Normal Texture' in groupNode.inputs:
                material.links.new(node.outputs['Color'], groupNode.inputs['Normal Texture'])
            if 'Normal Alpha' in groupNode.inputs:
                material.links.new(node.outputs['Alpha'], groupNode.inputs['Normal Alpha'])
        if node.label == "SPECULAR":
            if 'Mask Texture' in groupNode.inputs:
                material.links.new(node.outputs['Color'], groupNode.inputs['Mask Texture'])
            if 'Mask Alpha' in groupNode.inputs:
                material.links.new(node.outputs['Alpha'], groupNode.inputs['Mask Alpha'])


# Function to get property values with support for RGBA and single values
def getProperty(propertyName, properties):
    prop = []
    if propertyName.type == "RGBA":
        if propertyName.name == "Limbal Color":
            for value in properties[nodeProperty.get(propertyName.name)].to_dict().values():
                prop.append(value)
        else:
            for value in properties[nodeProperty.get(propertyName.name)].to_list():
                prop.append(value)
        # Ensure RGBA values have an alpha channel
        if len(prop) == 3:
            prop.append(1)

    if propertyName.type == "VALUE":
        prop = float(properties[nodeProperty.get(propertyName.name)])
    return prop


classes = [
    AutoMatFixOperator
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
