#!/usr/bin/env python

import os

import pygame

import pyguts.src as pyguts
import spine 

from common import get_asset

def main():
    pygame.init()

    width, height = (1024, 768)

    screen = pygame.display.set_mode((width, height))
    screen.fill((0,0,0))
    caption = 'PyGuts - A Pygame front-end based on the python-spine Runtime'
    pygame.display.set_caption(caption, 'Spine Runtime')

    atlas = pyguts.Atlas.Atlas(file=get_asset('dragon.atlas'))
    skeletonJson = spine.SkeletonJson.SkeletonJson(pyguts.AtlasAttachmentLoader.AtlasAttachmentLoader(atlas))
    skeletonData = skeletonJson.readSkeletonDataFile(get_asset('dragon.json'))

    skeleton = pyguts.Skeleton.Skeleton(skeletonData=skeletonData)

    flyingAnimation = skeletonData.findAnimation('flying')
    skeleton.debug = False

    skeleton.setToBindPose()
    skeleton.x = 480
    skeleton.y = 320
    skeleton.flipX = False
    skeleton.flipY = False
    skeleton.updateWorldTransform()

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
        skeleton.updateWorldTransform()
        screen.fill((0, 0, 0))
        skeleton.draw(screen, 0)
        pygame.display.set_caption('%s  %.2f' % (caption, clock.get_fps()), 'Spine Runtime')
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
