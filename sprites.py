import random

import pygame

from constants import EVENT_SPAWN_ENEMY, EVENT_ENEMY_BREACH


class Sprite(pygame.sprite.Sprite):
    """A base class for every sprite in the game.

    Sprite is 2-dimensional image,
    moving across the screen during the game.  
    pygame.sprite.Sprite provides useful features
    like grouping sprites and searching for collisions
    between groups.
    """
    def __init__(self, img, pos, params):
        """Creates a sprite from image.

        Args:
            img (Image): instance of Image class, contains surface and mask.
            pos (Tuple[int]): initial position of sprite.
            params (dict): in-game parameters like player velocity, screen size etc.
                `params` is initialized when a scene is created
                and then passed to every sprite created within that scene.
        """
        super().__init__()
        self.image = img.img
        self.mask = img.mask
        self.rect = img.img.get_rect()

        self.rect.center = pos
        self.params = params


class Player(Sprite):
    """Player's ship.
    """
    def __init__(self, img, pos, params):
        super().__init__(img, pos, params)

        self.screen_width, self.screen_height = pygame.display.get_window_size()
        self.velocity = params['player_velocity']
        # These parameters determine whether the ship can currently fire.
        self.cooldown = params['player_cooldown']
        self.max_energy = self.energy = params['player_energy']

    def update(self):
        """This method is called by sprite.Group.update(),
        which updates every sprite in the group.  
        This call occurs in every iteration of main loop.
        """
        self.energy = min(self.max_energy, self.energy + 1)

    def move(self, direction):
        """This method is called by scene
        when one of the specified keys is pressed.

        Args:
            direction (str): 'up', 'down', 'left' or 'right'
        """
        if direction not in ('up', 'down', 'left', 'right'):
            raise KeyError('Invalid direction.')

        if direction == 'up' and self.rect.top > self.velocity:
            self.rect.y -= self.velocity
        elif direction == 'down' and self.rect.bottom < self.screen_height - self.velocity:
            self.rect.y += self.velocity
        elif direction == 'left' and self.rect.left > self.velocity:
            self.rect.x -= self.velocity
        elif direction == 'right' and self.rect.right < self.screen_width - self.velocity:
            self.rect.x += self.velocity


class Projectile(Sprite):
    """A projectile that automatically moves
    to the top of the screen.
    """
    def __init__(self, img, pos, params):
        super().__init__(img, pos, params)
        self.velocity = params['projectile_velocity']

    def update(self):
        if self.rect.y > self.velocity:
            self.rect.y -= self.velocity
        else:
            self.kill()


class Enemy(Sprite):
    """An UFO that automatically moves
    to the bottom of the screen.
    """
    def __init__(self, img, pos, params):
        super().__init__(img, pos, params)
        self.velocity = params['enemy_velocity']

        self.screen_width, self.screen_height = pygame.display.get_window_size()
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width

    def update(self):
        if self.rect.bottom < self.screen_height:
            self.rect.y += self.velocity
        else:
            self.kill()
            # Emits event to tell scene that this enemy reached bottom screen border.
            pygame.event.post(pygame.event.Event(EVENT_ENEMY_BREACH))


class Explosion(Sprite):
    """Self-destroys after 100 ms.
    """
    def __init__(self, img, pos, params):
        super().__init__(img, pos, params)
        self.start_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.start_time > 100:
            self.kill()


class SpriteManager:
    def __init__(self, params, resources):
        self.params = params
        self.resources = resources
        self.screen_width, self.screen_height = pygame.display.get_window_size()

        # Groups are very useful for controlling sprites and finding collisions between them.
        self.create_sprite_groups()

    def create_sprite_groups(self):
        self.player_group = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.explosion = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group()

    # This section is about creating instances of game objects (ship, projectiles etc).
    # Methods like `create_X` are not only creating object, but also add them 
    # to the corresponding groups and carry out all the accompanying actions.
    def create_player(self):
        player = Player(
            self.resources.images['player'],
            (self.screen_width / 2, self.screen_height - 30),
            self.params
        )
        player.add(self.player_group, self.sprites)
        return player

    def create_enemy(self):
        enemy = Enemy(
            self.resources.images['enemy'],
            (random.randint(0, self.screen_width), 0),
            self.params
        )
        enemy.add(self.enemies, self.sprites)
        return enemy

    def create_projectile(self):
        projectile = Projectile(
            self.resources.images['projectile'],
            self.player_group.sprite.rect.midtop,
            self.params
        )
        projectile.add(self.projectiles, self.sprites)
        self.resources.sounds['shot'].play()
        return projectile

    def create_explosion(self, ship):
        explosion = Explosion(
            self.resources.images['explosion'],
            ship.rect.center,
            self.params
        )
        explosion.add(self.sprites)
        self.resources.sounds['explosion'].play()
        return explosion

    # Collisions detection
    def handle_player_collisions(self):
        score = 0
        player_damage = 0

        collisions = pygame.sprite.groupcollide(
            self.player_group, 
            self.enemies, 
            False, 
            True, 
            pygame.sprite.collide_mask
        )

        if collisions:
            self.create_explosion(self.player_group.sprite)
            for enemy in collisions[self.player_group.sprite]:
                self.create_explosion(enemy)
                player_damage += 1
                score += 1

        return player_damage, score

    def handle_projectiles_collisions(self):
        score = 0

        collisions = pygame.sprite.groupcollide(
            self.projectiles, 
            self.enemies, 
            True, 
            True, 
            pygame.sprite.collide_mask
        )
        if collisions:
            for projectile in collisions:
                for enemy in collisions[projectile]:
                    self.create_explosion(enemy)
                    score += 1

        return score

    # Service methods
    def update(self):
        self.sprites.update()

    def draw(self, surface):
        self.sprites.draw(surface)

    def set_enemy_spawn_timer(self, ms=0):
        if not ms:
            timeout = random.randint(self.params['spawn_timer_min'], self.params['spawn_timer_max'])
        else:
            timeout = ms

        pygame.time.set_timer(EVENT_SPAWN_ENEMY, timeout)
