import math

from . import attachment

class BaseRegionAttachment(attachment.Attachment):
    def __init__(self):
        super().__init__()
        self.x = 0.0
        self.y = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.rotation = 0.0
        self.width = 0.0
        self.height = 0.0
        self.offset = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]

    def update_offset(self):
        local_x_2 = self.width / 2.0
        local_y_2 = self.height / 2.0
        local_x = -local_x_2
        local_y = -local_y_2
        local_x *= self.scale_x
        local_y *= self.scale_y
        radians = math.radians(self.rotation)
        cos = math.cos(radians)
        sin = math.sin(radians)
        local_x_cos = local_x * cos + self.x
        local_x_sin = local_x * sin
        local_y_cos = local_y * cos + self.y
        local_y_sin = local_y * sin
        local_x_2_cos = local_x_2 * cos + self.x
        local_x_2_sin = local_x_2 * sin
        local_y_2_cos = local_y_2 * cos + self.y
        local_y_2_sin = local_y_2 * sin
        self.offset[0] = local_x_cos - local_y_sin
        self.offset[1] = local_y_cos + local_x_sin
        self.offset[2] = local_x_cos - local_y_2_sin
        self.offset[3] = local_y_2_cos + local_x_sin
        self.offset[4] = local_x_2_cos - local_y_2_sin
        self.offset[5] = local_y_2_cos + local_x_2_sin
        self.offset[6] = local_x_2_cos - local_y_sin
        self.offset[7] = local_y_cos + local_x_2_sin

class TextureCoordinates:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

class ColoredVertex:
    def __init__(self):
        import pygame
        self.color = pygame.Color(0, 0, 0, 0)
        self.tex_coords = TextureCoordinates()

class PyGameRegionAttachment(BaseRegionAttachment):
    def __init__(self, region):
        import pygame
        super().__init__()
        self.verticies = [ColoredVertex(), ColoredVertex(), ColoredVertex(), ColoredVertex()]
        self.u = region.x
        self.u2 = self.u + region.width
        self.v = region.y
        self.v2 = self.v + region.height
        self.rect = pygame.Rect((self.u, self.v, region.width, region.height))
        self.texture = region.page.texture.subsurface(self.rect)
        self.offset = pygame.Rect(0, 0, region.width, region.height)
        self.offset.center = (region.width / 2, region.height / 2)
        if region.rotate:
            self.verticies[1].tex_coords.x = self.u
            self.verticies[1].tex_coords.y = self.v2
            self.verticies[2].tex_coords.x = self.u
            self.verticies[2].tex_coords.y = self.v
            self.verticies[3].tex_coords.x = self.u2
            self.verticies[3].tex_coords.y = self.v
            self.verticies[0].tex_coords.x = self.u2
            self.verticies[0].tex_coords.y = self.v2
        else:
            self.verticies[0].tex_coords.x = self.u
            self.verticies[0].tex_coords.y = self.v2
            self.verticies[1].tex_coords.x = self.u
            self.verticies[1].tex_coords.y = self.v
            self.verticies[2].tex_coords.x = self.u2
            self.verticies[2].tex_coords.y = self.v
            self.verticies[3].tex_coords.x = self.u2
            self.verticies[3].tex_coords.y = self.v2

    def draw(self, slot):
        skeleton = slot.skeleton

        r = skeleton.r * slot.r * 255.0
        g = skeleton.g * slot.g * 255.0
        b = skeleton.b * slot.b * 255.0
        a = skeleton.a * slot.a * 255.0

        self.verticies[0].color.r = r
        self.verticies[0].color.g = g
        self.verticies[0].color.b = b
        self.verticies[0].color.a = a
        self.verticies[1].color.r = r
        self.verticies[1].color.g = g
        self.verticies[1].color.b = b
        self.verticies[1].color.a = a
        self.verticies[2].color.r = r
        self.verticies[2].color.g = g
        self.verticies[2].color.b = b
        self.verticies[2].color.a = a
        self.verticies[3].color.r = r
        self.verticies[3].color.g = g
        self.verticies[3].color.b = b
        self.verticies[3].color.a = a

        self.update_offset()
        self.update_world_verticies(slot.bone)

        skeleton.texture = self.texture
        skeleton.vertex_array.append(self.verticies[0])
        skeleton.vertex_array.append(self.verticies[1])
        skeleton.vertex_array.append(self.verticies[2])
        skeleton.vertex_array.append(self.verticies[3])

    def update_world_vertices(self, bone):
        x = bone.worldX
        y = bone.worldY
        m00 = bone.m00
        m01 = bone.m01
        m10 = bone.m10
        m11 = bone.m11
        self.verticies[0].position.x = self.offset[0] * m00 + self.offset[1] * m01 + x
        self.verticies[0].position.y = self.offset[0] * m10 + self.offset[1] * m11 + y
        self.verticies[1].position.x = self.offset[2] * m00 + self.offset[3] * m01 + x
        self.verticies[1].position.y = self.offset[2] * m10 + self.offset[3] * m11 + y
        self.verticies[2].position.x = self.offset[4] * m00 + self.offset[5] * m01 + x
        self.verticies[2].position.y = self.offset[4] * m10 + self.offset[5] * m11 + y
        self.verticies[3].position.x = self.offset[6] * m00 + self.offset[7] * m01 + x
        self.verticies[3].position.y = self.offset[6] * m10 + self.offset[7] * m11 + y
        
