import bpy
import os
import bpy.utils.previews

from .operators.limit_weights import NaoLimitWeightsOperator
from .operators.ue_psk_fix import UEPskFixOperator
from .operators.p3r_outline_mesh import P3ROutlineMeshOperator
from .operators.p3r_outline_skin_mesh import P3ROutlineSkinMeshOperator
from .operators.jjk_outline_mesh import JJKOutlineMeshOperator
from .operators.normalize_weights import NaoNormalizeOperator
from .operators.rename_uv import NaoRenameUVOperator
from .operators.split_by_material import NaoSplitByMaterialOperator
from .operators.triangulate_faces import NaoTriangulateOperator
from .operators.clear_unused_weights import NaoClearUnusedWeightsOperator
from .operators.copy_mirror_pose import NaoCopyMirrorPoseOperator
from .operators.ue_material_duplicate import UEMaterialDuplicateOperator
from .operators.skeleton_printer import SkeletonPrinterOperator

bl_info = {
    "name": "NaoTools",
    "author": "Mudkip",
    "version": (2, 6),
    "blender": (2, 80, 0),
    "location": "View3D > N-panel",
    "description": "Adds NaoTools for various operations",
    "category": "Tool"
}

class NaoProperties(bpy.types.PropertyGroup):
    max_vertex_groups: bpy.props.IntProperty(
        name="Max Vertex Groups",
        default=4,
        min=1,
        max=10
    )

def register_suffixes():
    bpy.types.Scene.nao_left_suffix = bpy.props.StringProperty(
        name="Left Suffix",
        description="Suffix for left-side bones (e.g., '_L', 'Left')",
        default="L",
    )
    bpy.types.Scene.nao_right_suffix = bpy.props.StringProperty(
        name="Right Suffix",
        description="Suffix for right-side bones (e.g., '_R', 'Right')",
        default="R",
    )

def unregister_suffixes():
    del bpy.types.Scene.nao_left_suffix
    del bpy.types.Scene.nao_right_suffix


# A dictionary to hold the custom preview collection for images
preview_collections = {}

# Define the main collapsible panel with logo and text
class NaoToolsPanel(bpy.types.Panel):
    bl_label = "Nao Tools"
    bl_idname = "PT_Nao_Tools_Main_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout

        # Add description text
        layout.label(text="Tool to streamline various blender operations.")

# Convert the original panels into sub-panels of the main panel
class NaoAllMeshesPanel(bpy.types.Panel):
    bl_parent_id = "PT_Nao_Tools_Main_Panel"
    bl_label = "All Meshes"
    bl_idname = "PT_Nao_All_Meshes_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.nao_limit_weights_operator")
        layout.prop(context.scene.nao_props, "max_vertex_groups")
        layout.operator("wm.nao_normalize_operator")
        layout.operator("wm.nao_rename_uv_operator")
        layout.prop(context.scene, "nao_custom_uv_name")

        # Custom UV Naming Guide Notes
        row = layout.row(align=True)
        row.label(text="Custom UV Naming Guide:")
        row.label(text="", icon="INFO")
        layout.label(text="P5R: UV0")
        layout.label(text="P4D: UV1")
        layout.label(text="Smush: map1")

class NaoSelectedMeshPanel(bpy.types.Panel):
    bl_parent_id = "PT_Nao_Tools_Main_Panel"
    bl_label = "Selected Mesh"
    bl_idname = "PT_Nao_Selected_Mesh_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.nao_split_by_material_operator")
        layout.operator("wm.nao_triangulate_operator")
        layout.operator("wm.nao_clear_unused_weights_operator") 
        layout.operator("wm.ue_material_duplicate_operator")
        
class NaoMiscPanel(bpy.types.Panel):
    bl_parent_id = "PT_Nao_Tools_Main_Panel"
    bl_label = "Misc"
    bl_idname = "PT_Nao_Misc"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Add Outline operators
        layout.operator("wm.p3r_outline_mesh_operator")
        layout.operator("wm.p3r_outline_skin_mesh_operator")
        layout.operator("wm.jjk_outline_mesh_operator")

        # Add bone suffix settings
        layout.prop(scene, "nao_left_suffix")
        layout.prop(scene, "nao_right_suffix")

        # Add Copy & Mirror Pose button
        layout.operator(NaoCopyMirrorPoseOperator.bl_idname)
        
class NaoSelectedArmaturePanel(bpy.types.Panel):
    bl_parent_id = "PT_Nao_Tools_Main_Panel"
    bl_label = "Selected Armature"
    bl_idname = "PT_Nao_Selected_Armature_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.ue_psk_fix_operator")
        layout.operator("wm.skeleton_printer_operator")

# Function to load the logo image into preview collections
def load_logo():
    addon_directory = os.path.dirname(os.path.realpath(__file__))
    logo_path = os.path.join(addon_directory, "naotools_logo.png")

    if not os.path.exists(logo_path):
        print("Logo image not found. Please ensure 'naotools_logo.png' is in the add-on directory.")
        return

    pcoll = bpy.utils.previews.new()
    pcoll.load("naotools_logo", logo_path, 'IMAGE')
    preview_collections["naotools_preview"] = pcoll

def unload_logo():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

# Register and unregister all classes
classes = (
    NaoProperties,
    NaoLimitWeightsOperator,
    NaoNormalizeOperator,
    NaoRenameUVOperator,
    NaoSplitByMaterialOperator,
    NaoTriangulateOperator,
    P3ROutlineMeshOperator,
    P3ROutlineSkinMeshOperator,
    JJKOutlineMeshOperator,
    NaoClearUnusedWeightsOperator,
    NaoToolsPanel,
    NaoAllMeshesPanel,
    NaoSelectedMeshPanel,
    NaoMiscPanel,
    NaoSelectedArmaturePanel,
    UEPskFixOperator,
    NaoCopyMirrorPoseOperator,
    UEMaterialDuplicateOperator,
    SkeletonPrinterOperator, 
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.nao_custom_uv_name = bpy.props.StringProperty(name="UV Name", default="UV0")
    bpy.types.Scene.nao_props = bpy.props.PointerProperty(type=NaoProperties)
    register_suffixes()
    load_logo()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nao_custom_uv_name
    del bpy.types.Scene.nao_props
    unregister_suffixes()
    unload_logo()

if __name__ == "__main__":
    register()