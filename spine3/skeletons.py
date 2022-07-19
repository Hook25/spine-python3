import math
import json
import typing
import pygame
from functools import cache

from .bone import Bone
from .slots import Slot
from . import slots
from . import skin
from . import bone
from . import animation 

class SkeletonData:
    def __init__(self):
        self.bones = []
        self.slots = []
        self.skins = []
        self.animations = []
        self.default_skin = None

    def find_bone(self, bone_name) -> Bone:
        for i, bone in enumerate(self.bones):
            if bone.name == bone_name:
                return bone
        raise ValueError("Unknown bone: %s" % bone_name)

    def find_bone_index(self, bone_name) -> int:
        for i, bone in enumerate(self.bones):
            if bone.name == bone_name:
                return i
        raise ValueError("Unknown bone: %s" % bone_name)

    def find_slot(self, slot_name) -> Slot:
        for i, slot in enumerate(self.slots):
            if slot.name == slot_name:
                return slot
        raise ValueError("Unknown slot: %s" % slot_name)

    def find_slot_index(self, slot_name) -> int:
        for i, slot in enumerate(self.slots):
            if slot.name == slot_name:
                return i
        raise ValueError("Unknown slot: %s" % slot_name)

    def find_skin(self, skinName) -> skin.Skin:
        for i, skin in enumerate(self.skins):
            if skin.name == skinName:
                return skin
        raise ValueError("Unknown skin: %s" % skinName)

    def find_animation(self, animation_name) -> animation.Animation:
        for i, animation in enumerate(self.animations):
            if animation.name == animation_name:
                return animation
        raise ValueError("Unknown animation: %s" % animation_name)

