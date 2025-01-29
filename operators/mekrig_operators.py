import bpy
from bpy.types import Operator
import os

# Define the path to the assets folder relative to this file
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "../assets")

class MEKTOOLS_OT_ImportMekrigBase(Operator):
    """Base class for importing Mekrig collections"""
    bl_options = {'REGISTER', 'UNDO'}

    collection_name: str
    file_name: str

    def execute(self, context):
        # Construct the file path
        file_path = os.path.join(ASSETS_PATH, self.file_name)

        # Check if the .blend file exists
        if not os.path.exists(file_path):
            self.report({'ERROR'}, f"File not found: {file_path}")
            return {'CANCELLED'}

        # Load and append the specified collection from the .blend file
        with bpy.data.libraries.load(file_path, link=False) as (data_from, data_to):
            if self.collection_name in data_from.collections:
                data_to.collections = [self.collection_name]
            else:
                self.report({'WARNING'}, f"Collection '{self.collection_name}' not found in {file_path}")
                return {'CANCELLED'}

        # Link the collection to the current scene
        for collection in data_to.collections:
            bpy.context.scene.collection.children.link(collection)

        self.report({'INFO'}, f"Successfully imported {self.collection_name}")
        bpy.ops.ed.undo_push()
        return {'FINISHED'}


# Male Rig Operators
class MEKTOOLS_OT_ImportMekrigMidlanderMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_midlander_male"
    bl_label = "Import Midlander Male Rig"
    collection_name = "Midlander Male"
    file_name = "Midlander Male.blend"

class MEKTOOLS_OT_ImportMekrigHighlanderMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_highlander_male"
    bl_label = "Import Highlander Male Rig"
    collection_name = "Highlander Male"
    file_name = "Highlander Male.blend"

class MEKTOOLS_OT_ImportMekrigElezenMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_elezen_male"
    bl_label = "Import Elezen Male Rig"
    collection_name = "Elezen Male"
    file_name = "Elezen Male.blend"

class MEKTOOLS_OT_ImportMekrigMiqoteMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_miqote_male"
    bl_label = "Import Miqote Male Rig"
    collection_name = "Miqote Male"
    file_name = "Miqote Male.blend"

class MEKTOOLS_OT_ImportMekrigRoegadynMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_roegadyn_male"
    bl_label = "Import Roegadyn Male Rig"
    collection_name = "Roegadyn Male"
    file_name = "Roegadyn Male.blend"

class MEKTOOLS_OT_ImportMekrigAuraMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_aura_male"
    bl_label = "Import Aura Male Rig"
    collection_name = "Aura Male"
    file_name = "Aura Male.blend"

class MEKTOOLS_OT_ImportMekrigHrothgarMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_hrothgar_male"
    bl_label = "Import Hrothgar Male Rig"
    collection_name = "Hrothgar Male"
    file_name = "Hrothgar Male.blend"

class MEKTOOLS_OT_ImportMekrigVieraMale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_viera_male"
    bl_label = "Import Viera Male Rig"
    collection_name = "Viera Male"
    file_name = "Viera Male.blend"

# Lalafell Rig Operators (both male and female point to the same file and collection)
class MEKTOOLS_OT_ImportMekrigLalafellBoth(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_lalafell_both"
    bl_label = "Import Lalafell Rig"
    collection_name = "Lalafell"
    file_name = "Lalafell.blend"

# Female Rig Operators
class MEKTOOLS_OT_ImportMekrigMidlanderFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_midlander_female"
    bl_label = "Import Midlander Female Rig"
    collection_name = "Midlander Female"
    file_name = "Midlander Female.blend"

class MEKTOOLS_OT_ImportMekrigHighlanderFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_highlander_female"
    bl_label = "Import Highlander Female Rig"
    collection_name = "Highlander Female"
    file_name = "Highlander Female.blend"

class MEKTOOLS_OT_ImportMekrigElezenFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_elezen_female"
    bl_label = "Import Elezen Female Rig"
    collection_name = "Elezen Female"
    file_name = "Elezen Female.blend"

class MEKTOOLS_OT_ImportMekrigMiqoteFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_miqote_female"
    bl_label = "Import Miqote Female Rig"
    collection_name = "Miqote Female"
    file_name = "Miqote Female.blend"

class MEKTOOLS_OT_ImportMekrigRoegadynFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_roegadyn_female"
    bl_label = "Import Roegadyn Female Rig"
    collection_name = "Roegadyn Female"
    file_name = "Roegadyn Female.blend"

class MEKTOOLS_OT_ImportMekrigAuraFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_aura_female"
    bl_label = "Import Aura Female Rig"
    collection_name = "Aura Female"
    file_name = "Aura Female.blend"

class MEKTOOLS_OT_ImportMekrigVieraFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_viera_female"
    bl_label = "Import Viera Female Rig"
    collection_name = "Viera Female"
    file_name = "Viera Female.blend"

class MEKTOOLS_OT_ImportMekrigHrothgarFemale(MEKTOOLS_OT_ImportMekrigBase):
    bl_idname = "mektools.import_mekrig_hrothgar_female"
    bl_label = "Import Hrothgar Female Rig"
    collection_name = "Hrothgar Female"
    file_name = "Hrothgar Female.blend"

# Register and unregister functions
def register():
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigLalafellBoth)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigMidlanderMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigHighlanderMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigElezenMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigMiqoteMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigRoegadynMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigAuraMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigHrothgarMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigVieraMale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigMidlanderFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigHighlanderFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigElezenFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigMiqoteFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigRoegadynFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigAuraFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigVieraFemale)
    bpy.utils.register_class(MEKTOOLS_OT_ImportMekrigHrothgarFemale)

def unregister():
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigLalafellBoth)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigMidlanderMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigHighlanderMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigElezenMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigMiqoteMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigRoegadynMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigAuraMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigHrothgarMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigVieraMale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigMidlanderFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigHighlanderFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigElezenFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigMiqoteFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigRoegadynFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigAuraFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigVieraFemale)
    bpy.utils.unregister_class(MEKTOOLS_OT_ImportMekrigHrothgarFemale)
