import pygame
import os


class Text:
    """Encapsulates the functionality needed to work with text objects.  
    In Pygame text object itself is just a Surface.  
    To create such a surface you need to call a `render()`  
    method from font object.

    After rendering text object is immutable,  
    so in order to change text or color you must re-render  
    this object with new parameters.
    """
    def __init__(self, message, font, color):
        # We need to save initial arguments,
        # because if we'll want to change color or message,
        # we'll need to re-render the whole object
        self.message = message
        self.font = font
        self.color = color

        # Creating a surface
        self.obj = font.render(message, True, color)
        # Calculating size and position
        self.rect = self.obj.get_rect()

    def draw(self, surface):
        """Shortcut for `surface.blit(self.obj, self.rect)

        Args:
            surface (pygame.Surface)
        """
        surface.blit(self.obj, self.rect)

    def change_color(self, color):
        """Re-renders text with new color.

        Args:
            color (Tuple[int], pygame.Color): RGB color
        """
        self.obj = self.font.render(self.message, True, color)

    def change_message(self, message):
        """Re-renders text with new message.

        Args:
            message (str)
        """
        self.obj = self.font.render(message, True, self.color)
        self.rect.width = self.obj.get_rect().width
        # Don't reassign `self.rect` with `self.obj.get_rect()`,
        # because it will reset position (rect.x, rect.y).
        # Just change width to resize rect for new text.


class Image:
    """Loads image from file and provides surface.  
    Also encapsulates conversion to pygame's inner format  
    to speed up blitting (drawing images on surface)  
    and other methods neccesary for proper image loading.
    """
    def __init__(self, filename, width=0, height=0):
        self.load(filename)
        self.convert()
        self.scale(width, height)
        self.get_mask()

    def load(self, filename):
        """Loads image from almost any file.
        .png, .jpg, .bmp, .tiff and many others
        formats are supported.

        Args:
            filename (str)
        """
        path = os.path.join('img', filename)
        try:
            self.img = pygame.image.load(path)
        except FileNotFoundError:
            # If file not found, just create an orange surface
            # instead of image.
            # Then treat this surface like a regular image,
            # including convertation and creating a mask.
            print(f'Can not open file {path}.')
            self.img = pygame.Surface((1, 1))
            self.img.fill(pygame.Color('orange'))

    def convert(self):
        """Converts image (array of pixels) into pygame's inner format,
        which blits on other surfaces much faster than regular images.
        """
        if self.img.get_alpha():
            self.img = self.img.convert_alpha()
        else:
            self.img = self.img.convert()

    def scale(self, width, height):
        """Scales image.
        If both arguments is passed - doesn't care about aspect ratio.
        If only one argument is passed - maintains initial aspect ratio.

        Args:
            width (int)
            height (int)
        """
        width = int(width)
        height = int(height)

        if width == 0 and height == 0:      # 0's are default values
            return

        # If both arguments were passed
        # we should scale image to the given size
        # even if the initial aspect ratio will be broken
        elif width != 0 and height != 0:
            self.img = pygame.transform.scale(self.img, (width, height))

        # But if only 1 argument passed
        # we scale image to the given width/height
        # maintaining the initial aspect ratio
        else:
            old_size = self.img.get_size()
            wh_ratio = old_size[0] / old_size[1]

            if width == 0:
                new_size = (int(height * wh_ratio), height)
            else:
                new_size = (width, int(width / wh_ratio))

            self.img = pygame.transform.scale(self.img, new_size)

    def get_mask(self):
        """Creates a mask from surface.
        `mask` is an array of opaque pixels.
        We will need it to calculate pixel-perfect collisions later.
        """
        self.mask = pygame.mask.from_surface(self.img)


class ResourceManager:
    """Loads images and sounds
    which are needed for every scene in the game.  
    Stores all resources in dictionaries `sounds` and `images`.
    """
    def __init__(self):
        self.load_sounds()
        self.load_images()

    def load_sounds(self):
        """Loads sounds from files using `pygame.Sound` class.

        Raises:
            pygame.error: if file not found, just prints a message.
        """
        if not pygame.mixer.get_init():
            raise pygame.error('pygame.mixer is not initialized.')

        self.sounds = {}
        sound_names = ['ost', 'shot', 'explosion', 'warning', 'beep', 'no_energy']
        for sound in sound_names:
            path = os.path.join('sounds', f'{sound}.mp3')
            try:
                self.sounds[sound] = pygame.mixer.Sound(path)
            except FileNotFoundError:
                print(f'Ошибка при загрузке аудио: {sound}.mp3')

    def load_images(self):
        """Loads images from files
        and stores them into a dictionary.
        """
        screen_width, screen_height = pygame.display.get_window_size()
        self.images = {}
        # Background should be stretched to the whole screen
        self.images['bg'] = Image('BG.jpg', screen_width, screen_height)
        self.images['player'] = Image('Ship1.png', 50)  # 50 px width
        self.images['enemy'] = Image('UFO.png', 50)
        self.images['projectile'] = Image('Laser.png', 12)
        self.images['explosion'] = Image('Explosion.png', 100)
