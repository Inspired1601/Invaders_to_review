import random

import pygame

from constants import EVENT_SPAWN_ENEMY, EVENT_ENEMY_BREACH, EVENT_PLAYER_DEAD
from resources import Text
from sprites import SpriteManager
from widgets import Menu, LabelPanel, EnergyBar


class Scene:
    """A base class for every scene in the game.  
    """
    def __init__(self, resources):
        """Creates a scene.

        Args:
            resources (ResourceManager): contains images, sounds and screen info.
        """
        self.width, self.height = pygame.display.get_window_size()
        self.resources = resources
        self.next_scene = self

    def handle_event(self, event):
        """Will be overrided in subclasses.
        """
        pass

    def update(self):
        """Will be overrided in subclasses.
        """
        pass

    def draw(self, surface):
        """Will be overrided in subclasses.
        """
        pass


class MenuScene(Scene):
    def __init__(self, resources):
        super().__init__(resources)
        self.index = 1          # 3 menu items: 0, 1, 2

        pygame.mixer.stop()     # Stop music playback

        self.menu = Menu(self.index)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keypress(event.key)

    def handle_keypress(self, key):
        # If one of the valid keys is pressed, then play the `beep` sound.
        if key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN):
            self.resources.sounds['beep'].play()

        if key == pygame.K_LEFT:
            self.index = self.menu.switch(-1)   # Move to 1 step left
        elif key == pygame.K_RIGHT:
            self.index = self.menu.switch(1)    # Move to 1 step right
        elif key in (pygame.K_SPACE, pygame.K_RETURN):
            self.next_scene = MainScene(self.resources, self.index)     # `index` is difficulty

    def draw(self, surface):
        self.menu.draw(surface)


