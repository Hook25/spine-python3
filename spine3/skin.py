from collections import namedtuple

Key = namedtuple("Key", ["slot_index", "name"])

class Skin:
    def __init__(self, name):
        self.name = name
        self.attachments = {}

    def add_attachment(self, slot_index, name, attachment):
        key = Key(slot_index=slot_index, name=name)
        self.attachments[key] = attachment

    def get_attachment(self, slot_index, name):
        key = Key(slot_index=slot_index, name=name)
        return self.attachments[key]

    @classmethod
    def build_from(cls, slot_map, skin_name, skeleton_data, scale, attachment_loader):
        skin_spec = cls(skin_name)
        for (slot_name, attachments_map) in slot_map.items():
            slot_index = skeleton_data.find_slot_index(slot_name)

            for attach_name, attach_map in attachments_map.items():
                attachment = attachment_loader.new_from(attach_name, attach_map, scale)                      
                skin_spec.add_attachment(slot_index, attach_name, attachment)
        if skin_name == 'default':
            skeleton_data.default_skin = skin_spec
        return skin_spec