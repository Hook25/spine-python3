#!/usr/bin/env python

import os
import pygame
import spine3 
from .common import get_asset

def main():
    pygame.init()

    width, height = (1024, 768)

    screen = pygame.display.set_mode((width, height))
    screen.fill((0,0,0))
    caption = 'spine3 - A Pygame and Spine Runtime'
    pygame.display.set_caption(caption, 'Spine Runtime')

    atlas = spine3.atlas.Atlas(file=get_asset('dragon.atlas'))

    skeleton = spine3.skeletons.Skeleton.parse(
        get_asset('dragon.json').open("r"),
        spine3.attachment_loader.AttachmentLoader(atlas)
    )
    flyingAnimation = skeleton.data.find_animation('flying')
    skeleton.debug = False

    skeleton.set_to_bind_pose()
    skeleton.x = 500
    skeleton.y = 420
    skeleton.flipX = False
    skeleton.flipY = False
    skeleton.update_world_transform()

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
        flyingAnimation.apply(skeleton=skeleton,
                              time=animationTime,
                              loop=True)
        skeleton.update_world_transform()
        screen.fill((0, 0, 0))
        skeleton.draw(screen)
        pygame.display.set_caption('%s  %.2f' % (caption, clock.get_fps()), 'Spine Runtime')
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
