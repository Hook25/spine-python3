class SlotData:
    def __init__(self, name, bone_data):
        if not name:
            raise ValueError('Name cannot be None.')

        if not bone_data:
            raise ValueError('boneData cannot be None.')

        self.name = name
        self.boneData = bone_data
        self.r = 255
        self.g = 255
        self.b = 255
        self.a = 255
        self.attachmentName = None
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
            slot_data.attachmentName = slot_map['attachment']

        return slot_data
            
class Slot:
    def __init__(self, slotData, skeleton, bone):
        if not slotData:
            raise Exception('slotData cannot be None.')
        if not skeleton:
            raise Exception('skeleton cannot be None.')
        if not bone:
            raise Exception('bone cannot be None.')
        self.data = slotData
        self.skeleton = skeleton
        self.bone = bone
        self.r = 255
        self.g = 255
        self.b = 255
        self.a = 255
        self.attachment = None
        self.attachmentTime = 0.0
        self.setToBindPose()


    def setColor(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
                          
        
    def setAttachment(self, attachment):
        self.attachment = attachment
        self.attachmentTime = self.skeleton.time


    def setAttachmentTime(self, time):
        self.attachmentTime = self.skeleton.time - time


    def getAttachmentTime(self):
        return self.skeleton.time - self.attachmentTime

    
    def setToBindPose(self):
        for i, slot in enumerate(self.skeleton.data.slots):
            if self.data == slot:
                self.setToBindPoseWithIndex(i)


    def setToBindPoseWithIndex(self, slotIndex):
        self.setColor(self.data.r, self.data.g, self.data.b, self.data.a)
        self.setAttachment(self.skeleton.get_attachment_by_index(slotIndex, self.data.attachmentName) if self.data.attachmentName else None)
    
    
