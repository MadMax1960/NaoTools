import bpy
import time

class NaoBakeNormalsWorkflowOperator(bpy.types.Operator):
    bl_idname = "wm.nao_bake_normals_workflow_operator"
    bl_label = "Transfer Normals (Bake)"
    bl_description = "Click 2 meshes, the first will have it's normals converted to a texture, the second will be baking that to the normals. This is NOT a normal map, its taking actual normals from a model. Assuming the uvs are 1:1, the normals should roughly be 1:1."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Starting NaoBakeNormalsWorkflowOperator")

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

        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Source: {source_mesh.name}, Target: {target_mesh.name}")

        # 2. Stash Settings & Materials
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
            
            # FIXED: Stash from material_slots to preserve 'None' slots and exact order
            stashed_materials[source_mesh.name] = [s.material for s in source_mesh.material_slots]
            stashed_materials[target_mesh.name] = [s.material for s in target_mesh.material_slots]
            
            print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Stashed {len(stashed_materials[source_mesh.name])} slots for Source")
            print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Stashed {len(stashed_materials[target_mesh.name])} slots for Target")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Error during stash: {e}")
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
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Setting up Source Mesh...")
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
        
        # Apply temp mat to all slots
        if not source_mesh.material_slots:
            source_mesh.data.materials.append(mat)
        else:
            for i in range(len(source_mesh.material_slots)):
                source_mesh.material_slots[i].material = mat

        scene.cycles.bake_type = 'COMBINED'
        scene.render.bake.target = 'IMAGE_TEXTURES'
        scene.render.bake.use_selected_to_active = False
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.margin = 16

        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Baking Map Range...")
        bpy.ops.object.bake(type='COMBINED')
        
        if len(bake_image.pixels) > 0:
            bake_image.pixels[0] = bake_image.pixels[0]

        # 5. Process Mesh 2 (Target) -> Bake to Vertex Colors
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Setting up Target Mesh...")
        bpy.ops.object.select_all(action='DESELECT')
        target_mesh.select_set(True)
        context.view_layer.objects.active = target_mesh
        
        # Temporary Layer Logic
        temp_layer_name = "Nao_Temp_Bake"
        if temp_layer_name in target_mesh.data.color_attributes:
            target_mesh.data.color_attributes.remove(target_mesh.data.color_attributes[temp_layer_name])

        target_mesh.data.color_attributes.new(name=temp_layer_name, type='BYTE_COLOR', domain='CORNER')
        for i, layer in enumerate(target_mesh.data.color_attributes):
            if layer.name == temp_layer_name:
                target_mesh.data.color_attributes.active_color_index = i
                break

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
        
        # Apply temp mat to all slots
        if not target_mesh.material_slots:
            target_mesh.data.materials.append(mat_target)
        else:
            for i in range(len(target_mesh.material_slots)):
                target_mesh.material_slots[i].material = mat_target
        
        scene.cycles.bake_type = 'EMIT' 
        scene.render.bake.target = 'VERTEX_COLORS'
        scene.render.bake.use_selected_to_active = False

        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Baking Vertex Colors...")
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.object.bake(type='EMIT')

        # 6. Restoration
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Restoring materials...")
        
        def restore_materials_safely(mesh, original_mats):
            if not original_mats:
                print(f"[{time.strftime('%H:%M:%S')}] DEBUG: No original materials to restore for {mesh.name}. Clearing.")
                mesh.data.materials.clear()
                return

            print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Restoring {len(original_mats)} slots for {mesh.name}")
            
            current_slots = len(mesh.material_slots)
            
            # If mismatch, fallback to clear + append (safe but loses faces)
            if current_slots != len(original_mats):
                 print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Slot count mismatch (Mesh: {current_slots}, Orig: {len(original_mats)}). Resetting.")
                 mesh.data.materials.clear()
                 for m in original_mats:
                     if m:
                         mesh.data.materials.append(m)
                     else:
                         # Append dummy to maintain slot count? Or just append None (not supported directly)?
                         # We'll just add a new slot
                         bpy.ops.object.material_slot_add()
            else:
                # Optimized path: Swap back safely
                for i, m in enumerate(original_mats):
                    print(f"[{time.strftime('%H:%M:%S')}] DEBUG:   -> Restoring Slot {i}...")
                    try:
                        mesh.material_slots[i].material = m
                        print(f"[{time.strftime('%H:%M:%S')}] DEBUG:   -> Slot {i} Done.")
                    except Exception as loop_e:
                        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Error assigning slot {i}: {loop_e}")

        # Restore
        restore_materials_safely(source_mesh, stashed_materials.get(source_mesh.name, []))
        restore_materials_safely(target_mesh, stashed_materials.get(target_mesh.name, []))

        # Restore settings
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Restoring Render Settings...")
        try:
            scene.render.engine = stashed_settings.get('engine', 'CYCLES')
            scene.cycles.samples = stashed_settings.get('samples', 128)
            scene.cycles.bake_type = stashed_settings.get('bake_type', 'COMBINED')
            scene.render.bake.target = stashed_settings.get('bake_target', 'IMAGE_TEXTURES')
        except Exception:
            pass

        # 7. Final Step: Convert Vertex Colors to Normals
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Converting VColors to Normals...")
        context.view_layer.objects.active = target_mesh
        bpy.ops.wm.nao_vertex_colors_to_normals_operator()

        # Cleanup
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Cleanup...")
        if temp_layer_name in target_mesh.data.color_attributes:
            target_mesh.data.color_attributes.remove(target_mesh.data.color_attributes[temp_layer_name])

        self.report({'INFO'}, "Normal Transfer & Conversion Complete.")
        print(f"[{time.strftime('%H:%M:%S')}] DEBUG: Process Complete.")
        return {'FINISHED'}