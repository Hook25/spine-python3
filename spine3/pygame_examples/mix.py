#!/usr/bin/env python

import pygame
import spine3 
from pathlib import Path

from .common import pygame_boilerplate_eventcyle, pygame_boilerplate_init

data_dir = (Path(__file__) / ".." / "data").resolve()

def main():
    screen = pygame_boilerplate_init()

    skeleton = spine3.utils.autoload_container(data_dir, "spineboy", autotime = False)
    skeleton.active_animation_names = ["walk", "jump"]

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

        jump = skeleton.active_animations["jump"].duration
        before_jump = 1.0
        blend_in = 0.4
        blend_out = 0.4
        blend_out_start = before_jump + jump - blend_out
        total = 3.75

        speed = 180.0

        if time > before_jump + blend_in and time < blend_out_start:
            speed = 360.0

        skeleton.x = skeleton.x + speed * delta / 1000.00
        
        screen.fill((0, 0, 0))

        if time > total:
            # restart
            time = 0.0
            skeleton.x = -50.0
        elif time > before_jump + jump:
            # just walk after jump
            skeleton.animate("walk", time, True)
        elif time > blend_out_start:
            # blend out jump
            skeleton.animate("walk", time, True)
            skeleton.animate("jump", time - before_jump, False, 1.0 - (time - blend_out_start) / blend_out)
        elif time > before_jump + blend_in:
            # just jump
            skeleton.animate("jump", time - before_jump, False)
        elif time > before_jump:
            # blend in jump
            skeleton.animate("walk", time, True)
            skeleton.animate("jump", time - before_jump, False, (time - before_jump) / blend_in)
        else:
            # just walk before jump
            skeleton.animate("walk", time, True)

        skeleton.draw(screen)
        pygame.display.set_caption(f'Spine Runtime: FPS: {int(clock.get_fps())}')
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
