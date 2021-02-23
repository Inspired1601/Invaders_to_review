import pygame


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
        self.surface = font.render(message, True, color)
        # Calculating size and position
        self.rect = self.surface.get_rect()

    def draw(self, surface):
        """Shortcut for `surface.blit(self.surface, self.rect)

        Args:
            surface (pygame.Surface)
        """
        surface.blit(self.surface, self.rect)

    def change_color(self, color):
        """Re-renders text with new color.

        Args:
            color (Tuple[int], pygame.Color): RGB color
        """
        self.surface = self.font.render(self.message, True, color)

    def change_message(self, message):
        """Re-renders text with new message.

        Args:
            message (str)
        """
        self.surface = self.font.render(message, True, self.color)
        self.rect.width = self.surface.get_rect().width
        # Don't reassign `self.rect` with `self.obj.get_rect()`,
        # because it will reset position (rect.x, rect.y).
        # Just change width to resize rect for new text.


class Menu:
    def __init__(self, start_index):
        self.width, self.height = pygame.display.get_window_size()
        self.index = start_index

        self.create_fonts()
        self.create_font_colors()
        self.create_text_objects()

    def create_fonts(self):
        self.header_font = pygame.font.SysFont('calibri', 72)
        self.menu_font = pygame.font.SysFont('calibri', 36)

    def create_font_colors(self):
        self.HEADER_COLOR = pygame.Color('red')
        self.ACTION_COLOR = pygame.Color('white')
        self.MENU_ITEM_COLOR = pygame.Color('white')
        self.SELECTED_MENU_ITEM_COLOR = pygame.Color('yellow')

    def create_text_objects(self):
        header = Text('Space Invaders', self.header_font, self.HEADER_COLOR)
        action = Text('Выберите сложность:', self.header_font, self.ACTION_COLOR)
        menu_item_0 = Text('Легко', self.menu_font, self.MENU_ITEM_COLOR)
        menu_item_1 = Text('Нормально', self.menu_font, self.MENU_ITEM_COLOR)
        menu_item_2 = Text('Сложно', self.menu_font, self.MENU_ITEM_COLOR)

        header.rect.center = (self.width / 2, self.height / 3)
        action.rect.midtop = (self.width / 2, header.rect.bottom + 60)
        menu_item_1.rect.midtop = (self.width / 2, action.rect.bottom + 60)
        menu_item_0.rect.topright = (menu_item_1.rect.left - 50, action.rect.bottom + 60)
        menu_item_2.rect.topleft = (menu_item_1.rect.right + 50, action.rect.bottom + 60)

        self.header_text = header
        self.action_text = action
        self.menu_items = (menu_item_0, menu_item_1, menu_item_2)

        # Change color of selected menu item
        self.menu_items[self.index].change_color(self.SELECTED_MENU_ITEM_COLOR)

    def switch(self, direction):
        if direction == -1 and self.index > 0:
            self.index -= 1
            self.menu_items[self.index].change_color(self.SELECTED_MENU_ITEM_COLOR)
            self.menu_items[self.index + 1].change_color(self.MENU_ITEM_COLOR)
        elif direction == 1 and self.index < 2:
            self.index += 1
            self.menu_items[self.index].change_color(self.SELECTED_MENU_ITEM_COLOR)
            self.menu_items[self.index - 1].change_color(self.MENU_ITEM_COLOR)

        return self.index

    def draw(self, surface):
        """Draws all text objects of menu.

        Args:
            surface (Window)
        """
        surface.blit(self.header_text.obj, self.header_text.rect)
        surface.blit(self.action_text.obj, self.action_text.rect)
        for menu_item in self.menu_items:
            surface.blit(menu_item.obj, menu_item.rect)


class LabelPanel:
    """Creates and manages a group of text objects.  
    These object will appear in the top left corner of the screen.

    Example:
        labels = LabelPanel(3)
        labels.update(f'{self.FPS}', f'{self.score}', f'{self.lives}')
        labels.draw(surface)
    """
    def __init__(self, label_amount):
        """Create a LabelPanel to handle `label_amount` labels.

        Args:
            label_amount (int): amount of labels in the panel.
        """
        self.labels = []
        self.font = pygame.font.SysFont('calibri', 24)
        self.color = pygame.Color('white')

        line_height = self.font.get_height()    # Height of a text line with vertical space included
        for i in range(label_amount):
            label = Text('', self.font, self.color)
            label.rect.left = 10
            label.rect.top = 10 + line_height * i

            self.labels.append(label)

    def update(self, new_labels):
        """Updates text in every label.
        Also recalculates `rect` attribute
        according to the new text.

        Args:
            new_labels (Tuple[str], List[str])

        Raises:
            IndexError: raises error if `new_labels`
                        has different length than `self.labels`
        """
        len_new = len(new_labels)
        len_old = len(self.labels)
        if len_new != len_old:
            raise IndexError(f'The lengths of the label lists do not match: expected {len_old}, got {len_old} items.')

        for (old_label, new_label_text) in zip(self.labels, new_labels):
            old_label.change_message(new_label_text)

    def draw(self, surface):
        """Draws every label in it's own place.

        Args:
            surface (Window)
        """
        for label in self.labels:
            label.draw(surface)


class EnergyBar:
    """Energy bar in the left bottom corner of the screen.

    Bar consists of 2 parts: outer bar (immutable)
    and inner bar, which width is changing according to
    the remaining energy.
    """
    def __init__(self, size, max_energy):
        self.size = size
        self.create_bars()

        self.max_energy = max_energy
        self.max_inner_width = self.inner_bar.rect.width

    def update(self, energy):
        """Changes width of inner bar according to
        the remaining energy.
        For example, `self.update(500)` when
        `self.max_energy == 1000` will lead to
        shrinking inner bar width to 50% of initial.

        Args:
            energy (int)
        """
        current_energy_pct = energy / self.max_energy
        self.inner_bar.rect.width = self.max_inner_width * current_energy_pct

        if current_energy_pct > 0.7:
            self.inner_bar.color = pygame.Color('green')
        elif current_energy_pct > 0.3:
            self.inner_bar.color = pygame.Color('yellow')
        else:
            self.inner_bar.color = pygame.Color('red')

    def draw(self, surface):
        """Draws outer and inner bars in corresponding rects.

        Args:
            surface (Window):
        """
        # Using pygame.draw.rect to dynamically draw rect with changing size
        self.outer_bar.draw(surface)
        self.inner_bar.draw(surface)

    def create_bars(self):
        """Creates 2 bars - `inner_bar` and `outer_bar`.
        Each bar is an instance of `Bar` class.
        """
        outer_bar_color = pygame.Color('gray')
        inner_bar_color = pygame.Color('green')

        outer_size = self.size
        inner_size = (outer_size[0] - 6, outer_size[1] - 6)
        screen_height = pygame.display.get_window_size()[1]

        outer_rect = pygame.Rect((0, 0), outer_size)
        inner_rect = pygame.Rect((0, 0), inner_size)

        outer_rect.bottomleft = (10, screen_height - 10)
        inner_rect.centery = outer_rect.centery
        inner_rect.left = outer_rect.left + 3

        self.inner_bar = Bar(inner_rect, inner_bar_color)
        self.outer_bar = Bar(outer_rect, outer_bar_color)


class Bar:
    """Creates a bar of a specified size and color.  
    """
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color

    def draw(self, surface):
        """Draw a bar.

        Args:
            surface (Window)
        """
        pygame.draw.rect(surface, self.color, self.rect)
