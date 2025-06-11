import bpy

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
