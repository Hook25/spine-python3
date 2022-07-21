from multiprocessing.sharedctypes import Value
import os
from pathlib import Path
from enum import IntEnum

formatNames = (
    'Alpha', 
    'Intensity',
    'LuminanceAlpha',
    'RGB565',
    'RGBA4444',
    'RGB888',
    'RGBA8888'
)

textureFiltureNames = (
    'Nearest',
    'Linear',
    'MipMap', 
    'MipMapNearestNearest', 
    'MipMapLinearNearest',
    'MipMapNearestLinear', 
    'MipMapLinearLinear'
)


class Format(IntEnum):
    alpha=0
    intensity=1
    luminanceAlpha=2
    rgb565=3
    rgba4444=4
    rgb888=5
    rgba8888=6

class TextureFilter(IntEnum):
    nearest=0
    linear=1
    mipMap=2
    mipMapNearestNearest=3
    mipMapLinearNearest=4
    mipMapNearestLinear=5
    mipMapLinearLinear=6

class TextureWrap(IntEnum):
    mirroredRepeat=0
    clampToEdge=1
    repeat=2

class Atlas:
    def __init__(self, file : Path):
        self.pages = []
        self.regions = []
        self.file_loc = (Path(file).parent.parent)
        self.loadWithFile(file)

    def loadWithFile(self, file):
        with Path(file).open('r') as fh:
            text = fh.readlines()
        self.load(text)

    def load(self, text):
        page = None
        _page = None
        _region = {}
        def s_rs(s): return s.strip().rstrip()

        def get_value(line : str):
            if "," in line:
                return [s_rs(x) for x in line.split(",")]
            elif line in ["false", "true"]:
                return bool(line.capitalize())
            return s_rs(line)
        
        for line in text:
            value = line.strip().rstrip()
            if len(value) == 0:
                _page = {}
                page = None
            if page is None:
                if not ':' in value:
                    value = s_rs(value)
                    _page['name'] = value
                else:
                    (key, value) = (s_rs(x) for x in value.split(':'))
                    value = get_value(value)
                    _page[key] = value
                    if key == 'repeat':
                        path = self.file_loc / _page['name']
                        page = AtlasPage.build_from(_page, path)              
                        self.pages.append(page)
            else:
                if not ':' in value:
                    value = s_rs(value)
                    _region['name'] = value
                else:
                    (key, value) = (s_rs(x) for x in value.split(':'))
                    value = get_value(value)
                    if isinstance(value, list):
                        _region[key] = [int(x) for x in value]
                    else:
                        _region[key] = value
                    if key == 'index':
                        region = AtlasRegion.build_from(_region, page)
                        self.regions.append(region)
                        _region = {}

    def findRegion(self, name):
        for region in self.regions:
            if region.name == name:
                return region
        raise NameError(f"Region {name} does not exist")

class AtlasRegion:
    def __init__(self, name, x, y, width, height, offset_x, offset_y, og_width, og_height, index, splits, pads, page):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.og_width = og_width
        self.og_height = og_height
        self.index = index
        self.splits = splits
        self.pads = pads
        self.page = page

        self.flip = False
        self.rotate = False
    @classmethod
    def build_from(cls, region, page):
        name = region['name']
        x, y= region['xy']
        width, height = region['size']
        splits = []
        pads = []
        if 'split' in region:
            splits = region['split']
            if 'pad' in region:
                pads = region['pad']
        og_width, og_height = region['orig']
        offset_x, offset_y = region['offset']
        index = int(region['index'])
        return cls(name, x, y, width, height, offset_x, offset_y, og_width, og_height, index, splits, pads, page)

class AtlasPage:
    def __init__(self, name, format, min_filter, mag_filter, u_wrap, v_wrap, texture):
        self.name = name
        self.format = format
        self.min_filter = min_filter
        self.mag_filter = mag_filter
        self.u_wrap = u_wrap
        self.v_wrap = v_wrap
        self.texture = texture
    @classmethod
    def build_from(cls, page, img_path):
        import pygame
        texture = pygame.image.load(img_path.resolve()).convert_alpha()
        min_filter, mag_filter = page['filter']
        u_wrap = TextureWrap.clampToEdge
        v_wrap = TextureWrap.clampToEdge
        if page['repeat'] == 'x':
            u_wrap = TextureWrap.repeat
        elif page['repeat'] == 'y':
            v_wrap = TextureWrap.repeat
        elif page['repeat'] == 'xy':
            u_wrap = TextureWrap.repeat
            v_wrap = TextureWrap.repeat
        return cls(
            name = page['name'], 
            format = page['format'], 
            min_filter = min_filter, 
            mag_filter = mag_filter, 
            u_wrap = u_wrap, 
            v_wrap = v_wrap, 
            texture = texture
        )
