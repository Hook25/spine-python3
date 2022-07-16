class SlotData:
    def __init__(self, name, bone_data):
        if not name:
            raise ValueError('Name cannot be None.')

        if not bone_data:
            raise ValueError('bone_data cannot be None.')

        self.name = name
        self.bone_data = bone_data
        self.r = 255
        self.g = 255
        self.b = 255
        self.a = 255
        self.attachment_name = None
    @classmethod
    def build_from(cls, slot_map, skeleton_data):
        slot_name = slot_map['name']
        bone_name = slot_map['bone']
        bone_data = skeleton_data.find_bone(bone_name)

        slot_data = cls(name=slot_name, bone_data=bone_data)
            
        if 'color' in slot_map:
            color_hex = slot_map['color']
            slot_data.r = int(color_hex[0:2], 16)
            slot_data.g = int(color_hex[2:4], 16)
            slot_data.b = int(color_hex[4:6], 16)
            slot_data.a = int(color_hex[6:8], 16)

        if 'attachment' in slot_map:
            slot_data.attachment_name = slot_map['attachment']

        return slot_data
            
class Slot:
    def __init__(self, slot_data, skeleton, bone):
        if not slot_data:
            raise Exception('slotData cannot be None.')
        if not skeleton:
            raise Exception('skeleton cannot be None.')
        if not bone:
            raise Exception('bone cannot be None.')
        self.data = slot_data
        self.skeleton = skeleton
        self.bone = bone
        self.r = 255
        self.g = 255
        self.b = 255
        self.a = 255
        self.attachment = None
        self.attachment_time = 0.0
        self.set_to_bind_pose()


    def set_color(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
                          
        
    def set_attachment(self, attachment):
        self.attachment = attachment
        self.attachment_time = self.skeleton.time


    def set_attachment_time(self, time):
        self.attachment_time = self.skeleton.time - time


    def get_attachment_time(self):
        return self.skeleton.time - self.attachment_time

    
    def set_to_bind_pose(self):
        for i, slot in enumerate(self.skeleton.data.slots):
            if self.data == slot:
                self.set_to_bind_pose_with_index(i)


    def set_to_bind_pose_with_index(self, slotIndex):
        self.set_color(self.data.r, self.data.g, self.data.b, self.data.a)
        self.set_attachment(self.skeleton.get_attachment_by_index(slotIndex, self.data.attachment_name) if self.data.attachment_name else None)
    
    