class Skeleton:
    def __init__(self, skeleton_data : SkeletonData, rotation_accuracy = 1):
        self.data = skeleton_data
        self.skin = None
        self.x = 0
        self.y = 0
        self.time = 0.0
        self.flip_x = False
        self.flip_y = False
        self.rotation_accuracy = rotation_accuracy

        self.bones : list[Bone] = self._build_bones(self.data.bones)
        self.slots = self._build_slots(self.data.slots, self.data.bones)
        self.ordered_drawables = self.get_ordered_drawables()

    def get_ordered_drawables(self):
        return [
            slot for slot in self.slots 
                if slot.attachment and slot.attachment.texture
        ]

    def _build_slots(self, slots_data, bones_data):
        to_r = []
        for slot_data in slots_data:
            bone = next(
                self.bones[i] # get the bone who's data matches 
                    for (i, bone) in enumerate(bones_data)
                        if slot_data.bone_data == bone # the one contained in the slot
            )
            slot = Slot(slot_data=slot_data, skeleton=self, bone=bone)
            to_r.append(slot)
        return to_r

    def _build_bones(self, bones_data):
        to_r = [
            Bone(bone_data) for bone_data in bones_data
        ]
        # Now construct the hierarchy, connecting each bone to its parent
        to_pair = (
            (bone, bone_data) for (bone, bone_data) in zip(to_r, bones_data)
                if bone_data.parent
        )
        for (bone, bone_data) in to_pair:
            index = next( # get the index of the first candidate 
                i for (i, candidate_parent) in enumerate(bones_data) 
                    if candidate_parent == bone_data.parent # that is our parent
            )
            bone.parent = to_r[index]
        return to_r
    
    @cache
    def _rotate(self, texture, angle):
        return pygame.transform.rotate(texture, -angle)

    @cache
    def _scale(self, texture, scale_x, scale_y):
        return pygame.transform.scale(texture, (scale_x, scale_y))

    def _accurate(self, i, accuracy):
        return int(i * accuracy) / accuracy
    
    def draw(self, screen):
        import pygame
        to_draw = []
        for slot in self.ordered_drawables:
            local_x = slot.attachment.x * slot.bone.m00 + slot.attachment.y * slot.bone.m01
            local_y = slot.attachment.x * slot.bone.m10 + slot.attachment.y * slot.bone.m11

            rotation = self._accurate(
                -(slot.bone.world_rotation + slot.attachment.rotation),
                self.rotation_accuracy
            )

            x_scale = slot.bone.world_scale_x + slot.attachment.scale_x - 1
            y_scale = slot.bone.world_scale_y + slot.attachment.scale_y - 1

            if self.flip_x:
                x_scale = -x_scale
                rotation = -rotation
            if self.flip_y:
                y_scale = -y_scale
                rotation = -rotation

            flip_x = False
            flip_y = False

            if x_scale < 0:
                flip_x = True
                x_scale = math.fabs(x_scale)
            if y_scale < 0:
                flip_y = True
                y_scale = math.fabs(y_scale)
            
            texture : pygame.Surface = slot.attachment.texture

            if rotation != 0:
                texture = self._rotate(
                    texture, 
                    rotation
                )
            
            old_scale = texture.get_size()
            scale_x, scale_y =  (
                int(old_scale[0] * x_scale), 
                int(old_scale[1] * y_scale)
            )
            texture = self._scale(texture, scale_x, scale_y)

            if flip_x or flip_y:
                texture = pygame.transform.flip(texture, flip_x, flip_y)
                
            # Center image
            cx, cy = texture.get_rect().center
            x = self.x + slot.bone.world_x + local_x
            y = self.y - (slot.bone.world_y + local_y)
            x -= cx
            y -= cy
            to_draw.append((texture, (x, y)))
        screen.blits(to_draw)

    def update_world_transform(self):
        for bone in self.bones:
            bone.update_world_transform(self.flip_x, self.flip_y)

    def set_to_bind_pose(self):
        self.set_bones_to_bind_pose()
        self.set_slots_to_bind_pose()

    def set_bones_to_bind_pose(self):
        for bone in self.bones:
            bone.set_to_bind_pose()

    def set_slots_to_bind_pose(self):
        for i, slot in enumerate(self.slots):
            slot.set_to_bind_pose_with_index(i)

    def get_root_bone(self):
        return self.bones[0]
        
    def set_root_bone(self, bone):
        if len(self.bones):
            self.bones[0] = bone
    
    def find_bone(self, bone_name):
        for i, bone in enumerate(self.bones):
            if self.data.bones[i].name == bone_name:
                return self.bones[i]
        return None

    def find_bone_index(self, bone_name):
        for i, bone in enumerate(self.bones):
            if self.data.bones[i].name == bone_name:
                return i
        return -1

    def find_slot(self, slot_name):
        for i, slot in enumerate(self.slots):
            if self.data.slots[i].name == slot_name:
                return self.slots[i]
        return None

    def find_slot_index(self, slot_name):
        for i, slot in enumerate(self.slots):
            if self.data.slots[i].name == slot_name:
                return i
        return -1

    def set_skin(self, skinName):
        skin = self.data.find_skin(skinName)
        if not skin:
            raise Exception('Skin not found: %s' % skinName)
        self.set_skin_to_skin(skin)

    def set_skin_to_skin(self, new_skin):
        new_skin.attach_all(self)
        self.skin = new_skin
        self.ordered_drawables = self.get_ordered_drawables()

    def get_attachment_by_name(self, slot_name, attachment_name):
        return self.get_attachment_by_index(self.data.find_slot_index(slot_name), attachment_name)

    def get_attachment_by_index(self, slot_index, attachment_name):
        if self.data.default_skin:
            attachment = self.data.default_skin.get_attachment(slot_index, attachment_name)
            if attachment:
                return attachment
        if self.skin:
            return self.skin.get_attachment(slot_index, attachment_name)
        return None

    def set_attachment(self, slot_name, attachment_name):
        for i in range(len(self.slots)):
            if self.slots[i].data.name == slot_name:
                self.slots[i].set_attachment(self.get_attachment_by_index(i, attachment_name))
                return
        raise Exception('Slot not found: %s' % slot_name)

    def update(self, delta):
        self.time += delta
    
    @classmethod
    def parse(cls, desc : typing.TextIO | str, attachment_loader, scale = 1):
        try:
            root = json.loads(desc) 
        except TypeError:
            root = json.load(desc)
        skeleton_data = SkeletonData()
                
        for bone_map in root.get('bones', []):
            bone_data = bone.BoneData.build_from(bone_map, scale, skeleton_data)
            skeleton_data.bones.append(bone_data)

        for slot_map in root.get('slots', []):
            slot_data = slots.SlotData.build_from(slot_map, skeleton_data)
            skeleton_data.slots.append(slot_data)
            
        for (skin_name, slot_map) in root.get('skins', {}).items():
            skin_spec = skin.Skin.build_from(
                slot_map, 
                skin_name, 
                skeleton_data, 
                scale, 
                attachment_loader
            )
            skeleton_data.skins.append(skin_spec)

        for (animation_name, animation_map) in root.get('animations', {}).items():
            animation_data = animation.Animation.build_from(
                name = animation_name, 
                root = animation_map, 
                skeleton_data = skeleton_data, 
                scale = scale
            )
            skeleton_data.animations.append(animation_data)

        return cls(skeleton_data)

    
