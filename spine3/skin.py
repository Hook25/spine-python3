from collections import namedtuple

Key = namedtuple("Key", ["slot_index", "name"])

class Skin:
    def __init__(self, name):
        if not name:
            raise Exception('Name cannot be None.')
        self.name = name
        self.attachments = {}

    def addAttachment(self, slot_index, name, attachment):
        if not name:
            raise Exception('Name cannot be None.')        
        key = Key(slot_index=slot_index, name=name)
        self.attachments[key] = attachment

    def getAttachment(self, slot_index, name):
        key = Key(slot_index=slot_index, name=name)
        if key in self.attachments:
            return self.attachments[key]
        return None
            
    def attachAll(self, skeleton, oldSkin):
        for key, attachment in self.attachments.iteritems():
            slot = skeleton.slots[key.slotIndex]
            if skeleton.slots[key.slotIndex].attachment == attachment:
                newAttachment = self.getAttachment(key.slotIndex, key.name)
                if newAttachment:
                    skeleton.slots[key.slotIndex].setAttachment(newAttachment)
    @classmethod
    def build_from(cls, slot_map, skin_name, skeleton_data, scale, attachment_loader):
        skin_spec = cls(skin_name)
        for (slot_name, attachments_map) in slot_map.items():
            slotIndex = skeleton_data.findSlotIndex(slot_name)

            for attach_name, attach_map in attachments_map.items():
                attachment = attachment_loader.new_from(attach_name, attach_map, scale)                      
                skin_spec.addAttachment(slotIndex, attach_name, attachment)
        if skin_name == 'default':
            skeleton_data.defaultSkin = skin_spec