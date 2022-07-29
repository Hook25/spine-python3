#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_init, pygame_boilerplate_eventcyle

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    goblin = spine3.utils.autoload_container(data_dir, "goblins", autotime=True)
    goblin.skin = "goblin"
    goblin.active_animation_names = ["walk"]

    goblin.x = 120
    goblin.y = 400

    goblingirl = goblin.clone()
    # clone creates a new object with the same skin and active_animations
    goblingirl.skin = 'goblingirl'

    goblingirl.x = 420
    goblingirl.y = 400

    clock = pygame.time.Clock()    

    done = False
    while not done:
        done = pygame_boilerplate_eventcyle()
        clock.tick(0)
        screen.fill((0, 0, 0))
        
        goblin.render(screen)
        goblingirl.render(screen)

        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()