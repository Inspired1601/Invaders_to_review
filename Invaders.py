import sys

import pygame

from resources import ResourceManager
from scenes import MenuScene


class Screen:
    """Creates a Screen of the specified size and provides a surface to draw on.
    """
    def __init__(self, size, caption='Space Invaders'):
        # Main surface to draw every game object on.
        # `display.set_mode` creates a Screen
        # and returns a surface.
        self.surface = pygame.display.set_mode(size)

        pygame.display.set_caption(caption)

    def get_surface(self):
        return self.surface


class Game:
    """Controls main game loop (handles events + draws all game objects).  
    In every iteration it checks which scene is active
    and calls corresponding methods of this scene.

    Scene (not Game, but a scene managed by Game!) methods are:
        handle_event(event):    to handle current event
                                the way it should be handled in current scene
        update():               to update all objects' state
        draw():                 to blit every object from current scene
    """
    def __init__(self, size, fps=60):
        pygame.init()

        self.FPS = fps
        self.screen = Screen(size).get_surface()
        self.resources = ResourceManager()

        self.scene = MenuScene(self.resources)
        self.run()

    def run(self):
        # Necessary for FPS controling via `clock.tick()`
        clock = pygame.time.Clock()

        # `self.scene` will become `None` only if
        # some scene will explicitly say `No next scene expected`
        while self.scene:
            # Slowing loop so it won't run faster than `FPS` times per second.
            # Otherwise game will run to fast, up to 1.5k+ FPS.
            clock.tick(self.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                else:
                    self.scene.handle_event(event)

            self.scene.update()

            self.screen.blit(self.resources.images['bg'].img, (0, 0))
            # Blits every object created in a current scene to the main surface
            self.scene.draw(self.screen)
            # `update` actually displays every "blitted" object on surfaces
            pygame.display.update()

            self.scene = self.scene.next_scene


if __name__ == '__main__':
    Game(size=(800, 600), fps=60)
