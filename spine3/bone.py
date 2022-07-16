import math

class BoneData:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.length = 0.0
        self.x = 0.0
        self.y = 0.0
        self.rotation = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.flip_y = False
    @classmethod
    def build_from(cls, json_dct : dict, scale : float, sketon_data):
        to_r = cls(name=json_dct['name'])
        if 'parent' in json_dct:
            to_r.parent = sketon_data.find_bone(json_dct['parent'])
            if not to_r.parent:
                raise Exception('Parent bone not found: %s' % json_dct['name'])

        to_r.length = float(json_dct.get('length', 0.0)) * scale
        to_r.x = float(json_dct.get('x', 0.0)) * scale
        to_r.y = float(json_dct.get('y', 0.0)) * scale
        to_r.rotation = float(json_dct.get('rotation', 0.0))
        to_r.scale_x = float(json_dct.get('scaleX', 1.0))
        to_r.scale_y = float(json_dct.get('scaleY', 1.0))
        return to_r

class Bone:
    def __init__(self, data):
        self.data = data
        self.parent = None
        self.x = data.x
        self.y = data.y
        self.rotation = data.rotation
        self.scale_x = data.scale_x
        self.scale_y = data.scale_y
        self.m00 = 0.0
        self.m01 = 0.0
        self.m10 = 0.0
        self.m11 = 0.0
        self.world_x = 0.0
        self.world_y = 0.0
        self.world_rotation = 0.0
        self.world_scale_x = 0.0
        self.world_scale_y = 0.0
        self.line = None
        self.circle = None

    @property
    def name(self):
        return self.data.name

    def set_to_bind_pose(self):
        self.x = self.data.x
        self.y = self.data.y
        self.rotation = self.data.rotation
        self.scale_x = self.data.scale_x
        self.scale_y = self.data.scale_y

    def update_world_transform(self, flip_x, flip_y):
        if self.parent:
            self.world_x = self.x * self.parent.m00 + self.y * self.parent.m01 + self.parent.world_x 
            self.world_y = self.x * self.parent.m10 + self.y * self.parent.m11 + self.parent.world_y
            self.world_scale_x = self.parent.world_scale_x * self.scale_x
            self.world_scale_y = self.parent.world_scale_y * self.scale_y
            self.world_rotation = self.parent.world_rotation + self.rotation
        else:
            self.world_x = self.x
            self.world_y = self.y
            self.world_scale_x = self.scale_x
            self.world_scale_y = self.scale_y
            self.world_rotation = self.rotation

        radians = math.radians(self.world_rotation)
        cos = math.cos(radians)
        sin = math.sin(radians)
        self.m00 = cos * self.world_scale_x
        self.m10 = sin * self.world_scale_x
        self.m01 = -sin * self.world_scale_y
        self.m11 = cos * self.world_scale_y

        if flip_x:
            self.m00 = -self.m00 
            self.m01 = -self.m01 
        if flip_y:
            self.m10 = -self.m10 
            self.m11 = -self.m11 
        # The C++ runtime has this, but Corona doesn't.
        #if self.data.flip_y:
        #    self.m10 = -self.m10 if self.m10 != 0.0 else 0.0
        #    self.m11 = -self.m11 if self.m11 != 0.0 else 0.0
        
