import bpy
import mathutils

# courtesy of Dniwe

class NaoVertexColorsToNormalsOperator(bpy.types.Operator):
    bl_idname = "wm.nao_vertex_colors_to_normals_operator"
    bl_label = "Vertex Colors to Normals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the active object
        obj = context.active_object

        # Ensure it's a mesh
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        # Get the active vertex color layer
        if not obj.data.vertex_colors:
             self.report({'WARNING'}, "No active vertex color layer")
             return {'CANCELLED'}

        color_layer = obj.data.vertex_colors.active

        if color_layer is None:
            self.report({'WARNING'}, "No active vertex color layer")
            return {'CANCELLED'}
        
        # Create a list to store the new normals
        new_normals = []

        # Iterate over the polygons (i.e., faces)
        for poly in obj.data.polygons:
            # Iterate over the loop indices of the polygon
            for loop_index in poly.loop_indices:
                # Get the color of the current vertex
                color = color_layer.data[loop_index].color

                # Apply gamma correction
                corrected_color = [pow(c, 2.2) for c in color]

                # Convert the color to a direction vector
                # (R * 2 - 1, G * 2 - 1, B * 2 - 1)
                normal = mathutils.Vector((
                    corrected_color[0] * 2 - 1, 
                    corrected_color[1] * 2 - 1, 
                    corrected_color[2] * 2 - 1
                ))

                # Normalize the vector
                normal.normalize()

                # Add the normal to the list
                new_normals.append(normal)

        # Set the new normals
        obj.data.normals_split_custom_set(new_normals)
        
        self.report({'INFO'}, "Successfully converted Vertex Colors to Normals.")
        return {'FINISHED'}