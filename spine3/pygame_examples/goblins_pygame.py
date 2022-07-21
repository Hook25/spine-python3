#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_init

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    goblin = spine3.utils.autoload(data_dir, "goblins")

    walk_animation = goblin.data.find_animation('walk')
    goblin.debug = True

    goblin.set_skin('goblin')
    goblin.x = 120
    goblin.y = 400

    goblingirl = spine3.skeletons.Skeleton(skeleton_data=goblin.data)

    goblingirl.set_skin('goblingirl')
    goblingirl.x = 420
    goblingirl.y = 400

    clock = pygame.time.Clock()    
    animationTime = 0.0

    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                done = True
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    done = True
        clock.tick(0)
        animationTime += clock.get_time() / 1000.0
        walk_animation.apply(
            skeleton=goblin,
            time=animationTime,
            loop=True
        )
        walk_animation.apply(
            skeleton=goblingirl,
            time=animationTime,
            loop=True
        )
        goblin.update_world_transform()
        goblingirl.update_world_transform()
        screen.fill((0, 0, 0))
        goblin.draw(screen)
        goblingirl.draw(screen)
        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()