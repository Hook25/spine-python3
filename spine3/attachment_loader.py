from enum import Enum

from .region_attachment import PyGameRegionAttachment

class AttachmentType(Enum):
    Region = 0
    RegionSequence = 1
    @staticmethod
    def parse(string : str):
        string = string[0].upper() + string[1:]
        return AttachmentType[string]

class AttachmentLoader:
    def __init__(self, atlas):
        super().__init__()
        self.atlas = atlas

    def new_from(self, attach_name, attach_map, scale):
        region = self.atlas.findRegion(attach_map.get("name", attach_name))
        
        type = AttachmentType.parse(attach_map.get('type', 'region'))
        if type != AttachmentType.Region:
            raise ValueError('Unknown attachment type: %s' % type)

        attachment = PyGameRegionAttachment(region)
        attachment.name = attach_name
        attachment.x = float(attach_map.get('x', 0.0)) * scale
        attachment.y = float(attach_map.get('y', 0.0)) * scale
        attachment.scale_x = float(attach_map.get('scaleX', 1.0))
        attachment.scale_y = float(attach_map.get('scaleY', 1.0))
        attachment.rotation = float(attach_map.get('rotation', 0.0))
        attachment.width = float(attach_map.get('width', 32)) * scale
        attachment.height = float(attach_map.get('height', 32)) * scale  

        return attachment

