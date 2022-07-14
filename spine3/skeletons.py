import math
import json
import typing

from pkg_resources import to_filename

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
        self.defaultSkin = None

    def findBone(self, boneName):
        for i, bone in enumerate(self.bones):
            if bone.name == boneName:
                return bone
        raise ValueError("Unknown bone: %s" % boneName)

    def findBoneIndex(self, boneName):
        for i, bone in enumerate(self.bones):
            if bone.name == boneName:
                return i
        raise ValueError("Unknown bone: %s" % boneName)

    def findSlot(self, slotName):
        for i, slot in enumerate(self.slots):
            if slot.name == slotName:
                return slot
        raise ValueError("Unknown slot: %s" % slotName)

    def findSlotIndex(self, slotName):
        for i, slot in enumerate(self.slots):
            if slot.name == slotName:
                return i
        raise ValueError("Unknown slot: %s" % slotName)

    def findSkin(self, skinName):
        for i, skin in enumerate(self.skins):
            if skin.name == skinName:
                return skin
        raise ValueError("Unknown skin: %s" % skinName)

    def findAnimation(self, animationName):
        for i, animation in enumerate(self.animations):
            if animation.name == animationName:
                return animation
        raise ValueError("Unknown animation: %s" % animationName)

class Skeleton:
    def __init__(self, skeletonData : SkeletonData):
        self.data = skeletonData
        self.skin = None
        self.x = 0
        self.y = 0
        self.time = 0.0
        self.flipX = False
        self.flipY = False

        if not self.data:
            raise ValueError('skeletonData can not be null.')

        self.bones = self._build_bones(self.data.bones)
        self.slots = self._build_slots(self.data.slots, self.data.bones)
        self.ordered_drawables = [
            slot for slot in self.slots 
                if slot.attachment and slot.attachment.texture
        ]
    
    def _build_slots(self, slots_data, bones_data):
        to_r = []
        for slotData in slots_data:
            bone = next(
                self.bones[i] # get the bone who's data matches 
                    for (i, bone) in enumerate(bones_data)
                        if slotData.boneData == bone # the one contained in the slot
            )
            slot = Slot(slotData=slotData, skeleton=self, bone=bone)
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

    def draw(self, screen):
        import pygame
        to_draw = []
        for slot in self.ordered_drawables:
            x = self.x + slot.bone.worldX + slot.attachment.x * slot.bone.m00 + slot.attachment.y * slot.bone.m01
            y = self.y - (slot.bone.worldY + slot.attachment.x * slot.bone.m10 + slot.attachment.y * slot.bone.m11)

            rotation = -(slot.bone.worldRotation + slot.attachment.rotation)

            x_scale = slot.bone.worldScaleX + slot.attachment.scaleX - 1
            y_scale = slot.bone.worldScaleY + slot.attachment.scaleY - 1

            if self.flipX:
                x_scale = -x_scale
                rotation = -rotation
            if self.flipY:
                y_scale = -y_scale
                rotation = -rotation

            flipX = False
            flipY = False

            if x_scale < 0:
                flipX = True
                x_scale = math.fabs(x_scale)
            if y_scale < 0:
                flipY = True
                y_scale = math.fabs(y_scale)
            
            texture : pygame.Surface = slot.attachment.texture
            old_scale = texture.get_size()
            act_scale = (
                int(old_scale[0] * x_scale), 
                int(old_scale[1] * y_scale)
            )
            texture = pygame.transform.flip(texture, flipX, flipY)
            texture = pygame.transform.scale(texture, act_scale)
            texture = pygame.transform.rotate(texture, -rotation)

            # Center image
            cx, cy = texture.get_rect().center
            x -= cx
            y -= cy
            to_draw.append((texture, (x, y)))

        screen.blits(to_draw)

    def updateWorldTransform(self):
        for bone in self.bones:
            bone.updateWorldTransform(self.flipX, self.flipY)

    def setToBindPose(self):
        self.setBonesToBindPose()
        self.setSlotsToBindPose()

    def setBonesToBindPose(self):
        for bone in self.bones:
            bone.setToBindPose()

    def setSlotsToBindPose(self):
        for i, slot in enumerate(self.slots):
            slot.setToBindPoseWithIndex(i)

    def getRootBone(self):
        if len(self.bones):
            return self.bones[0]
        return None

    def setRootBone(self, bone):
        if len(self.bones):
            self.bones[0] = bone
    
    def findBone(self, boneName):
        for i, bone in enumerate(self.bones):
            if self.data.bones[i].name == boneName:
                return self.bones[i]
        return None

    def findBoneIndex(self, boneName):
        for i, bone in enumerate(self.bones):
            if self.data.bones[i].name == boneName:
                return i
        return -1

    def findSlot(self, slotName):
        for i, slot in enumerate(self.slots):
            if self.data.slots[i].name == slotName:
                return self.slots[i]
        return None

    def findSlotIndex(self, slotName):
        for i, slot in enumerate(self.slots):
            if self.data.slots[i].name == slotName:
                return i
        return -1

    def setSkin(self, skinName):
        skin = self.data.findSkin(skinName)
        if not skin:
            raise Exception('Skin not found: %s' % skinName)
        self.setSkinToSkin(skin)

    def setSkinToSkin(self, newSkin):
        if self.skin and newSkin:
            newSkin.attachAll(self, self.skin)
        self.skin = newSkin

    def getAttachmentByName(self, slotName, attachmentName):
        return self.getAttachmentByIndex(self.data.findSlotIndex(slotName), attachmentName)

    def getAttachmentByIndex(self, slotIndex, attachmentName):
        if self.data.defaultSkin:
            attachment = self.data.defaultSkin.getAttachment(slotIndex, attachmentName)
            if attachment:
                return attachment
        if self.skin:
            return self.skin.getAttachment(slotIndex, attachmentName)
        return None

    def setAttachment(self, slotName, attachmentName):
        for i in range(len(self.slots)):
            if self.slots[i].data.name == slotName:
                self.slots[i].setAttachment(self.getAttachmentByIndex(i, attachmentName))
                return
        raise Exception('Slot not found: %s' % slotName)

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
            boneData = bone.BoneData.build_from(bone_map, scale, skeleton_data)
            skeleton_data.bones.append(boneData)

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

    
