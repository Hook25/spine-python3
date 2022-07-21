from msilib.schema import File
from pathlib import Path
from . import atlas
from . import skeletons
from . import attachment_loader
class Color:
	def __init__(self, r, g, b, a):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	def __iter__(self):
		return iter((self.a, self.g, self.b, self.a))
	@classmethod
	def parse(cls, hex_str):
		return cls(
			r = int(hex_str[0:2], 16), 
			g = int(hex_str[2:4], 16), 
			b = int(hex_str[4:6], 16), 
			a = int(hex_str[6:8], 16)
		)

def autoload(dir, name):
	dir = Path(dir)
	atlas_path = (dir / name).with_suffix('.atlas').resolve()
	skeleton_path = (dir / name).with_suffix(".json").resolve()
	if not atlas_path.exists():
		raise FileNotFoundError(f"Atlas {atlas_path} not fount")
	if not skeleton_path.exists():
		raise FileNotFoundError(f"Skeleton {skeleton_path} not fount")

	l_atlas = atlas.Atlas(file=atlas_path)
	skeleton = skeletons.Skeleton.parse(
        skeleton_path.open("r"),
        attachment_loader.AttachmentLoader(l_atlas)
    )
	skeleton.set_to_bind_pose()

	return skeleton