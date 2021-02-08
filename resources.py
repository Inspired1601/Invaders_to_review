import pygame
import os


class Image:
    """Loads image from file and provides surface.  
    Also encapsulates conversion to pygame's inner format  
    to speed up blitting (drawing images on surface)  
    and other methods neccesary for proper image loading.
    """
    def __init__(self, filename, width=0, height=0):
        self.img = self.load(filename)
        self.convert()
        self.scale(width, height)
        self.mask = self.get_mask()

    def load(self, filename):
        """Loads image from almost any file.
        .png, .jpg, .bmp, .tiff and many others
        formats are supported.

        Args:
            filename (str)
        """
        path = os.path.join('img', filename)
        try:
            img = pygame.image.load(path)
        except FileNotFoundError:
            # If file not found, just create an orange surface
            # instead of image.
            # Then treat this surface like a regular image,
            # including convertation and creating a mask.
            print(f'Can not open file {path}.')
            img = pygame.Surface((1, 1))
            img.fill(pygame.Color('orange'))

        return img

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

        # If both arguments were passed
        # we should scale image to the given size
        # even if the initial aspect ratio will be broken
        if width and height:
            new_size = width, height

        # But if only 1 argument passed
        # we scale image to the given width/height
        # maintaining the initial aspect ratio
        elif width or height: 
            new_size = self._calculate_size_keeping_aspect_ratio(width, height)

        self.img = pygame.transform.scale(self.img, new_size)

    def _calculate_size_keeping_aspect_ratio(self, width, height):
        old_size = self.img.get_size()
        aspect_ratio = old_size[0] / old_size[1]

        if width:
            new_size = (width, int(width / aspect_ratio))
        else:
            new_size = (int(height * aspect_ratio), height)

        return new_size

    def get_mask(self):
        """Creates a mask from surface.
        `mask` is an array of opaque pixels.
        We will need it to calculate pixel-perfect collisions later.
        """
        return pygame.mask.from_surface(self.img)


class ResourceManager:
    """Loads images and sounds
    which are needed for every scene in the game.  
    Stores all resources in dictionaries `sounds` and `images`.
    """
    def __init__(self):
        self.sounds = self.load_sounds()
        self.images = self.load_images()

    def load_sounds(self):
        """Loads sounds from files using `pygame.Sound` class.

        Raises:
            pygame.error: if file not found, just prints a message.
        """
        if not pygame.mixer.get_init():
            raise pygame.error('pygame.mixer is not initialized.')

        sounds = {}
        sound_names = ['ost', 'shot', 'explosion', 'warning', 'beep', 'no_energy']

        for sound in sound_names:
            path = os.path.join('sounds', f'{sound}.mp3')
            try:
                sounds[sound] = pygame.mixer.Sound(path)
            except FileNotFoundError:
                print(f'Ошибка при загрузке аудио: {sound}.mp3')

        return sounds

    def load_images(self):
        """Loads images from files
        and stores them into a dictionary.
        """
        screen_width, screen_height = pygame.display.get_window_size()
        images = {}
        # Background should be stretched to the whole screen
        images['bg'] = Image('BG.jpg', screen_width, screen_height)
        images['player'] = Image('Ship1.png', screen_width / 16)
        images['enemy'] = Image('UFO.png', screen_width / 16)
        images['projectile'] = Image('Laser.png', screen_width / 70)
        images['explosion'] = Image('Explosion.png', screen_width / 8)

        return images
