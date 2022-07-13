from enum import IntEnum

from .RegionAttachment import PyGameRegionAttachment

class AttachmentType(IntEnum):
    region = 0
    regionSequence = 1

class AttachmentLoader:
    def __init__(self, atlas):
        super(AttachmentLoader, self).__init__()
        self.atlas = atlas

    def newAttachment(self, type, name):
        if type == AttachmentType.region:
            region = self.atlas.findRegion(name)
            if not region:
                raise ValueError("Atlas region not found: %s" % name)
            return PyGameRegionAttachment(region)
        else:
            raise ValueError('Unknown attachment type: %s' % type)

