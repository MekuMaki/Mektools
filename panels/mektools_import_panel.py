import bpy
from bpy.types import Panel

class VIEW3D_PT_ImportPanel(Panel):
    bl_label = "Import"
    bl_idname = "VIEW3D_PT_import_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mektools'

    def draw(self, context):
        layout = self.layout

        # Import Options
        row = layout.row(align=True)
        row.operator("mektools.import_meddle_gltf", text="GLTF from Meddle")
        row.operator("mektools.import_textools_fbx", text="FBX from TexTools")

        # Shader Append Button
        layout.operator("mektools.append_shaders", text="Append Shaders", icon="SHADING_TEXTURE")

        # Rigs Label and Popovers for Male and Female Rigs
        layout.separator()
        layout.label(text="Rigs")
        split = layout.split(factor=0.5, align=True)
        split.popover("MEKTOOLS_PT_MaleRigs", text="Male", icon_value=0)
        split.popover("MEKTOOLS_PT_FemaleRigs", text="Female", icon_value=0)


class MEKTOOLS_PT_MaleRigs(Panel):
    """Male Mekrigs Import"""
    bl_label = "Male Mekrigs"
    bl_idname = "MEKTOOLS_PT_MaleRigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_import_panel"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.operator("mektools.import_mekrig_midlander_male", text="Midlander Male")
        layout.operator("mektools.import_mekrig_highlander_male", text="Highlander Male")
        layout.operator("mektools.import_mekrig_elezen_male", text="Elezen Male")
        layout.operator("mektools.import_mekrig_miqote_male", text="Miqote Male")
        layout.operator("mektools.import_mekrig_roegadyn_male", text="Roegadyn Male")
        layout.operator("mektools.import_mekrig_lalafell_both", text="Lalafell Male")
        layout.operator("mektools.import_mekrig_aura_male", text="Aura Male")
        layout.operator("mektools.import_mekrig_hrothgar_male", text="Hrothgar Male")
        layout.operator("mektools.import_mekrig_viera_male", text="Viera Male")


class MEKTOOLS_PT_FemaleRigs(Panel):
    """Female Mekrigs Import"""
    bl_label = "Female Mekrigs"
    bl_idname = "MEKTOOLS_PT_FemaleRigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_import_panel"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.operator("mektools.import_mekrig_midlander_female", text="Midlander Female")
        layout.operator("mektools.import_mekrig_highlander_female", text="Highlander Female")
        layout.operator("mektools.import_mekrig_elezen_female", text="Elezen Female")
        layout.operator("mektools.import_mekrig_miqote_female", text="Miqote Female")
        layout.operator("mektools.import_mekrig_roegadyn_female", text="Roegadyn Female")
        layout.operator("mektools.import_mekrig_lalafell_both", text="Lalafell Female")
        layout.operator("mektools.import_mekrig_aura_female", text="Aura Female")
        layout.operator("mektools.import_mekrig_hrothgar_female", text="Hrothgar Female")
        layout.operator("mektools.import_mekrig_viera_female", text="Viera Female")


def register():
    bpy.utils.register_class(VIEW3D_PT_ImportPanel)
    bpy.utils.register_class(MEKTOOLS_PT_MaleRigs)
    bpy.utils.register_class(MEKTOOLS_PT_FemaleRigs)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_ImportPanel)
    bpy.utils.unregister_class(MEKTOOLS_PT_MaleRigs)
    bpy.utils.unregister_class(MEKTOOLS_PT_FemaleRigs)
