#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_eventcyle, pygame_boilerplate_init

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    skeleton = spine3.utils.autoload(data_dir, "spineboy")
    walkAnimation = skeleton.data.find_animation('walk')
    jumpAnimation = skeleton.data.find_animation('jump')

    skeleton.x = -50
    skeleton.y = 400

    clock = pygame.time.Clock()    

    done = False

    time = 0

    while not done:
        done = pygame_boilerplate_eventcyle()
        clock.tick(60.0)

        delta = clock.get_time() * 1.0

        time += delta / 1000.00

        jump = jumpAnimation.duration
        beforeJump = 1.0
        blendIn = 0.4
        blendOut = 0.4
        blendOutStart = beforeJump + jump - blendOut
        total = 3.75

        root = skeleton.bones[0]
        speed = 180.0

        if time > beforeJump + blendIn and time < blendOutStart:
            speed = 360.0

        root.x = root.x + speed * delta / 1000.00
        
        screen.fill((0, 0, 0))

        if time > total:
            # restart
            time = 0.0
            root.x = -50.0
        elif time > beforeJump + jump:
            # just walk after jump
            walkAnimation.apply(skeleton, time, True)
        elif time > blendOutStart:
            # blend out jump
            walkAnimation.apply(skeleton, time, True)
            jumpAnimation.mix(skeleton, time - beforeJump, False, 1.0 - (time - blendOutStart) / blendOut)
        elif time > beforeJump + blendIn:
            # just jump
            jumpAnimation.apply(skeleton, time - beforeJump, False)
        elif time > beforeJump:
            # blend in jump
            walkAnimation.apply(skeleton, time, True)
            jumpAnimation.mix(skeleton, time - beforeJump, False, (time - beforeJump) / blendIn)
        else:
            # just walk before jump
            walkAnimation.apply(skeleton, time, True)

        skeleton.update_world_transform()
        skeleton.update(clock.get_time())
        skeleton.draw(screen)
        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
