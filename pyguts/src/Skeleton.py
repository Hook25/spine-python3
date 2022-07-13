import math
import spine
import pygame

class Circle:
    def __init__(self, x, y, r):
        super().__init__()
        self.x = x
        self.y = y
        self.r = r
        self.color = (0, 255, 0, 255)

class Line:
    def __init__(self, length):
        super().__init__()
        self.x = 0.0
        self.y = 0.0
        self.x1 = 0.0
        self.x2 = 0.0
        self.length = length
        self.rotation = 0.0
        self.color = (255, 0, 0, 255)
        self.texture = pygame.Surface((640, 480), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.texture, (255, 255, 0, 64), (0, 0, self.texture.get_width(), self.texture.get_height()), 1)


    def rotate(self):
        return pygame.transform.rotozoom(self.texture, self.rotation, self.x_scale)

class Skeleton(spine.Skeleton.Skeleton):
    def __init__(self, skeletonData):
        super().__init__(skeletonData=skeletonData)
        self.x = 0
        self.y = 0
    def draw(self, screen : pygame.Surface, states):
        drawable_slots = (slot for slot in self.drawOrder if slot.attachment and slot.attachment.texture)
        to_draw = []
        for slot in drawable_slots:
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