import bpy
from bpy.types import Panel
import addon_utils
import webbrowser




class VIEW3D_PT_ImportPanel(Panel):
    bl_label = "Import"
    bl_idname = "VIEW3D_PT_import_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'  
    bl_category = 'Mektools'

    def draw(self, context):
        layout = self.layout
        #First we check if meddle is installed
        isMeddleInstalled = False

        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Meddle Tools":  
                isMeddleInstalled = True

                break

        if isMeddleInstalled:
            layout.prop(context.scene, "import_with_meddle_shader", text="Import MeddleTools Shader (GLTF Only)")

        # Import Options
        row = layout.row(align=True)
        row.operator("mektools.import_meddle_gltf", text="GLTF from Meddle")
        row.operator("mektools.import_textools_fbx", text="FBX from TexTools")


        if isMeddleInstalled:
            # Shader Append Button
            layout.operator('append.import_shaders',  text="Import MeddleTools Shaders", icon="SHADING_TEXTURE")
            layout.operator('append.use_shaders_current', text="Apply MeddleTools Shaders To Selected Objects", icon="SHADING_TEXTURE")
        else:
            layout.label(text="MeddleTools addon not installed.")
            layout.label(text="Please install it for shader functionality.")

            layout.operator("wm.url_open", text="Get MeddleTools Addon", icon="URL").url = "https://github.com/PassiveModding/MeddleTools/releases"
        


        # Rigs Label and Popovers for Male and Female Rigs
        layout.separator()
        layout.label(text="Rigs")
        split = layout.split(factor=0.5, align=True)
        split.popover("MEKTOOLS_PT_MaleRigs", text="Male", icon_value=0)
        split.popover("MEKTOOLS_PT_FemaleRigs", text="Female", icon_value=0)

        # Fixer Buttons Section
        layout.separator()
        layout.label(text="Fixer Buttons")
        layout.operator("object.fix_backface_culling", text="Fix Backface Culling")
        layout.operator("mesh.clear_custom_split_normals", text="Clear Custom Split Normals")
        layout.operator("mektools.clear_parents", text="Clear Parents (Keep Transforms)")

class MEKTOOLS_PT_MaleRigs(Panel):
    """Male Mekrigs Import"""
    bl_label = "Male Mekrigs"
    bl_idname = "MEKTOOLS_PT_MaleRigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'HIDE_HEADER', 'DEFAULT_CLOSED'}

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
    bl_region_type = 'WINDOW'
    bl_options = {'HIDE_HEADER', 'DEFAULT_CLOSED'}

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
