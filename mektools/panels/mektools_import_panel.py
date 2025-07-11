import bpy
from bpy.types import Panel
import addon_utils
import webbrowser
from ..addon_preferences import get_addon_preferences 

class VIEW3D_PT_ImportPanel(Panel):
    bl_label = "Import"
    bl_idname = "VIEW3D_PT_import_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'  
    bl_category = 'Mektools'

    def draw(self, context):
        prefs = get_addon_preferences()
        layout = self.layout
        #First we check if meddle is installed
        isMeddleInstalled = False

        # We go through each addon and see if we find a 'Meddle Tools' addon
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Meddle Tools":  
                isMeddleInstalled = True

                break
        has_operators = False
 
        # Ideally, using a try/catch block for the logic of your code is not the best practice
        # try/catch blocks are for handling exceptions, not for controlling the flow of your code
        # but i had no fucking clue how to do it otherwise, so it stays.
        try:
            # We check if the operators are available
            # If someone just installed the addon (without restarting blender)
            # these will error out, so we need to catch that
            # once someone restarts blender these go through no problemo
            bpy.ops.meddle.import_shaders.poll()
            bpy.ops.meddle.use_shaders_selected_objects.poll()

            #we set the operators as true to display all the buttons and shenanigans
            has_operators = True
            #print(f"Both MeddleTools operators found")

        except (AttributeError, RuntimeError):
            print(f"MeddleTools operators not found")
            has_operators = False
        # Import Buttons Section
        # We check if meddle is instaslled AND its initialized properly (after a restart)
        if isMeddleInstalled and has_operators:

            row = layout.row(align=True)
            row.operator("mektools.import_meddle_gltf", text="Character Import", icon = "IMPORT") #should only show if meddle is installed Subject for later refactor 
            
            row = layout.row(align=True) # these should only show if meddle is installed 

        # We need to split the logic here since we want different things to happen wether meddle is installed or not
        # and if the operators are available or not
        if isMeddleInstalled:
            # If the operators are available and meddle is installed that means that the initial restart setup is done, and its all g
            if has_operators:
                if prefs.legacy_button_import_shaders == 'ON':
                    layout.operator('meddle.import_shaders', text="Import Shaders", icon="SHADING_TEXTURE")
                if prefs.legacy_button_apply_shaders == 'ON':
                    layout.operator('meddle.use_shaders_selected_objects', text="Apply Shaders", icon="SHADING_TEXTURE")

            # If meddle is installed, but the operators are not available, that means that the user just installed the addon
            # And user needs to restart blender
            else:
                column = layout.column(align=True)
                column.alert = True
                column.label(text="!!!!!!!!!!!!!!!!!!!!!!!!!")
                column.label(text="Ooop, not quite finished yet.")
                column.label(text="Almost there though.")
                column.label(text="Go give Blender a good ol' restart,")
                column.label(text="If that doesn't work make sure MeddleTools addon is enabled.")
                column.label(text="!!!!!!!!!!!!!!!!!!!!!!!!!")

        # If MeddleTools is not installed, we show a message to the user to install it
        else:
            column = layout.column(align=True)
            column.alert = True
            column.label(text="!!!!!!!!!!!!!!!!!!!!!!!!!")
            column.label(text="MeddleTools addon not installed.")
            column.label(text="Please install it for import functionality.")
            column.label(text="!!!!!!!!!!!!!!!!!!!!!!!!!")

            layout.operator("wm.url_open", text="Get MeddleTools Addon", icon="URL").url = "https://github.com/PassiveModding/MeddleTools/releases"
        

        if prefs.legacy_button_import_rigs == 'ON':
            # Rigs Label and Popovers for Male and Female Rigs
            layout.separator()
            layout.label(text="Rigs")
            split = layout.split(factor=0.5, align=True)
            split.popover("MEKTOOLS_PT_MaleRigs", text="Male", icon_value=0)
            split.popover("MEKTOOLS_PT_FemaleRigs", text="Female", icon_value=0)    

        # Fixer Buttons Section
        if (
            prefs.legacy_button_fix_backface_culling == 'ON' or 
            prefs.legacy_button_clear_custom_split_normals == 'ON' or 
            prefs.legacy_button_clear_parents_keep_transform == 'ON'
        ):
            layout.separator()
            layout.label(text="Fixer Buttons")
        
        if prefs.legacy_button_fix_backface_culling == 'ON':
            layout.operator("object.fix_backface_culling", text="Fix Backface Culling")   
        if prefs.legacy_button_clear_custom_split_normals == 'ON':
            layout.operator("mesh.clear_custom_split_normals", text="Clear Custom Split Normals")
        if prefs.legacy_button_clear_parents_keep_transform == 'ON':
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
