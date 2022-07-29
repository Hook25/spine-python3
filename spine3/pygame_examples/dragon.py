#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_init, pygame_boilerplate_eventcyle

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    dragon = spine3.utils.autoload_container(data_dir, "dragon", autotime = True)
    dragon.active_animation_names = ["flying"]

    dragon.x = 500
    dragon.y = 350

    clock = pygame.time.Clock()  

    done = False
    while not done:
        done = pygame_boilerplate_eventcyle()
        clock.tick(0)
        screen.fill((0, 0, 0))
        dragon.render(screen)
        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
