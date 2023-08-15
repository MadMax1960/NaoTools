import bpy

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

class NaoLimitWeightsOperator(bpy.types.Operator):
    bl_idname = "wm.nao_limit_weights_operator"
    bl_label = "Limit Weights"

    def execute(self, context):
        max_vertex_groups = context.scene.nao_props.max_vertex_groups
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj.vertex_groups:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)  # Select the object
                bpy.ops.object.vertex_group_limit_total(limit=max_vertex_groups)
                bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
        return {'FINISHED'}

class NaoNormalizeOperator(bpy.types.Operator):
    bl_idname = "wm.nao_normalize_operator"
    bl_label = "Normalize Weights"

    def execute(self, context):
        for obj in bpy.context.visible_objects:
            if obj.type == 'MESH' and obj.vertex_groups:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.vertex_group_normalize_all()
        return {'FINISHED'}

class NaoRenameUVOperator(bpy.types.Operator):
    bl_idname = "wm.nao_rename_uv_operator"
    bl_label = "Rename UV Maps"

    uv_map_name: bpy.props.StringProperty(name="UV Name", default="UV0")

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for uv_map in obj.data.uv_layers:
                    uv_map.name = context.scene.nao_custom_uv_name
        return {'FINISHED'}

class NaoSplitByMaterialOperator(bpy.types.Operator):
    bl_idname = "wm.nao_split_by_material_operator"
    bl_label = "Split by Materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' and obj.data.materials:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='MATERIAL')
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class NaoTriangulateOperator(bpy.types.Operator):
    bl_idname = "wm.nao_triangulate_operator"
    bl_label = "Triangulate Faces"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.quads_convert_to_tris()
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class NaoPanel(bpy.types.Panel):
    bl_idname = "PT_Nao_Panel"
    bl_label = "NaoTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'NaoTools'

    def draw(self, context):
        layout = self.layout

        # Display an image at the top
        layout.label(text="NaoTools", icon='PLUGIN')

        # All Meshes category
        layout.label(text="All Meshes:")
        layout.operator("wm.nao_limit_weights_operator")
        layout.prop(context.scene.nao_props, "max_vertex_groups")
        layout.operator("wm.nao_normalize_operator")
        layout.operator("wm.nao_rename_uv_operator")
        
        layout.prop(context.scene, "nao_custom_uv_name")
        row = layout.row(align=True)
        row.label(text="Custom UV Naming Guide:")
        row.label(text="", icon="INFO")
        layout.label(text="P5R: UV0")
        layout.label(text="P4D: UV1")
        layout.label(text="Smush: map1")
        
        # Selected Mesh category
        layout.separator()
        layout.label(text="Selected Mesh:")
        layout.operator("wm.nao_split_by_material_operator")
        layout.operator("wm.nao_triangulate_operator")

classes = (
    NaoLimitWeightsOperator,
    NaoNormalizeOperator,
    NaoRenameUVOperator,
    NaoSplitByMaterialOperator,
    NaoTriangulateOperator,
    NaoPanel,
    NaoProperties
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.nao_custom_uv_name = bpy.props.StringProperty(name="UV Name", default="UV0")
    bpy.types.Scene.nao_props = bpy.props.PointerProperty(type=NaoProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.nao_custom_uv_name
    del bpy.types.Scene.nao_props

if __name__ == "__main__":
    register()
