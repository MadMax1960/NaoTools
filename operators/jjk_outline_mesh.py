import bpy

class JJKOutlineMeshOperator(bpy.types.Operator):
    bl_idname = "wm.jjk_outline_mesh_operator"
    bl_label = "JJK Outline Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_object = bpy.context.active_object
        if selected_object is None or selected_object.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object.")
            return {'CANCELLED'}
        else:
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})
            duplicated_object = bpy.context.active_object
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')
            duplicated_object.data.materials.clear()
            material = bpy.data.materials.get("MI_CP_060_00_Outline")
            if material:
                duplicated_object.data.materials.append(material)
            else:
                self.report({'WARNING'}, "Material 'MI_CP_060_00_Outline' not found. Please ensure it exists in the current blend file.")
            if duplicated_object.data.vertex_colors:
                while len(duplicated_object.data.vertex_colors) > 0:
                    bpy.context.object.data.vertex_colors.remove(duplicated_object.data.vertex_colors[0])
            new_vertex_color_layer = duplicated_object.data.vertex_colors.new(name="JJKVTXCOL_0")
            color = (0xFF / 0xFF, 0x01 / 0xFF, 0xFF / 0xFF, 1)
            for poly in duplicated_object.data.polygons:
                for idx in poly.loop_indices:
                    new_vertex_color_layer.data[idx].color = color
            return {'FINISHED'}
