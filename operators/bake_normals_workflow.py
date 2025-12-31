import bpy

class NaoBakeNormalsWorkflowOperator(bpy.types.Operator):
    bl_idname = "wm.nao_bake_normals_workflow_operator"
    bl_label = "Transfer Normals (Bake)"
    bl_description = "Click 2 meshes, the first will have it's normals converted to a texture, the second will be baking that to the normals. This is NOT a normal map, its taking actual normals from a model. Assuming the uvs are 1:1, the normals should roughly be 1:1."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 1. Validation
        selected = context.selected_objects
        active = context.active_object
        
        if len(selected) != 2:
            self.report({'ERROR'}, "Please select exactly 2 meshes.")
            return {'CANCELLED'}
        
        if not active or active not in selected:
            self.report({'ERROR'}, "One object must be Active.")
            return {'CANCELLED'}
            
        target_mesh = active
        source_mesh = [obj for obj in selected if obj != active][0]
        
        if target_mesh.type != 'MESH' or source_mesh.type != 'MESH':
            self.report({'ERROR'}, "Both objects must be Meshes.")
            return {'CANCELLED'}

        # 2. Stash Settings
        scene = context.scene
        stashed_settings = {}
        stashed_materials = {}
        
        try:
            stashed_settings['engine'] = scene.render.engine
            stashed_settings['samples'] = scene.cycles.samples
            stashed_settings['preview_samples'] = scene.cycles.preview_samples
            stashed_settings['adaptive'] = scene.cycles.use_adaptive_sampling
            stashed_settings['denoise'] = scene.cycles.use_denoising
            
            stashed_settings['bake_type'] = scene.cycles.bake_type
            stashed_settings['bake_target'] = scene.render.bake.target
            stashed_settings['bake_margin'] = scene.render.bake.margin
            
            stashed_materials[source_mesh.name] = source_mesh.data.materials[0] if source_mesh.data.materials else None
            stashed_materials[target_mesh.name] = target_mesh.data.materials[0] if target_mesh.data.materials else None
        except Exception:
            pass 

        # 3. Apply Low Specs
        scene.render.engine = 'CYCLES'
        scene.cycles.use_preview_adaptive_sampling = False
        scene.cycles.preview_samples = 1
        scene.cycles.use_preview_denoising = False
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.samples = 1
        scene.cycles.use_denoising = False

        # 4. Process Mesh 1 (Source) -> Bake Map Range
        bpy.ops.object.select_all(action='DESELECT')
        source_mesh.select_set(True)
        context.view_layer.objects.active = source_mesh
        
        img_name = f"Bake_Result_MapRange_{source_mesh.name}"
        if img_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[img_name])
        bake_image = bpy.data.images.new(img_name, width=2048, height=2048)

        mat = bpy.data.materials.new(name="TEMP_SOURCE_MAT")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        geo_node = nodes.new('ShaderNodeNewGeometry')
        map_node = nodes.new('ShaderNodeMapRange')
        map_node.data_type = 'FLOAT_VECTOR'
        map_node.inputs['From Min'].default_value = (-1.0, -1.0, -1.0)
        out_node = nodes.new('ShaderNodeOutputMaterial')
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = bake_image
        tex_node.select = True 
        nodes.active = tex_node

        links.new(geo_node.outputs['Normal'], map_node.inputs['Vector'])
        links.new(map_node.outputs['Vector'], out_node.inputs['Surface'])
        
        source_mesh.data.materials.clear()
        source_mesh.data.materials.append(mat)

        scene.cycles.bake_type = 'COMBINED'
        scene.render.bake.target = 'IMAGE_TEXTURES'
        scene.render.bake.use_selected_to_active = False
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.margin = 16

        bpy.ops.object.bake(type='COMBINED')
        
        if len(bake_image.pixels) > 0:
            bake_image.pixels[0] = bake_image.pixels[0]

        # 5. Process Mesh 2 (Target) -> Bake to Vertex Colors
        bpy.ops.object.select_all(action='DESELECT')
        target_mesh.select_set(True)
        context.view_layer.objects.active = target_mesh
        
        if hasattr(context.view_layer, "depsgraph"):
             context.view_layer.depsgraph.update()

        # --- MODIFICATION START: Temporary Layer Logic ---
        # Remember original active layer index to restore later
        original_active_index = 0
        if target_mesh.data.color_attributes:
            original_active_index = target_mesh.data.color_attributes.active_color_index

        # Define temporary layer name
        temp_layer_name = "Nao_Temp_Bake"

        # Ensure we don't crash if it already exists from a previous failed run
        if temp_layer_name in target_mesh.data.color_attributes:
            target_mesh.data.color_attributes.remove(target_mesh.data.color_attributes[temp_layer_name])

        # Create new temporary layer
        target_mesh.data.color_attributes.new(name=temp_layer_name, type='BYTE_COLOR', domain='CORNER')

        # Set the new temporary layer as active
        for i, layer in enumerate(target_mesh.data.color_attributes):
            if layer.name == temp_layer_name:
                target_mesh.data.color_attributes.active_color_index = i
                break
        # --- MODIFICATION END ---

        mat_target = bpy.data.materials.new(name="TEMP_TARGET_MAT")
        mat_target.use_nodes = True
        nodes_t = mat_target.node_tree.nodes
        links_t = mat_target.node_tree.links
        nodes_t.clear()

        tex_node_t = nodes_t.new('ShaderNodeTexImage')
        tex_node_t.image = bake_image
        tex_node_t.extension = 'EXTEND'
        tex_node_t.interpolation = 'Linear'
        emit_node = nodes_t.new('ShaderNodeEmission')
        out_node_t = nodes_t.new('ShaderNodeOutputMaterial')

        links_t.new(tex_node_t.outputs['Color'], emit_node.inputs['Color'])
        links_t.new(emit_node.outputs['Emission'], out_node_t.inputs['Surface'])
        
        target_mesh.data.materials.clear()
        target_mesh.data.materials.append(mat_target)
        
        scene.cycles.bake_type = 'EMIT' 
        scene.render.bake.target = 'VERTEX_COLORS'
        scene.render.bake.use_selected_to_active = False

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.object.bake(type='EMIT')

        # 6. Restoration
        source_mesh.data.materials.clear()
        if stashed_materials.get(source_mesh.name):
            source_mesh.data.materials.append(stashed_materials[source_mesh.name])

        target_mesh.data.materials.clear()
        if stashed_materials.get(target_mesh.name):
            target_mesh.data.materials.append(stashed_materials[target_mesh.name])

        try:
            scene.render.engine = stashed_settings.get('engine', 'CYCLES')
            scene.cycles.samples = stashed_settings.get('samples', 128)
            scene.cycles.bake_type = stashed_settings.get('bake_type', 'COMBINED')
            scene.render.bake.target = stashed_settings.get('bake_target', 'IMAGE_TEXTURES')
        except Exception:
            pass

        # 7. Final Step: Convert Vertex Colors to Normals (Logic Chain)
        # Ensure target is active
        context.view_layer.objects.active = target_mesh
        bpy.ops.wm.nao_vertex_colors_to_normals_operator()

        # --- MODIFICATION START: Cleanup ---
        # Remove the temporary layer
        if temp_layer_name in target_mesh.data.color_attributes:
            target_mesh.data.color_attributes.remove(target_mesh.data.color_attributes[temp_layer_name])

        # Restore the original active layer if it is still valid
        if target_mesh.data.color_attributes and original_active_index < len(target_mesh.data.color_attributes):
            target_mesh.data.color_attributes.active_color_index = original_active_index
        # --- MODIFICATION END ---

        self.report({'INFO'}, "Normal Transfer & Conversion Complete.")
        return {'FINISHED'}
