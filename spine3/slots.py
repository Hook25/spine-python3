from .utils import Color

class SlotData:
    def __init__(self, name, bone_data, color = Color(255, 255, 255, 255), attachment_name = None):
        self.name = name
        self.bone_data = bone_data
        self.color = color
        self.attachment_name = attachment_name
    @classmethod
    def build_from(cls, slot_map, skeleton_data):
        slot_name = slot_map['name']
        bone_name = slot_map['bone']
        bone_data = skeleton_data.find_bone(bone_name)

        color_hex = slot_map.get('color', "ff" * 4)
        color = Color.parse(color_hex)

        attachment_name = slot_map.get('attachment', None)
        
        slot_data = cls(
            name=slot_name, 
            bone_data=bone_data, 
            color=color, 
            attachment_name = attachment_name
        )

        return slot_data
            
class Slot:
    def __init__(self, slot_data, skeleton, bone):
        self.data = slot_data
        self.skeleton = skeleton
        self.bone = bone
        self.color = self.data.color
        self.attachment = None
        self.attachment_time = 0.0
        self.set_to_bind_pose()
                          
    def set_attachment(self, attachment):
        self.attachment = attachment
        self.attachment_time = self.skeleton.time
    
    def set_to_bind_pose(self):
        for i, slot in enumerate(self.skeleton.data.slots):
            if self.data == slot:
                self.set_to_bind_pose_with_index(i)

    def set_to_bind_pose_with_index(self, slotIndex):
        self.color = self.data.color
        self.set_attachment(
            self.skeleton.get_attachment_by_index(slotIndex, self.data.attachment_name) 
                if self.data.attachment_name else None
        )
    
    
