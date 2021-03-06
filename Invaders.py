import sys

import pygame

from resources import ResourceManager
from scenes import MenuScene


def create_window(size, caption):
    surface = pygame.display.set_mode(size)
    pygame.display.set_caption(caption)

    return surface                      # Возвращаем основную поверхность созданного окна


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
        self.screen = create_window(size, 'Space Invaders')
        self.resources = ResourceManager()

        self.scene = MenuScene(self.resources)
        self.run()

    def run(self, fps=60):
        # Necessary for FPS controling via `clock.tick()`
        clock = pygame.time.Clock()

        # `self.scene` will become `None` only if
        # some scene will explicitly say `No next scene expected`
        while self.scene:
            # Slowing loop so it won't run faster than `FPS` times per second.
            # Otherwise game will run to fast, up to 1.5k+ FPS.
            clock.tick(fps)

            self.handle_events()
            self.scene.update()
            self.draw_content()

            self.scene = self.scene.next_scene

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            else:
                self.scene.handle_event(event)

    def draw_content(self):
        # Blits every object created in the current scene to the main surface
        self.scene.draw(self.screen)
        # `update` actually displays every "blitted" object on surfaces
        pygame.display.update()


if __name__ == '__main__':
    game = Game(size=(800, 600))
    game.run(fps=60)
