import numpy as np
import pygame
import charlie2.tools.events as events
from .defaults import window_size, bg_colour, default_text_colour
from .paths import fonts_path, pj, get_common_vis_stim_paths


class Screen:
    """This class creates a pygame screen, and contains attributes and methods
    necessart for drawing test, shapes and images. It has convenience functions
    for loading all stimuli prior to performing any trials, and shortcut
    functions for response images and splash messages Screen object. Much of
    this is just wrapping around pygame functions."""

    def __init__(self, _window_size=None, full=True, mouse=False):
        """Creates a new pygame window. Optionally specify the window size and
        whether to run full-screen. If full is True and no window size is given
        (default option), the screen will be set to native resolution."""

        pygame.init()
        pygame.mouse.set_visible(mouse)
        self.set_mouse = pygame.mouse.set_visible

        # containers for various things
        self.images = {}  # filename : surface
        self.zones = []  # ordered list of clickable rects

        # create display surface
        if _window_size:

            self.window = window_size

        elif full:

            info = pygame.display.Info()
            self.window = (info.current_w, info.current_h)

        else:

            self.window = window_size

        if full:

            self.screen = pygame.display.set_mode(self.window,
                                                  pygame.FULLSCREEN)

        else:

            self.screen = pygame.display.set_mode(self.window)

        # other stuff
        self.screen.fill(bg_colour)
        self.font = None
        self.font2 = None
        self.create_font()
        self.x0, self.y0 = self.screen.get_rect().center
        self.centre = self.screen.get_rect().center
        self.wordzones = {}
        self.keyzones = {}
        self.imagezones = {}
        self.update = pygame.display.update
        self.flip = pygame.display.flip
        self.kill = pygame.display.quit
        self.images_visible = False

    def create_font(self, size=36, bold=False, italic=False):
        """Creates two font objects: self.font is for explanatory text, font2
        is for test-specific text."""
        pygame.font.init()
        f = pj(fonts_path, 'ClearSans-Regular.ttf')
        self.font = pygame.font.Font(f, size, bold=bold, italic=italic)
        f = pj(fonts_path, 'ClearSans-Medium.ttf')
        self.font2 = pygame.font.Font(f, size, bold=bold, italic=italic)

    def wipe(self, r=None, update=True, prc=True, force_hide_mouse=False):
        """Wipes (fills with background colour) either the entire screen if r
        is None, or an area defined by r, which should be a pygame Rect or a
        list of Rects."""

        if force_hide_mouse is True:

            pygame.mouse.set_visible(False)

        if r:

            if not hasattr(r, '__iter__'):

                r = [r]

            for a in r:

                if prc:

                    a.center = self.x0 + a.center[0], self.y0 + a.center[1]

                self.screen.fill(bg_colour, a)

            if update:

                pygame.display.update(r)
        else:

            self.screen.fill(bg_colour)

            if update:

                pygame.display.flip()

            self.images_visible = False

    def blit_text(self, s, pos, colour=None, blit=True, update=False,
                  prc=True, font=None):
        """Blits a single line of text s to the screen at specified postion."""

        if not colour:

            colour = default_text_colour

        if not font:

            font = self.font

        q = font.render(s, True, colour)
        r = q.get_rect()

        if prc:

            r.center = self.x0 + pos[0], self.y0 + pos[1]

        else:

            r.x, r.y = pos

        if blit:

            self.screen.fill(bg_colour, r)
            self.screen.blit(q, r)

        if update:

            pygame.display.update(r)

        return q, r

    def splash(self, s, wait=True, mouse=False, clear_events=True, font=None):
        """Makes a splash screen. Typically these are used for displaying task
        instructions or demarking the begining/end of one phase of a test.
        Splashes clear all the previous content and are drawn to the centre of
        the screen. The message string s can contain multiple lines, which are
        parsed and blitted separately. Standard python line breaks (\\n) are
        handled. Can also clear events, hide/display the mouse, and wait for a
        key press to continue."""
        self.wipe()

        if not font:

            font = self.font

        if not mouse:

            pygame.mouse.set_visible(False)

        else:

            pygame.mouse.set_visible(True)

        S = s.split('\n')
        x, y = (0, 0)
        X = [x] * len(S)
        Y = [y + i * self.font.get_linesize() for i in range(len(S))]
        Y = [int(b - float(sum(Y) / float(len(Y)))) for b in Y]
        [self.blit_text(
            a, xy, update=False, font=font
        ) for a, xy in zip(S, zip(X, Y))]
        pygame.display.update()

        if wait:

            if clear_events:

                keydown = events.wait_for_keydown(clear=True)

            else:

                keydown = events.wait_for_keydown()

            if keydown == 'EXIT':

                return 'EXIT'

            else:

                return None

    def countdown_splash(self, t, s, font=None):
        """Creates a splash that counts down from a given t. The splash will
        automatically disappear when the countdown is over."""
        self.wipe()

        if not font:

            font = self.font2

        clock = pygame.time.Clock()
        current = 0

        while current < t:

            snew = s % int(round(t - current))
            self.splash(snew, mouse=False, wait=False, font=font)
            events.wait(0.98)
            current += (clock.tick_busy_loop() / 1000.)

    def blit_image(self, image, pos, blit=True, update=False, prc=True):
        """Blits a single image to the screen. 'image' can be a string
        representing the path of an image, a pygame surface, or a 2D numpy
        array."""

        if isinstance(image, str):

            image = pygame.image.load(image)
            image = image.convert_alpha()

        elif type(image) == np.ndarray:

            image = image / 2. + 0.5
            image = np.round(image * 255)
            image = image[..., None].repeat(3, -1).astype("uint64")
            image = pygame.surfarray.make_surface(image)

        r = image.get_rect()

        if prc:

            r.center = self.x0 + pos[0], self.y0 + pos[1]

        else:

            r.x, r.y = pos

        if blit:

            self.screen.fill(bg_colour, r)
            self.screen.blit(image, r)

        if update:

            pygame.display.update(r)

        return image, r

    def load_image(self, f):
        """Preloads an image at path f and adds it to the preloaded_images
        dictionary, where f is the key and the surface is the value. f can be
        a list of paths."""

        if not hasattr(f, '__iter__'):

            f = [f]

        for a in f:

            image = pygame.image.load(a)
            image = image.convert_alpha()
            self.images[a] = image

    def load_keyboard_keys(self):
        """Preloads the images of arrow keys and adds them to the images
        dictionary. Unlike load_image, this function will use the filename as
        the key in the images dict rather than the absolute path."""

        for k, v in get_common_vis_stim_paths().items():

            image = pygame.image.load(v)
            image = image.convert_alpha()
            self.images[k] = image

    def create_word_zones(self, words, spacing, y, font=None):
        """Used in experiments wherein the proband must click on words printed
        on the screen, such as the emotion recognition test. This is tricky to
        code because the clickable zones will have variable sizes depending on
        the words, and the words must be printed within those zones. To
        simplify things, this method will always space the words equally along
        the x-axis."""

        if not font:

            font = self.font2

        n = len(words)
        x0 = - int(0.5 * spacing * (n - 1))

        for i, word in enumerate(words):

            x = x0 + spacing * i
            q, r = self.blit_text(word, (x, y), default_text_colour, False,
                                  font=font)
            self.zones.append(r)
            self.wordzones[word] = (q, r)

    def create_keyboard_key_zones(self, keys, spacing, y):
        """Similar to create_word_zones but for images of keyboard keys."""
        n = len(keys)
        x0 = - int(0.5 * spacing * (n - 1))

        for i, k in enumerate(keys):

            x = x0 + spacing * i
            q, r = self.blit_image(self.images[k + '.png'], (x, y), True,
                                   False)
            self.zones.append(r)
            self.keyzones[k] = (q, r)

    def create_image_zones(self, images, spacing, y):
        """Similar to create_word_zones but for any images."""
        n = len(images)
        x0 = - int(0.5 * spacing * (n - 1))

        for i, f in enumerate(images):

            x = x0 + spacing * i
            q, r = self.blit_image(f, (x, y), True, False)
            self.zones.append(r)
            self.imagezones[f] = (q, r)

    def create_rect_zones(self, coord_list):
        """Create empty Rect zones. Coords should be a list-like with tuples
        in the format (left, top, width, height)."""

        for p in coord_list:

            r = pygame.Rect(*p)
            self.zones.append(r)

    def blit_rectangle(self, rect, fill_colour=None, border_colour=BLACK,
                       border_width=3, alpha=255, update=False):
        """Draw a rectangle with size and position determined by the pygame
        rect object. According to the pygame docs, it may be more efficient
        to use Surface objects rather than pygame.draw.rect under some
        circumstances, so this is done for filled rectangles. Alpha (for
        transparancy) is ignored for unfilled rectangles."""

        if type(rect) != pygame.Rect:

            rect = pygame.Rect(*rect)

        if fill_colour:

            s = pygame.Surface((rect.width, rect.height))
            s.set_alpha(alpha)
            s.fill(fill_colour)
            self.screen.blit(s, (rect.x, rect.y))

        if border_colour and border_width:

            pygame.draw.rect(self.screen, border_colour, rect, border_width)

        if update:

            pygame.display.update(rect)

    def blit_line(self, start, end, width, colour=None, prc=True):
        """Draw a line from start to end of width. Start and end can be rects;
        if so, the prc argument is ignored."""

        if not colour:

            colour = default_text_colour

        if type(start) is pygame.Rect and type(end) is pygame.Rect:

            start = start.center
            end = end.center
            prc = False

        if prc:

            start = self.x0 + start[0], self.y0 + start[1]
            end = self.x0 + end[0], self.y0 + end[1]

        pygame.draw.line(self.screen, colour, start, end, width)

    def update_image_zones(self, update=True):
        """Update all images within self.imagezones, and set
        self.images_visible to True."""

        if not self.images_visible:

            R = []

            for k in self.imagezones.keys():

                q, r = self.imagezones[k]
                self.screen.blit(q, r)
                R.append(r)

            if update:

                pygame.display.update(R)

            self.images_visible = True

    def change_word_colour(self, word, colour, update=False, font=None):
        """This will only work in tests with clickable word zones. Changes the
        colour of word or words to colour."""

        if not hasattr(word, '__iter__'):

            word = [word]

        if not isinstance(colour, list):

            colour = [colour]

        if len(colour) == 1:

            colour *= len(word)

        if not font:

            font = self.font2

        R = []

        for w, c in zip(word, colour):

            q, r = self.wordzones[w]
            q = font.render(w, True, c)
            self.wordzones[w] = (q, r)
            self.screen.fill(bg_colour, r)
            self.screen.blit(q, r)
            R.append(r)

        if update:

            pygame.display.update(R)

    def change_key_colour(self, key, colour, update=False, font=None):
        """This will only work in tests with clickable word zones. Changes the
        colour of word or words to colour."""

        if not hasattr(key, '__iter__'):

            key = [key]

        if not hasattr(colour, '__iter__'):

            colour = [colour]

        R = []

        for k, c in zip(key, colour):

            q, r = self.keyzones[k]
            q = self.images[k + c + '.png']
            self.keyzones[k] = (q, r)
            self.screen.fill(bg_colour, r)
            self.screen.blit(q, r)
            R.append(r)

        if update:

            pygame.display.update(R)

    def check_if_inside_clickable(self, pos):
        """Checks if the x,y coordinate was inside one of the rects within
        self.clickable_rects, and if so returns True and the Rect index."""

        for i, rect in enumerate(self.zones):

            if rect.collidepoint(pos):

                return True, i

        return False, False

    def reset_zones(self):
        """Resets predefined zones. This is useful if there is a dramatic logic
        change during a single task, such as the digit-symbol substitution
        task."""
        self.zones = []
        self.wordzones = {}
        self.keyzones = {}
        self.imagezones = {}
        self.images_visible = False

    def reset_mouse_pos(self, x=None, y=None):
        """
        Moves the mouse cursor to the centre of the screen, or another
        position.
        """
        if x is None:

            x = self.x0

        if y is None:

            y = self.y0

        pygame.mouse.set_pos((x, y))
