"""Defines a Qt widget containing convenience methods for drawing to the GUI.

"""
from copy import copy
from logging import getLogger
from typing import Tuple, List

from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtGui import QFont, QPixmap, QKeyEvent
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget

from .audiowidget import AudioWidget
from .paths import get_instructions, get_vis_stim_paths

logger = getLogger(__name__)


class VisualWidget(AudioWidget):
    def __init__(self, parent=None) -> None:
        """Visual widget.

        Not called directly. Serves as a base class for BaseTestWidget, providing
        methods for drawing to the GUI.

        """
        super(VisualWidget, self).__init__(parent)
        logger.debug(f"initialised {type(self)} with parent={parent}")

        # stimuli paths
        self.vis_stim_paths = get_vis_stim_paths(self.kwds["test_name"])

        # font widget
        self.instructions_font = QFont("Helvetica", 26)

        # instructions
        t = self.kwds["test_name"]
        l = self.kwds["language"]
        self.instructions = get_instructions(t, l)

        # zones
        self.zones = []

    def clear_screen(self, delete: bool = False) -> None:
        """Hide widgets.

        Hides and optionally deletes all children of this widget.

        Args:
            delete (:obj:`bool`, optional): Delete the widgets as well.

        """
        # for widgets  organized in a layout
        logger.debug("called clear_screen()")
        if self.layout() is not None:
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    if delete:
                        widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        # for widgets not organized
        for widget in self.children():
            if hasattr(widget, "hide"):
                widget.hide()
            if delete:
                widget.deleteLater()

    def display_instructions(self, message: str, font: QFont = None) -> QLabel:
        """Display instructions.

        This method will first hide any visible widgets (e.g., images from the last
        trial). Typically `message` is an item from the list `self.instructions`.

        Args:
            message (str): Message to display.
            font (:obj:`QFont`, optional): A font in which to display the instructions.

        Returns:
            label (QLabel): Object containing the message.

        """
        logger.debug(
            f"called display_instructions() with message={message} and font={font}"
        )
        self.clear_screen()
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        if font is None:
            label.setFont(self.instructions_font)
        else:
            label.setFont(font)
        label.resize(self.size())
        label.show()
        return label

    def display_instructions_with_continue_button(
        self, message: str, font: QFont = None, wait: bool = True
    ) -> Tuple[QLabel, QPushButton]:
        """Display instructions with a continue button.

        This is the same as `self.display_instructions` except that a continue button is
        additionally displayed. Continue buttons prevent the test from moving forward
        until pressed. Generally this is used at the beginning of blocks of trials.

        Args:
            message (str): Message to display.
            font (:obj:`QFont`, optional): A font in which to display the instructions.
            wait (:obj:`bool`, optional): Wait for a bit before enabling the continue
                button.

        Returns:
            label (QLabel): Object containing the message.
            button (QPushButton): Button.

        """
        logger.debug(
            f"called display_instructions_with_continue_button() with message={message}"
            f"and font={font}"
        )
        label = self.display_instructions(message, font)
        button = self._display_continue_button()
        logger.debug("now waiting for continue button to be pressed")
        if wait:
            if hasattr(self, "paintEvent"):
                logger.debug("temporarily disabling paint events")
                _paintEvent = copy(self.paintEvent)
                self.paintEvent = lambda _: None
            button.setEnabled(False)
            self.sleep(2 * 1000)
            button.setEnabled(True)
            if hasattr(self, "paintEvent"):
                logger.debug("reenabling paint events")
                self.paintEvent = _paintEvent
        return label, button

    def display_instructions_with_space_bar(self, message: str) -> QLabel:
        """Display instructions, allowing the space bar to continue.

        Args:
            message (str): Message to display.

        Returns:
            label (QLabel): Object containing the message.

        """
        logger.debug(
            f"called display_instructions_with_space_bar() with message={message}"
        )
        label = self.display_instructions(message)
        logger.debug("now waiting for space bar to be pressed")
        self._keyReleaseEvent = copy(self.keyReleaseEvent)
        self.keyReleaseEvent = self._space_bar_continue
        label.setFocus()
        logger.debug("what widget needs to be in focus for this to work?")
        logger.debug("self? %s" % self.hasFocus())
        logger.debug("label? %s" % label.hasFocus())
        return label

    def _space_bar_continue(self, event: QKeyEvent) -> None:
        logger.debug(f"called _space_bar_continue() with event={event}")
        logger.debug("%s pressed, looking for %s" % (event.key(), Qt.Key_Space))
        if event.key() == Qt.Key_Space:
            logger.debug("got the correct key")
            self._trial()
            self.keyReleaseEvent = self._keyReleaseEvent

    def load_image(self, s: str) -> QLabel:
        """Return an image.

        It is possibly important for correct alignment to explicitly set the size of the
        label after setting its pixmap since it does not inherit this attribute even
        though the entire pixmap may br visible.

        Args:
            s (str): Path to the .png image file.

        Returns:
            label (QLabel): Label containing the image as a pixmap.

        """
        logger.debug(f"called load_image() with s={s}")
        label = QLabel(self)
        pixmap = QPixmap(self.vis_stim_paths[s])
        label.setPixmap(pixmap)
        label.resize(pixmap.size())
        label.hide()
        return label

    def move_widget(self, widget: QWidget, pos: Tuple[int, int]) -> QRect:
        """Move `widget` to new coordinates.

        Coords are relative to the centre of the window where (1, 1) would be the upper
        right.

        Args:
            widget (QWidget): Any widget.
            pos (:obj:`tuple` of :obj:`int`): New position.

        Returns:
            g (QRect): Updated geometry of the wdiget.

        """
        logger.debug(f"called move_widget() with widget={widget} and pos={pos}")
        x = self.frameGeometry().center().x() + pos[0]
        y = self.frameGeometry().center().y() - pos[1]
        point = QPoint(x, y)
        g = widget.frameGeometry()
        g.moveCenter(point)
        widget.move(g.topLeft())
        return g

    def display_image(self, s: object, pos: object = None) -> QLabel:
        """Show an image on the screen.

        Args:
            s (:obj:`str` or :obj:`QLabel`): Path to image or an image itself.
            pos (:obj:`tuple` of :obj:`int`, optional): Coords of image.

        Returns:
            label (QLabel): Label containing the image as a pixmap.

        """
        logger.debug(f"called display_image() with s={s} and pos={pos}")
        if isinstance(s, str):
            label = self.load_image(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        logger.debug("showing %s" % s)
        return label

    def load_text(self, s: str) -> QLabel:
        """Return a QLabel containing text.

        Args:
            s (str): Text.

        Returns:
            label (QLabel): Label containing the text.

        """
        logger.debug(f"called load_text() with s={s}")
        label = QLabel(s, self)
        label.setFont(self.instructions_font)
        label.setAlignment(Qt.AlignCenter)
        label.resize(label.sizeHint())
        label.hide()
        return label

    def display_text(self, s: str, pos: object = None) -> QLabel:
        """Same as `load_text` but also display it.

        Args:
            s (:obj:`str` or :obj:`QLabel`): Text or label containing text.
            pos (:obj:`tuple` of :obj:`int`, optional): Coords.

        Returns:
            label (QLabel): Label containing the text.

        """
        logger.debug(f"called display_text() with s={s} and pos={pos}")
        if isinstance(s, str):
            label = self.load_text(s)
        else:
            label = s
        if pos:
            self.move_widget(label, pos)
        label.show()
        return label

    def load_keyboard_arrow_keys(
            self, instructions: List[str], y: int = -225
    ) -> List[QLabel]:
        """Load keyboard arrow keys.

        Args:
            instructions (list): Labels to display under the keys. Must be of length 2
                (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
                Items can be :obj:`str` or `None`. If `None`, no text is displayed.
            y (:obj:`int`, optional): Vertical position of key centres.

        Returns:
            w (:obj:`list` of :obj:`QLabel`): The created labels.

        """
        logger.debug(
            f"called load_keyboard_arrow_keys() with instructions={instructions} and "
            f"y={y}"
        )
        w = []
        lx = -75
        rx = 75
        if len(instructions) == 3:
            lx = -225
            rx = 225
        l = self.load_image("l.png")
        self.move_widget(l, (lx, y))
        l.hide()
        w.append(l)
        r = self.load_image("r.png")
        self.move_widget(r, (rx, y))
        r.hide()
        w.append(r)
        xs = [lx, rx]
        if len(instructions) == 3:
            d = self.load_image("d.png")
            self.move_widget(d, (0, y))
            d.hide()
            w.append(d)
            xs = [lx, 0, rx]
        for x, instr in zip(xs, instructions):
            if instr is not None:
                a = self.load_text(instr)
                self.move_widget(a, (x, y - 75))
                a.hide()
                w.append(a)
        return w

    def display_keyboard_arrow_keys(
            self, instructions: List[str], y: int = -225
    ) -> List[QLabel]:
        """Same as `load_keyboard_arrow_keys` except also show them.

        Args:
            instructions (list): Labels to display under the keys. Must be of length 2
                (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
                Items can be :obj:`str` or `None`. If `None`, no text is displayed.
            y (:obj:`int`, optional): Vertical position of key centres.

        Returns:
            w (:obj:`list` of :obj:`QLabel`): The created labels.

        """
        logger.debug(
            f"called display_keyboard_arrow_keys() with instructions={instructions} and"
            f" y={y}"
        )
        widgets = self.load_keyboard_arrow_keys(instructions, y)
        [w.show() for w in widgets]
        return widgets

    def make_zones(self, rects: List[QRect], reset: bool = True) -> None:
        """Update `self.zones`.

        `self.zones` contains areas of the window (`QRect` objects) that can be
    pressed.

        Args:
            rects (:obj:`list` of :obj:`QRect`): List of `QRects`.
            reset (:obj:`bool`, optional): Remove old items.

        """
        logger.debug("called make_zones()")
        if reset:
            self.zones = []
        for rect in rects:
            self.zones.append(rect)

    def _display_continue_button(self) -> QPushButton:
        """Display a continue button."""
        logger.debug("called _display_continue_button()")
        button = QPushButton(self.instructions[1], self)
        button.setFont(self.instructions_font)
        size = (button.sizeHint().width() + 20, button.sizeHint().height() + 20)
        button.resize(*size)
        button.clicked.connect(self._continue_button_pressed)
        x = (self.frameGeometry().width() - button.width()) // 2
        y = self.frameGeometry().height() - (button.height() + 20)
        button.move(x, y)
        button.show()
        return button

    def display_trial_continue_button(self, wait: bool = True) -> None:
        """The button is connected to _next_trial instead of _trial."""
        logger.debug("called display_trial_continue_button()")
        button = self._display_continue_button()
        button.clicked.disconnect()
        if wait:
            if hasattr(self, "paintEvent"):
                logger.debug("temporarily disabling paint events")
                _paintEvent = copy(self.paintEvent)
                self.paintEvent = lambda _: None
            button.setEnabled(False)
            self.sleep(2 * 1000)
            button.setEnabled(True)
            if hasattr(self, "paintEvent"):
                logger.debug("reenabling paint events")
                self.paintEvent = _paintEvent
        button.clicked.connect(self._next_trial)

    def _continue_button_pressed(self) -> None:
        """Continue to next trial."""
        logger.debug("called _continue_button_pressed()")
        self._trial()

    def display_countdown(self, t: int = 5, s: int = 1000) -> None:
        """Display the countdown timer."""
        logger.debug("called display_countdown()")
        for i in range(t):
            self.display_instructions(self.instructions[0] % (t - i))
            self.sleep(s)
