import sys, os, bpy
sys.path.append(os.path.dirname(__file__)) 
import utils, rotating_camera, target_movement


bl_info = {
    "name":        "Camera Tools",
    "description": "A tool to make good camera animations faster",
    "author":      "Jacques Lucke",
    "version":     (0, 1, 0),
    "blender":     (2, 7, 1),
    "location":    "View 3D > Tool Shelf",
    "warning":     "Alpha",
    "category":    "3D View"
    }
	
	
# interface

class CameraToolsPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	bl_label = "Camera Tools"
	bl_context = "objectmode"
	
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		col.operator("animation.add_rotating_camera")
		
		col = layout.column(align = True)
		col.operator("view3d.object_as_camera", text = "Set Active Camera")
			

#registration

def register():
	bpy.utils.register_module(__name__)
	rotating_camera.register()
	target_movement.register()

def unregister():
	bpy.utils.unregister_module(__name__)
	rotating_camera.unregister()
	target_movement.unregister()

if __name__ == "__main__":
	register()