class MainScene(Scene):
    def __init__(self, resources, difficulty):
        super().__init__(resources)
        self.clock = pygame.time.Clock()        # Uses to measure FPS

        # Setting up basic game parameters.
        self.setup_params(difficulty)
        self.score = 0
        self.last_shot_time = 0

        # Creating sprites
        self.sprites = SpriteManager(self.params, self.resources)
        self.player = self.sprites.create_player()

        # Creating widgets
        self.labels = LabelPanel(3)
        self.energy_bar = EnergyBar(
            size=(100, 20), 
            max_energy=self.player.max_energy
            )

        # Starting background processes
        self.resources.sounds['ost'].play(-1)   # -1 means `loop indefinitely`
        self.sprites.set_enemy_spawn_timer()

    def handle_event(self, event):
        # EVENT_SPAWN_ENEMY is emitted by timer approximately every 1.5 seconds (depends on difficulty)
        if event.type == EVENT_SPAWN_ENEMY:
            self.sprites.create_enemy()
            self.sprites.set_enemy_spawn_timer()    # Re-setting the timer to add a factor of randomness.
        # EVENT_ENEMY_BREACH is emitted by enemy when it reached bottom screen border.
        elif event.type == EVENT_ENEMY_BREACH:
            self.handle_enemy_breach()
        # EVENT_ENEMY_BREACH is emitted when lives become <= 0.
        elif event.type == EVENT_PLAYER_DEAD:
            self.next_scene = FinalScene(self.resources, self.sprites)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_scene = MenuScene(self.resources)

    def update(self):
        self.clock.tick()           # To measure FPS

        # Handles `long` keypresses, which can't be conveniently handled via events 
        # due to event's `only once happened` nature.
        self.handle_pressed_keys()
        self.handle_collisions()

        self.sprites.update()
        self.energy_bar.update(self.player.energy)
        self.labels.update((
            f'Lives: {self.params["player_lives"]}',
            f'Score: {self.score}',
            f'FPS: {int(self.clock.get_fps())}'
            ))

    def draw(self, surface):
        """Calls `draw` methods for every object in the scene.

        Args:
            surface (Window):
        """
        self.sprites.draw(surface)
        self.labels.draw(surface)
        self.energy_bar.draw(surface)

    # This section is about handling some in-game events, like keypress, collisions etc
    def shoot(self):
        """Fires a projectile from player's ship.
        Whether the player can shoot depends on 2 factors.
        1: >= 100 ms elapsed since the last shot.
        2: Player has enough energy to fire.
        """
        current_time = pygame.time.get_ticks()
        can_shoot = current_time - self.last_shot_time > self.params['player_cooldown']
        can_shoot = can_shoot and self.player.energy >= self.params['shoot_cost']

        if can_shoot:
            self.sprites.create_projectile()
            self.last_shot_time = current_time
            self.player.energy -= self.params['shoot_cost']

    def handle_pressed_keys(self):
        # Get current state of every key of keyboard as a list of values.  
        # Value for every key is True if pressed, otherwise False.
        pressed = pygame.key.get_pressed()
        directions = {
            pygame.K_LEFT: 'left',
            pygame.K_RIGHT: 'right',
            pygame.K_UP: 'up',
            pygame.K_DOWN: 'down'
        }
        for key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
            if pressed[key]:                        # If one of arrow keys is pressed
                self.player.move(directions[key])   # Move player's ship in a corresponding direction

        if pressed[pygame.K_SPACE]:
            self.shoot()

    def handle_collisions(self):
        """Handles 2 types of collisions:
        1. Between player's ship and enemies.
        2. Between projectiles and enemies.
        """
        damage, score = self.sprites.handle_player_collisions()
        score += self.sprites.handle_projectiles_collisions()

        self.score += score
        self.damage_player(damage)

    def handle_enemy_breach(self):
        """Handles situation when enemy reaches bottom of the screen.
        """
        self.damage_player(1)

        if self.params['player_lives'] > 0:
            self.resources.sounds['warning'].play()

    # This section is for secondary service functions
    def setup_params(self, difficulty):
        """Sets up game parameters, such as lives, energy etc.
        Concrete values depends on difficulty.
        """
        self.params = {}

        if difficulty == 0:
            self.params = {
                'player_lives': 5,
                'player_velocity': 5,
                'player_cooldown': 100,
                'player_energy': 600,

                'spawn_timer_min': 1500,
                'spawn_timer_max': 2000,
                'enemy_velocity': 1,

                'projectile_velocity': 5,
                'shoot_cost': 30
            }
        elif difficulty == 1:
            self.params = {
                'player_lives': 3,
                'player_velocity': 5,
                'player_cooldown': 100,
                'player_energy': 550,

                'spawn_timer_min': 1300,
                'spawn_timer_max': 1800,
                'enemy_velocity': 1,

                'projectile_velocity': 5,
                'shoot_cost': 35
            }
        elif difficulty == 2:
            self.params = {
                'player_lives': 1,
                'player_velocity': 5,
                'player_cooldown': 100,
                'player_energy': 400,

                'spawn_timer_min': 1200,
                'spawn_timer_max': 1600,
                'enemy_velocity': 2,

                'projectile_velocity': 5,
                'shoot_cost': 40
            }

    def damage_player(self, amount):
        """Deals `amount` of damage to player.
        If player become dead - emits EVENT_PLAYER_DEAD.

        Args:
            amount (int):
        """
        self.params['player_lives'] -= amount

        if self.params['player_lives'] <= 0:
            self.sprites.create_explosion(self.player)
            pygame.event.post(pygame.event.Event(EVENT_PLAYER_DEAD))


class FinalScene(Scene):
    """`You lose` text and fast flying enemies.
    Needs sprites from previous scene.
    """
    def __init__(self, resources, sprites):
        """
        Args:
            resources (ResourceManager)
            sprites (SpriteManager)
        """
        super().__init__(resources)

        self.sprites = sprites
        self.remove_player_ship()
        self.change_enemies_velocity(10)
        self.sprites.set_enemy_spawn_timer(200)

        self.create_lose_text()      

    def handle_event(self, event):
        if event.type == EVENT_SPAWN_ENEMY:
            self.sprites.create_enemy()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.next_scene = MenuScene(self.resources)

    def update(self):
        self.sprites.update()

    def draw(self, surface):
        self.sprites.draw(surface)
        self.text.draw(surface)

    def remove_player_ship(self):
        self.sprites.player_group.sprite.kill()

    def change_enemies_velocity(self, velocity):
        for enemy in self.sprites.enemies:
            enemy.velocity = velocity
        self.sprites.params['enemy_velocity'] = velocity

    def create_lose_text(self):
        font = pygame.font.SysFont('calibri', 72)
        self.text = Text('You lose!', font, pygame.Color('red'))
        self.text.rect.center = (self.width / 2, self.height / 2)
