#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_init

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    skeleton = spine3.utils.autoload(data_dir, "dragon")
    flyingAnimation = skeleton.data.find_animation('flying')

    skeleton.x = 500
    skeleton.y = 350

    clock = pygame.time.Clock()    
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    break
        clock.tick(0)
        flyingAnimation.apply(
            skeleton=skeleton,
            time=pygame.time.get_ticks() / 1000,
            loop=True
        )
        skeleton.update_world_transform()
        screen.fill((0, 0, 0))
        skeleton.draw(screen)
        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()

if __name__ == '__main__':
    main()
