import bpy
import os
import bpy.utils.previews

from .operators.limit_weights import NaoLimitWeightsOperator
from .operators.ue_psk_fix import UEPskFixOperator
from .operators.p3r_outline_mesh import P3ROutlineMeshOperator
from .operators.normalize_weights import NaoNormalizeOperator
from .operators.rename_uv import NaoRenameUVOperator
from .operators.split_by_material import NaoSplitByMaterialOperator
from .operators.triangulate_faces import NaoTriangulateOperator
from .operators.clear_unused_weights import NaoClearUnusedWeightsOperator
from .operators.ue_material_duplicate import UEMaterialDuplicateOperator
from .operators.skeleton_printer import SkeletonPrinterOperator
from .operators.vertex_colors_to_normals import NaoVertexColorsToNormalsOperator
from .operators.bake_normals_workflow import NaoBakeNormalsWorkflowOperator

bl_info = {
    "name": "NaoTools",
    "author": "Mudkip",
    "version": (3, 0),
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
        layout.operator("wm.p3r_outline_mesh_operator")
        
class NaoNormalBakingPanel(bpy.types.Panel):
    bl_parent_id = "PT_Nao_Tools_Main_Panel"
    bl_label = "Normal Baking Workflow"
    bl_idname = "PT_Nao_Normal_Baking_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout
        # New Script Button (Automated Workflow)
        layout.operator("wm.nao_bake_normals_workflow_operator")
        # Removed separator to fix the gap
        # Vertex Colors to Normals Button (Manual/Second step)
        layout.operator("wm.nao_vertex_colors_to_normals_operator", text="Vertex Colors to Normals")

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

classes = (
    NaoProperties,
    NaoLimitWeightsOperator,
    NaoNormalizeOperator,
    NaoRenameUVOperator,
    NaoSplitByMaterialOperator,
    NaoTriangulateOperator,
    P3ROutlineMeshOperator,
    NaoClearUnusedWeightsOperator,
    NaoToolsPanel,
    NaoAllMeshesPanel,
    NaoSelectedMeshPanel,
    NaoNormalBakingPanel,
    NaoSelectedArmaturePanel,
    UEPskFixOperator,
    UEMaterialDuplicateOperator,
    SkeletonPrinterOperator,
    NaoVertexColorsToNormalsOperator, 
    NaoBakeNormalsWorkflowOperator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.nao_custom_uv_name = bpy.props.StringProperty(name="UV Name", default="UV0")
    bpy.types.Scene.nao_props = bpy.props.PointerProperty(type=NaoProperties)
    load_logo()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nao_custom_uv_name
    del bpy.types.Scene.nao_props
    unload_logo()

if __name__ == "__main__":
    register()
