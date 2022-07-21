from pathlib import Path

HERE = (Path(__file__) / "..").resolve()

def get_asset(name):
  return HERE / "data" / name

def pygame_boilerplate_init():
    import pygame
    pygame.init()

    width, height = (1024, 768)

    screen = pygame.display.set_mode((width, height))
    screen.fill((0,0,0))
    caption = 'spine3 - A Pygame and Spine Runtime'
    pygame.display.set_caption(caption, 'Spine Runtime')
    return screen
    
def pygame_boilerplate_eventcyle():
  import pygame
  return any(
    event.type == pygame.QUIT or
      pygame.key.get_pressed()[pygame.K_ESCAPE]
      for event in pygame.event.get()
  )