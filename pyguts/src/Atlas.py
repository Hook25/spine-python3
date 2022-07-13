import os
import pygame
import spine
from pathlib import Path

class AtlasPage(spine.Atlas.AtlasPage):
    def __init__(self):
        super().__init__()
        self.texture = None

class AtlasRegion(spine.Atlas.AtlasRegion):
    def __init__(self):
        super().__init__()
        self.page = None

class Atlas(spine.Atlas.Atlas):
    def __init__(self, file : Path):
        super().__init__()
        # file is dir/file
        # get ../../ because paths are in the form dir/...
        self.file_loc = (file.parent.parent)
        super().loadWithFile(file)
    def newAtlasPage(self, name):
        page = AtlasPage()
        img_path = self.file_loc / name
        page.texture = pygame.image.load(img_path.resolve()).convert_alpha()
        return page
    def newAtlasRegion(self, page):
        region = AtlasRegion()
        region.page = page
        return region
    def findRegion(self, name):
        return super().findRegion(name)
