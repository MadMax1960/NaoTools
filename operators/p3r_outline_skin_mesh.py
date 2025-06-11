import bpy

class P3ROutlineSkinMeshOperator(bpy.types.Operator):
    bl_idname = "wm.p3r_outline_skin_mesh_operator"
    bl_label = "P3R Outline Skin"
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
            bpy.ops.mesh.remove_doubles(threshold=0.001)
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')
            duplicated_object.data.materials.clear()
            material = bpy.data.materials.get("MI_CH_OlMk")
            if material:
                duplicated_object.data.materials.append(material)
            else:
                self.report({'WARNING'}, "Material 'MI_CH_OlMk' not found. Please ensure it exists in the current blend file.")
            if duplicated_object.data.vertex_colors:
                while len(duplicated_object.data.vertex_colors) > 0:
                    bpy.context.object.data.vertex_colors.remove(duplicated_object.data.vertex_colors[0])
            new_vertex_color_layer = duplicated_object.data.vertex_colors.new(name="PSKVTXCOL_0")
            # Set the color to full white
            color = (1.0, 1.0, 1.0, 1.0)
            for poly in duplicated_object.data.polygons:
                for idx in poly.loop_indices:
                    new_vertex_color_layer.data[idx].color = color
            return {'FINISHED'}
