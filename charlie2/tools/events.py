import pygame


def wait(t):
    """Just waits (literally does nothing) for t seconds."""
    pygame.event.pump()
    pygame.time.wait(int(t * 1000))


def wait_for_keydown(escape=True, clear=False):
    """Idles until a key is pressed. Optionally kills python if it detects
    Esc. Returns the event and the length of time since the function was
    called."""

    if clear is True:

        pygame.event.clear()

    pygame.event.set_allowed(None)
    pygame.event.set_allowed(pygame.KEYDOWN)
    clock = pygame.time.Clock()
    clock.tick_busy_loop()

    while 1:

        event = pygame.time.wait()

        if escape and event.key == pygame.K_ESCAPE:

            return 'EXIT'

        else:

            return event, clock.tick_busy_loop()


def poll_for_valid_keydown(valid_responses, check_type, escape=True):
    """Polls the event list for a keydown with a key in valid_responses. This
    is useful in tasks where trials are time-limited. Returns None each time
    no response is found. Note that this function does not return reaction
    times: those should be recorded in the loop that calls this function."""

    try:

        event = pygame.event.poll()

    except:

        return None

    if event.type == pygame.KEYDOWN:

        if escape and event.key == pygame.K_ESCAPE:

            return 'EXIT'

        if check_type == 'unicode' and event.unicode in valid_responses:

            return event.unicode

        if check_type == 'key' and event.key in valid_responses:

            return event.key

    else:

        return None


def wait_for_valid_keydown(valid_responses, check_type, escape=True):
    """Idles until a valid key is pressed. Requires a list of possible
    responses and whether those are unicodes or pygame keys. Optionally kills
    python if it detects Esc."""

    while 1:

        keydown = wait_for_keydown(escape)

        if keydown == 'EXIT':

            return 'EXIT'

        else:

            event, rt =  keydown

        if check_type == 'unicode' and event.unicode in valid_responses:

            return event.unicode, rt

        if check_type == 'key' and event.key in valid_responses:

            return event.key, rt


def wait_for_arrowkey(labels=None):
    """A specific variety of valid_keydown check that returns the arrowkey
    label. If the argument is omitted or None, the default is to assume the
    labels are yes/no."""

    if not labels:

        labels = ['Yes', 'No']

    keys = {pygame.K_LEFT: labels[0], pygame.K_RIGHT: labels[1]}
    key, rt = wait_for_valid_keydown(keys.keys(), 'key')
    return keys[key], rt


def wait_for_mouse_click(escape=True, clear=False):
    """Idles until the mouse is clicked. Optionally kills python if it detects
    Esc."""
    pygame.mouse.set_visible(True)

    if clear:

        pygame.event.clear()

    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])
    clock = pygame.time.Clock()
    clock.tick_busy_loop()

    while 1:

        event = pygame.event.wait()

        if event.type == pygame.KEYDOWN:

            if escape and event.key == pygame.K_ESCAPE:

                return 'EXIT'
        else:

            return event, clock.tick_busy_loop()


def wait_for_valid_mouse_click(screen, button, escape=True, clear=False):
    """
    Idles until a mouse click is made within a valid zone. 'zones' is a list
    of pygame Rects. Returns the zone index, the clicked rect itself, and the
    rt.
    """
    valid = False
    while not valid:
        mouse_click = wait_for_mouse_click(escape)
        if mouse_click == 'EXIT':
            return 'EXIT'
        else:
            event, rt =  mouse_click
        if button is not None and event.button == button:
            valid, i = screen.check_if_inside_clickable(event.pos)
        if button is None:
            valid, i = screen.check_if_inside_clickable(event.pos)
    if button is not None:
        return i, rt
    else:
        return i, rt, event.button


def poll_for_valid_mouse_click(screen, button, escape=True):
    """Polls the event list for a mouse click within a valid zone. This
    is useful in tasks where trials are time-limited. Returns None each time
    no response is found. Note that this function does not return reaction
    times: those should be recorded in the loop that calls this function."""
    pygame.mouse.set_visible(True)

    if pygame.event.get_blocked(pygame.MOUSEBUTTONDOWN):

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    try:

        event = pygame.event.poll()

    except:

        return None

    if event.type == pygame.KEYDOWN:

        if escape and event.key == pygame.K_ESCAPE:

            return 'EXIT'

    if event.type == pygame.MOUSEBUTTONDOWN:

        if event.button == button:

            valid, i = screen.check_if_inside_clickable(event.pos)

            if valid:

                return i

        else:

            return None
