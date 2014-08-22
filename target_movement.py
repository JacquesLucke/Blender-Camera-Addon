import bpy
from utils import *

def insertTargetMovementCamera():
	print("hi")



# operators
		
class AddTargetMovementCamera(bpy.types.Operator):
	bl_idname = "animation.add_target_movement_camera"
	bl_label = "Add Target Camera"
	
	def execute(self, context):
		insertTargetMovementCamera()
		return{"FINISHED"}


def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)