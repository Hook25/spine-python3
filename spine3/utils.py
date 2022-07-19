
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
