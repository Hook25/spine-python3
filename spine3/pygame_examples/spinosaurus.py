#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_init, pygame_boilerplate_eventcyle

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    skeleton = spine3.utils.autoload(data_dir, "spinosaurus")
    animation = skeleton.data.find_animation('animation')

    skeleton.x = 512
    skeleton.y = 360

    clock = pygame.time.Clock()    
    animationTime = 0.0

    done = False

    while not done:
        done = pygame_boilerplate_eventcyle()
        clock.tick(0)
        animationTime += clock.get_time() / 1000.0
        animation.apply(
            skeleton=skeleton,
            time=animationTime,
            loop=True
        )
        skeleton.update_world_transform()
        screen.fill((0, 0, 0))
        skeleton.draw(screen)
        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()