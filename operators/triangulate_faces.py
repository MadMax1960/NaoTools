import bpy

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
