import bpy
import mathutils

def get_bounding_box_volume(obj):
    dims = obj.dimensions
    return dims.x * dims.y * dims.z

def get_bounding_box_width(obj):
    return obj.dimensions.x

def get_object_height(obj):
    """Get the actual height (Z dimension) of the object in world space."""
    # Update the object's data to ensure dimensions are current
    if obj.type == 'MESH':
        # Get bounding box in world coordinates
        bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        # Find min and max Z values
        min_z = min(v.z for v in bbox_corners)
        max_z = max(v.z for v in bbox_corners)
        return max_z - min_z
    return obj.dimensions.z

def get_object_width(obj):
    """Get the actual width (X dimension) in world space."""
    if obj.type == 'MESH':
        bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        min_x = min(v.x for v in bbox_corners)
        max_x = max(v.x for v in bbox_corners)
        return max_x - min_x
    return obj.dimensions.x

def get_object_depth(obj):
    """Get the actual depth (Y dimension) in world space."""
    if obj.type == 'MESH':
        bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        min_y = min(v.y for v in bbox_corners)
        max_y = max(v.y for v in bbox_corners)
        return max_y - min_y
    return obj.dimensions.y

class OBJECT_OT_arrange_by_volume(bpy.types.Operator):
    bl_idname = "object.arrange_by_volume"
    bl_label = "Quick Arrange"
    bl_options = {'REGISTER', 'UNDO'}
    
    padding_mode: bpy.props.EnumProperty(
        name="Padding Mode",
        description="How to calculate spacing between objects",
        items=[
            ('AUTO', "Auto", "Calculate padding based on object sizes (5% of average width)"),
            ('MANUAL', "Manual", "Use fixed padding"),
        ],
        default='AUTO'
    )
    
    padding: bpy.props.FloatProperty(
        name="Padding",
        description="Space between objects (used in Manual mode)",
        default=0.1,
        min=0.0,
        max=10.0
    )
    
    padding_percent: bpy.props.FloatProperty(
        name="Padding %",
        description="Padding as percentage of average object width (used in Auto mode)",
        default=5.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE'
    )
    
    sort_ascending: bpy.props.BoolProperty(
        name="Smallest First",
        description="Sort from smallest to largest volume",
        default=True
    )

    sort_by: bpy.props.EnumProperty(
        name="Sort By",
        description="What to sort objects by",
        items=[
            ('VOLUME', "Volume", "Sort by bounding box volume"),
            ('HEIGHT', "Height", "Sort by object height (Z)"),
            ('WIDTH', "Width", "Sort by object width (X)"),
            ('DEPTH', "Depth", "Sort by object depth (Y)"),
        ],
        default='VOLUME'
    )
    
    sort_ascending: bpy.props.BoolProperty(
        name="Smallest First",
        description="Sort from smallest to largest",
        default=True
    )

    def execute(self, context):
        selected_objects = context.selected_objects
        
        if len(selected_objects) < 2:
            self.report({'WARNING'}, "Select at least 2 objects")
            return {'CANCELLED'}
        
        # Check if objects have stored original positions
        has_stored_positions = all(
            "arrange_original_loc" in obj for obj in selected_objects
        )
        
        if has_stored_positions:
            # UNDO: Restore original positions
            for obj in selected_objects:
                if "arrange_original_loc" in obj:
                    obj.location = mathutils.Vector(obj["arrange_original_loc"])
                    del obj["arrange_original_loc"]
            
            self.report({'INFO'}, f"Restored {len(selected_objects)} objects to original positions")
            return {'FINISHED'}
        
        else:
            # Store original positions
            for obj in selected_objects:
                obj["arrange_original_loc"] = obj.location.copy()

            # Calculate sort value based on mode
            objects_with_value = []
            for obj in selected_objects:
                if self.sort_by == 'VOLUME':
                    value = get_bounding_box_volume(obj)
                elif self.sort_by == 'HEIGHT':
                    value = get_object_height(obj)
                elif self.sort_by == 'WIDTH':
                    value = get_object_width(obj)
                elif self.sort_by == 'DEPTH':
                    value = get_object_depth(obj)
                objects_with_value.append((obj, value))
            
            objects_with_value.sort(key=lambda x: x[1], reverse=not self.sort_ascending)
            sorted_objects = [item[0] for item in objects_with_value]

            # Calculate automatic padding if enabled
            if self.padding_mode == 'AUTO':
                avg_width = sum(get_bounding_box_width(obj) for obj in sorted_objects) / len(sorted_objects)
                actual_padding = avg_width * (self.padding_percent / 100.0)
            else:
                actual_padding = self.padding
            
            # Calculate total width for centering
            total_width = sum(get_bounding_box_width(obj) for obj in sorted_objects)
            total_padding = actual_padding * (len(sorted_objects) - 1)
            start_x = -(total_width + total_padding) / 2.0
            
            current_x = start_x
            
            for obj in sorted_objects:
                width = get_bounding_box_width(obj)
                
                new_location = mathutils.Vector((
                    current_x + width / 2.0,
                    0.0,
                    0.0
                ))
                
                obj.location = new_location
                current_x += width + actual_padding
            
            padding_info = f"{actual_padding:.4f}" if self.padding_mode == 'AUTO' else f"{self.padding}"
            self.report({'INFO'}, f"Arranged {len(sorted_objects)} objects (padding: {padding_info})")
            return {'FINISHED'}

class VIEW3D_PT_arrange_objects(bpy.types.Panel):
    bl_label = "Quick Arrange"
    bl_idname = "VIEW3D_PT_arrange_objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Quick Arrange'
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Quick Arrange", icon='SORTSIZE')
        
        # Check if selected objects have stored positions
        selected_objects = context.selected_objects
        has_stored_positions = any(
            "arrange_original_loc" in obj for obj in selected_objects
        )
        
        row = box.row()
        if has_stored_positions:
            row.operator("object.arrange_by_volume", text="Restore", icon='LOOP_BACK')
        else:
            row.operator("object.arrange_by_volume", text="Arrange", icon='ALIGN_LEFT')
        
        # Show object count
        selected_count = len(selected_objects)
        box.label(text=f"Selected: {selected_count} objects")

def register():
    bpy.utils.register_class(OBJECT_OT_arrange_by_volume)
    bpy.utils.register_class(VIEW3D_PT_arrange_objects)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_arrange_objects)
    bpy.utils.unregister_class(OBJECT_OT_arrange_by_volume)
