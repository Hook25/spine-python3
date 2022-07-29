import time

class BaseAnimationContainer:
	def __init__(self, skeleton):
		self.skeleton = skeleton
		self.active_animations = {}

	@property
	def active_animation_names(self):
		return list(self.active_animations)

	@active_animation_names.setter
	def active_animation_names(self, animation_names : list[str]):
		self.active_animations = {
			x : self.skeleton.data.find_animation(x) for x in animation_names
		}

	@staticmethod
	def _gact(dct, name):
		try:
			return dct[name]
		except KeyError:
			return 0
	
	def get_weights(self, mix_weight):
		weights = [self._gact(mix_weight, name) for name in self.active_animation_names]
		if len(weights) == 1:
			weights = [1]
		return weights
	
	def get_times(self, times):
		if isinstance(times, dict):
			return [self._gact(times, name) for name in self.active_animation_names]
		return [times]

	def animate(self, name, time, loop = True, weight = 1):
		if not self.active_animations:
			raise ValueError("No active animation")
		self.active_animations[name].mix(
				self.skeleton, 
				time, 
				loop, 
				weight
			)
	def draw(self, surface):
		self.skeleton.update_world_transform()
		self.skeleton.draw(surface)
	def render(self, surface, time, loop = True, mix_weight = []):
		self.animate(self.active_animation_names[0], time, loop, mix_weight)
		self.draw(surface)

class AnimationContainer(BaseAnimationContainer):
	@property
	def x(self):
		return self.skeleton.x
	@x.setter
	def x(self, value):
		self.skeleton.x = value
	@property
	def y(self):
		return self.skeleton.y
	@y.setter
	def y(self, value):
		self.skeleton.y = value
	@property
	def flip_x(self):
		return self.skeleton.flip_x
	@flip_x.setter
	def flip_x(self, val):
		self.skeleton.flip_x = val
	@property
	def flip_y(self):
		return self.skeleton.flip_y
	@flip_y.setter
	def flip_y(self, val):
		self.skeleton.flip_y = val
	@property
	def skin(self):
		return self.skeleton.skin.name
	@skin.setter
	def skin(self, val):
		self.skeleton.set_skin(val)
	def clone(self):
		from .skeletons import Skeleton
		to_r = self.__class__(Skeleton(self.skeleton.data))
		to_r.skin = self.skin
		to_r.active_animations = self.active_animations
		return to_r


class AutotimeAnimationContainer(AnimationContainer):
	def animate(self, name, loop=True, mix_weight = 1):
		return super().animate(name, time.time(), loop, mix_weight)
	def render(self, surface, loop = True, weight = 1):
		self.animate(self.active_animation_names[0], loop, weight)
		self.draw(surface)