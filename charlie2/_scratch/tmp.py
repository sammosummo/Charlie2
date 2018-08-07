
# if no_trials_left is True:
#
#     logger.debug("remaining_trials is empty, test must be completed")
#     self.data["test_completed"] = True
#
#
#
#
# if self.data["current_trial"] is None:
#
#     logger.debug("there is no current trial; must be start of a new session")
#
#
#
# # no remaining trials
# if len(self.data["remaining_trials"]) == 0:
#     logger.debug("remaining_trials is empty, test must be completed")
#     self.data["test_completed"] = True
#     logger.debug("is there an orphaned current_trial?")
#     if self.data["current_trial"] is not None:
#         logger.debug("yes, appending to completed_trials")
#         self._append_current_trial()
#     self.update()
#     raise StopIteration
#
# # some remaining trials
# # no current trial
# if self.data["current_trial"] is None:
#     logger.debug("no current_trial, so popping new one from remaining_trials")
#     self.data["current_trial"] = Trial(self.data["remaining_trials"].pop(0))
#
# # there is a current trial
# else:
#     logger.debug("there is a current_trial; what is it?")
#     logger.debug("current_trial is a %s" % str(type(self.data["current_trial"])))
#
#     if isinstance(self.data["current_trial"], Trial):
#         logger.debug("must have been created in this session, so appending")
#         self._append_current_trial()
#         logger.debug("and popping new one from remaining_trials")
#         self.data["current_trial"] = Trial(self.data["remaining_trials"].pop(0))
#
#     elif isinstance(self.data["current_trial"], dict):
#         logger.debug("must have been loaded from file, so using it")
#         self.data["current_trial"] = Trial(self.data["current_trial"])
#
# self.update()
#
# logger.debug("current_trial looks like %s" % str(self.data["current_trial"]))
# logger.debug("should this trial be skipped?")
#
# # recursively skip
# if self.data["current_trial"].status == "skipped":
#     logger.debug("yes, so recursively iterating")
#     return self.__next__()
#
# # no skip
# else:
#     logger.debug("no, so returning current_trial")
#     return self.data["current_trial"]

# def _append_current_trial(self):
#     """Append current_trial to completed_trials, if there is indeed a current_trial
#     and it is not already at the bottom of completed_trials.
#
#     """
#     logger.debug("attempting to append to current_trial to completed_trials")
#     ct = self.data["current_trial"]
#     # if ct.status != "skipped":
#     #     logger.debug("setting status of current_trial to completed")
#     #     ct.status = "completed"
#     # else:
#     #     logger.debug("preserving status of current_trial as skipped")
#     if len(self.data["completed_trials"]) > 0:
#         if dict(ct) == self.data["completed_trials"][-1]:
#             logger.debug("current_trial is last item in completed_trials already")
#             return
#     logger.debug("current_trial is not on completed_trials, so appending")
#     self.data["completed_trials"].append(vars(ct))
#
# def save_completed_trials_as_csv(self):
#     """Output the list of dicts as a csv."""
#     df = pd.DataFrame(self.data["completed_trials"])
#     try:
#         df.set_index("trial_number", inplace=True)
#     except KeyError:
#         logger.warning("No trial_number in data frame, no trials yet?")
#     df.dropna(axis=1, how="all", inplace=True)
#     df.to_csv(self.data["csv"])
#     self.update()
#
# def save_summary(self):
#     """Save the summary as a csv"""
#     pd.Series(self.data["summary"]).to_csv(self.data["summary_path"])
#     self.update()
#
# def skip_current_trial(self, reason):
#     """Set the current trial to skipped."""
#     t = self.data["current_trial"]
#     t.status = "skipped"
#     t.reason_skipped = reason
#
# def skip_current_block(self, reason):
#     """Set all trials in remaining_trials in the current block, including
#     current_trial, to skipped.
#
#     """
#     logger.debug("current_trial type: %s" % str(type(self.data["current_trial"])))
#     b = self.data["current_trial"].block_number
#     logger.debug("current block number: %s" % str(b))
#     self.skip_current_trial(reason)
#     for i, t in enumerate(self.data["remaining_trials"]):
#         logger.debug("trial %s" % str(t))
#         if "block_number" in t:
#             if t["block_number"] == b:
#                 self.data["remaining_trials"][i]["status"] = "skipped"
#                 self.data["remaining_trials"][i]["reason_skipped"] = reason
#         else:
#             self.data["remaining_trials"][i]["status"] = "skipped"
#             self.data["remaining_trials"][i]["reason_skipped"] = reason
#         logger.debug("trial %s" % str(t))


#
# def _block(self):
#     """Runs at the start of a new block of trials.
#
#     Typically blocks are used to delineate trials of a different condition, when new
#     instructions are often needed."""
#     logger.debug("called _block()")
#     self._performing_block = False
#     logger.debug("checking if this is a silent block")
#
#     # new block
#     if self.silent_block:
#         logger.debug("this is indeed a silent block")
#         logger.debug("skipping the countdown")
#         self.skip_countdown = True
#         logger.debug("running _trial()")
#         self._trial()
#
#     # "silent" block (don't do anything special)
#     else:
#         logger.debug("this is a not a silent block")
#         logger.debug("running block()")
#         self.block()
#
# def block(self):
#     """Override this method."""
#     raise AssertionError("block must be overridden")
#
# def _trial(self):
#     """Runs at the start of a new trial.
#
#     Displays the countdown if first in a new block, checks if very last trial, flags
#     the fact that a trial is in progress, updates the results list.
#
#     """
#     logger.debug("called _trial()")
#     t = self.procedure.data["current_trial"]
#     logger.debug("current trial looks like %s" % str(dict(t)))
#     if t.first_trial_in_block and not self.skip_countdown:
#         logger.debug("countdown requested")
#         self.display_countdown()
#     self.repaint()
#     if self.procedure.data["current_trial"].first_trial_in_block is True:
#         logger.debug("this is the first trial in a new block")
#         self.performing_block = True
#     self.performing_trial = True
#     self.trial()
#
# def safe_close(self):
#     """Safely clean up and save the data at the end of the test."""
#     logger.debug("called safe_close()")
#
#     # properly ended test
#     if self.procedure.data["test_completed"] is True:
#         logger.debug("saving a csv of the completed trials")
#         self.procedure.save_completed_trials_as_csv()
#         logger.debug("trying to summarise performance on the test")
#         summary = self.summarise()
#         logger.debug("updating data object to include summary")
#         self.procedure.data["summary"] = summary
#         self.procedure.save()
#         logger.debug("saving the summary")
#         self.procedure.save_summary()
#
#     # early quit
#     else:
#         self.procedure.save()
#         logger.debug("no trials completed, so don't try to summarise")
#
#     # end test
#     logger.debug("all done, so switching the central widget")
#     self.parent().switch_central_widget()
#
#
#
# def trial(self):
#     """Override this method."""
#     raise AssertionError("trial must be overridden")
#
# def summarise(self):
#     """Override this method."""
#     raise AssertionError("summarise must be overridden")
#
# def mousePressEvent_(self, event):
#     """Override this method."""
#     pass
#
# def keyReleaseEvent_(self, event):
#     """Override this method."""
#     pass
#
# def sleep(self, t):
#     """Sleep for `t` ms.
#
#     Use instead of `time.sleep()` or any other method of sleeping because (a) Qt
#     handles it properly and (b) it prevents a `closeEvent` from quitting the test
#     during this time.
#
#     Args:
#         t (float): Time to sleep in seconds.
#
#     """
#     logger.debug(f"called sleep with t={t}")
#     self.parent().ignore_close_event = True
#     loop = QEventLoop()
#     QTimer.singleShot(t, loop.quit)
#     loop.exec_()
#     self.parent().ignore_close_event = False
#
# def display_instructions(self, message, font=None):
#     """Display instructions.
#
#     This method will first hide any visible widgets (e.g., images from the last
#     trial). Typically `message` is an item from the list `self.instructions`.
#
#     Args:
#         message (str): Message to display.
#         font (:obj:`QFont`, optional): A font in which to display the instructions.
#
#     Returns:
#         label (QLabel): Object containing the message.
#
#     """
#     logger.debug(
#         f"called display_instructions() with message={message} and font={font}"
#     )
#     self.clear_screen()
#     label = QLabel(message, self)
#     label.setAlignment(Qt.AlignCenter)
#     if font is None:
#         label.setFont(self.instructions_font)
#     else:
#         label.setFont(font)
#     label.resize(self.size())
#     label.show()
#     return label
#
# def display_instructions_with_continue_button(self, message, font=None, wait=True):
#     """Display instructions with a continue button.
#
#     This is the same as `self.display_instructions` except that a continue button is
#     additionally displayed. Continue buttons prevent the test from moving forward
#     until pressed. Generally this is used at the beginning of blocks of trials.
#
#     Args:
#         message (str): Message to display.
#         font (:obj:`QFont`, optional): A font in which to display the instructions.
#         wait (:obj:`bool`, optional): Wait for a bit before enabling the continue
#         button.
#
#     Returns:
#         label (QLabel): Object containing the message.
#         button (QPushButton): Button.
#
#     """
#     logger.debug(
#         f"called display_instructions_with_continue_button() with message={message}"
#         f"and font={font}"
#     )
#     label = self.display_instructions(message, font)
#     button = self._display_continue_button()
#     logger.debug("now waiting for continue button to be pressed")
#     if wait:
#         if hasattr(self, "paintEvent"):
#             logger.debug("temporarily disabling paint events")
#             _paintEvent = copy(self.paintEvent)
#             self.paintEvent = lambda _: None
#         button.setEnabled(False)
#         self.sleep(2 * 1000)
#         button.setEnabled(True)
#         if hasattr(self, "paintEvent"):
#             logger.debug("reenabling paint events")
#             self.paintEvent = _paintEvent
#     return label, button
#
# def display_instructions_with_space_bar(self, message):
#     """Display instructions, allowing the space bar to continue.
#
#     Args:
#         message (str): Message to display.
#
#     Returns:
#         label (QLabel): Object containing the message.
#
#     """
#     logger.debug(
#         f"called display_instructions_with_space_bar() with message={message}"
#     )
#     label = self.display_instructions(message)
#     logger.debug("now waiting for space bar to be pressed")
#     self._keyReleaseEvent = copy(self.keyReleaseEvent)
#     self.keyReleaseEvent = self._space_bar_continue
#     label.setFocus()
#     logger.debug("what widget needs to be in focus for this to work?")
#     logger.debug("self? %s" % self.hasFocus())
#     logger.debug("label? %s" % label.hasFocus())
#     return label
#
# def _space_bar_continue(self, event):
#     logger.debug(f"called _space_bar_continue() with event={event}")
#     logger.debug("%s pressed, looking for %s" % (event.key(), Qt.Key_Space))
#     if event.key() == Qt.Key_Space:
#         logger.debug("got the correct key")
#         self._trial()
#         self.keyReleaseEvent = self._keyReleaseEvent
#
# def load_image(self, s):
#     """Return an image.
#
#     It is possibly important for correct alignment to explicitly set the size of the
#     label after setting its pixmap since it does not inherit this attribute even
#     though the entire pixmap may br visible.
#
#     Args:
#         s (str): Path to the .png image file.
#
#     Returns:
#         label (QLabel): Label containing the image as a pixmap.
#
#     """
#     logger.debug(f"called load_image() with s={s}")
#     label = QLabel(self)
#     pixmap = QPixmap(self.vis_stim_paths[s])
#     label.setPixmap(pixmap)
#     label.resize(pixmap.size())
#     label.hide()
#     return label
#
# def move_widget(self, widget, pos):
#     """Move `widget` to new coordinates.
#
#     Coords are relative to the centre of the window where (1, 1) would be the upper
#     right.
#
#     Args:
#         widget (QWidget): Any widget.
#         pos (:obj:`tuple` of :obj:`int`): New position.
#
#     Returns:
#         g (QRect): Updated geometry of the wdiget.
#
#     """
#     logger.debug(f"called move_widget() with widget={widget} and pos={pos}")
#     x = self.frameGeometry().center().x() + pos[0]
#     y = self.frameGeometry().center().y() - pos[1]
#     point = QPoint(x, y)
#     g = widget.frameGeometry()
#     g.moveCenter(point)
#     widget.move(g.topLeft())
#     return g
#
# def display_image(self, s, pos=None):
#     """Show an image on the screen.
#
#     Args:
#         s (:obj:`str` or :obj:`QLabel`): Path to image or an image itself.
#         pos (:obj:`tuple` of :obj:`int`, optional): Coords of image.
#
#     Returns:
#         label (QLabel): Label containing the image as a pixmap.
#
#     """
#     logger.debug(f"called display_image() with s={s} and pos={pos}")
#     if isinstance(s, str):
#         label = self.load_image(s)
#     else:
#         label = s
#     if pos:
#         self.move_widget(label, pos)
#     label.show()
#     logger.debug("showing %s" % s)
#     return label
#
# def load_text(self, s):
#     """Return a QLabel containing text.
#
#     Args:
#         s (str): Text.
#
#     Returns:
#         label (QLabel): Label containing the text.
#
#     """
#     logger.debug(f"called load_text() with s={s}")
#     label = QLabel(s, self)
#     label.setFont(self.instructions_font)
#     label.setAlignment(Qt.AlignCenter)
#     label.resize(label.sizeHint())
#     label.hide()
#     return label
#
# def display_text(self, s, pos=None):
#     """Same as `load_text` but also display it.
#
#     Args:
#         s (:obj:`str` or :obj:`QLabel`): Text or label containing text.
#         pos (:obj:`tuple` of :obj:`int`, optional): Coords.
#
#     Returns:
#         label (QLabel): Label containing the text.
#
#     """
#     logger.debug(f"called display_text() with s={s} and pos={pos}")
#     if isinstance(s, str):
#         label = self.load_text(s)
#     else:
#         label = s
#     if pos:
#         self.move_widget(label, pos)
#     label.show()
#     return label
#
# def load_keyboard_arrow_keys(self, instructions, y=-225):
#     """Load keyboard arrow keys.
#
#     Args:
#         instructions (list): Labels to display under the keys. Must be of length 2
#             (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
#             Items can be :obj:`str` or `None`. If `None`, no text is displayed.
#         y (:obj:`int`, optional): Vertical position of key centres.
#
#     Returns:
#         w (:obj:`list` of :obj:`QLabel`): The created labels.
#
#     """
#     logger.debug(
#         f"called load_keyboard_arrow_keys() with instructions={instructions} and "
#         f"y={y}"
#     )
#     w = []
#     lx = -75
#     rx = 75
#     if len(instructions) == 3:
#         lx = -225
#         rx = 225
#     l = self.load_image("l.png")
#     self.move_widget(l, (lx, y))
#     l.hide()
#     w.append(l)
#     r = self.load_image("r.png")
#     self.move_widget(r, (rx, y))
#     r.hide()
#     w.append(r)
#     xs = [lx, rx]
#     if len(instructions) == 3:
#         d = self.load_image("d.png")
#         self.move_widget(d, (0, y))
#         d.hide()
#         w.append(d)
#         xs = [lx, 0, rx]
#     for x, instr in zip(xs, instructions):
#         if instr is not None:
#             a = self.load_text(instr)
#             self.move_widget(a, (x, y - 75))
#             a.hide()
#             w.append(a)
#     return w
#
# def display_keyboard_arrow_keys(self, instructions, y=-225):
#     """Same as `load_keyboard_arrow_keys` except also show them.
#
#     Args:
#         instructions (list): Labels to display under the keys. Must be of length 2
#             (left- and right-arrow keys) or 3 (left-, down-, and right-array keys).
#             Items can be :obj:`str` or `None`. If `None`, no text is displayed.
#         y (:obj:`int`, optional): Vertical position of key centres.
#
#     Returns:
#         w (:obj:`list` of :obj:`QLabel`): The created labels.
#
#     """
#     logger.debug(
#         f"called display_keyboard_arrow_keys() with instructions={instructions} and"
#         f" y={y}"
#     )
#     widgets = self.load_keyboard_arrow_keys(instructions, y)
#     [w.show() for w in widgets]
#     return widgets
#
# def make_zones(self, rects, reset=True):
#     """Update `self.zones`.
#
#     `self.zones` contains areas of the window (`QRect` objects) that can be pressed.
#
#     Args:
#         rects (:obj:`list` of :obj:`QRect`): List of `QRects`.
#         reset (:obj:`bool`, optional): Remove old items.
#
#     """
#     logger.debug("called make_zones()")
#     if reset:
#         self.zones = []
#     for rect in rects:
#         self.zones.append(rect)
#
# def clear_screen(self, delete=False):
#     """Hide widgets.
#
#     Hides and optionally deletes all children of this widget.
#
#     Args:
#         delete (:obj:`bool`, optional): Delete the widgets as well.
#
#     """
#     # for widgets  organized in a layout
#     logger.debug("called clear_screen()")
#     if self.layout() is not None:
#         while self.layout().count():
#             item = self.layout().takeAt(0)
#             widget = item.widget()
#             if widget is not None:
#                 widget.hide()
#                 if delete:
#                     widget.deleteLater()
#             else:
#                 self.clearLayout(item.layout())
#     # for widgets not organized
#     for widget in self.children():
#         if hasattr(widget, "hide"):
#             widget.hide()
#         if delete:
#             widget.deleteLater()
#
# def basic_summary(self, **kwds):
#     """Returns an basic set of summary statistics.
#
#     Kwds:
#         trials (:obj:`list`, optional): List of trials to analyse. If not passed,
#             all trials are used.
#         adjust (:obj:`bool`, optional): Calculated "adjusted" time taken if not all
#             trials were completed before a timeout event.
#
#     Returns:
#         dic (dict): dictionary of results.
#
#     """
#     logger.debug("called basic_summary()")
#     if "trials" not in kwds:
#         total_trials = self.procedure.data["completed_trials"]
#     else:
#         total_trials = kwds["trials"]
#     total_trials = [t for t in total_trials if not t["practice"]]
#     completed_trials = [t for t in total_trials if t["status"] == "completed"]
#     skipped_trials = [t for t in total_trials if t["status"] == "skipped"]
#     first_trial = total_trials[0]
#
#     dic = {
#         "total_trials": len(total_trials),
#         "completed_trials": len(completed_trials),
#         "skipped_trials": len(skipped_trials),
#     }
#
#     try:
#
#         correct_trials = [t for t in completed_trials if t["correct"]]
#         rt_correct_ms = [t["trial_time_elapsed_ms"] for t in correct_trials]
#         dic["correct_trials"] = len(correct_trials)
#
#         if len(completed_trials) > 0:
#
#             dic["accuracy"] = len(correct_trials) / len(completed_trials)
#
#         if len(completed_trials) > 0 and len(correct_trials) > 0:
#
#             last_trial = completed_trials[-1]
#             dic["began_timestamp"] = str(first_trial["timestamp"])
#             dic["duration_ms"] = last_trial["block_time_elapsed_ms"]
#             dic["total_duration_ms"] = last_trial["test_time_elapsed_ms"]
#             dic["total_duration_min"] = dic["total_duration_ms"] / 60 / 1000
#             dic["finished_timestamp"] = str(last_trial["timestamp"])
#             dic["mean_rt_correct_ms"] = sum(rt_correct_ms) / len(rt_correct_ms)
#
#             if "adjust" in kwds:
#                 all_rts = [t["trial_time_elapsed_ms"] for t in completed_trials]
#                 mean_rt = sum(all_rts) / len(all_rts)
#                 est_extra_time = mean_rt * len(skipped_trials)
#                 dic["duration_ms_adjusted"] = dic["duration_ms"] + est_extra_time
#         else:
#
#             dic["began_timestamp"] = None
#             dic["duration_ms"] = None
#             dic["total_duration_ms"] = None
#             dic["finished_timestamp"] = None
#             dic["mean_rt_correct_ms"] = 0
#             dic["total_duration_min"] = 0
#
#             if "adjust" in kwds:
#                 dic["duration_ms_adjusted"] = None
#
#     except KeyError:
#
#         if len(completed_trials) > 0:
#
#             last_trial = completed_trials[-1]
#             dic["began_timestamp"] = str(first_trial["timestamp"])
#             dic["duration_ms"] = last_trial["block_time_elapsed_ms"]
#             dic["total_duration_ms"] = last_trial["test_time_elapsed_ms"]
#             dic["total_duration_min"] = dic["total_duration_ms"] / 60 / 1000
#             dic["finished_timestamp"] = str(last_trial["timestamp"])
#
#         else:
#
#             dic["began_timestamp"] = None
#             dic["duration_ms"] = None
#             dic["total_duration_ms"] = None
#             dic["finished_timestamp"] = None
#             dic["mean_rt_correct_ms"] = 0
#             dic["total_duration_min"] = 0
#
#     if "prefix" in kwds:
#         p = kwds["prefix"] + "_"
#         dic = {p + k: v for k, v in dic.items() if "total_duration" not in k}
#
#     return dic
#
# def _display_continue_button(self):
#     """Display a continue button."""
#     logger.debug("called _display_continue_button()")
#     button = QPushButton(self.instructions[1], self)
#     button.setFont(self.instructions_font)
#     size = (button.sizeHint().width() + 20, button.sizeHint().height() + 20)
#     button.resize(*size)
#     button.clicked.connect(self._continue_button_pressed)
#     x = (self.frameGeometry().width() - button.width()) // 2
#     y = self.frameGeometry().height() - (button.height() + 20)
#     button.move(x, y)
#     button.show()
#     return button
#
# def display_trial_continue_button(self, wait=True):
#     """The button is connected to _next_trial instead of _trial."""
#     logger.debug("called display_trial_continue_button()")
#     button = self._display_continue_button()
#     button.clicked.disconnect()
#     if wait:
#         if hasattr(self, "paintEvent"):
#             logger.debug("temporarily disabling paint events")
#             _paintEvent = copy(self.paintEvent)
#             self.paintEvent = lambda _: None
#         button.setEnabled(False)
#         self.sleep(2 * 1000)
#         button.setEnabled(True)
#         if hasattr(self, "paintEvent"):
#             logger.debug("reenabling paint events")
#             self.paintEvent = _paintEvent
#     button.clicked.connect(self._next_trial)
#
# def _continue_button_pressed(self):
#     """Continue to next trial."""
#     logger.debug("called _continue_button_pressed()")
#     self._trial()
#
# def display_countdown(self, t=5, s=1000):
#     """Display the countdown timer."""
#     logger.debug("called display_countdown()")
#     for i in range(t):
#         self.display_instructions(self.instructions[0] % (t - i))
#         self.sleep(s)
#
#
#
# def _add_timing_details(self):
#     """Gathers some details about the current state from the various timers."""
#     logger.debug("called _add_timing_details()")
#     dic = {
#         "test_time_elapsed_ms": self.test_time.elapsed(),
#         "block_time_elapsed_ms": self.block_time.elapsed(),
#         "trial_time_elapsed_ms": self.trial_time.elapsed(),
#         "test_time_left_ms": self._test_time_left,
#         "block_time_left_ms": self._time_left_in_block,
#         "trial_time_left_ms": self._time_left_in_trial,
#         "test_time_up_ms": self._test_time_up,
#         "block_time_up_ms": self._block_time_up,
#         "trial_time_up_ms": self._trial_time_up,
#     }
#     self.procedure.data["current_trial"].update(dic)
#
# def mousePressEvent(self, event):
#     """Overridden from `QtWidget`."""
#     logger.debug(f"called mousePressEvent() with event={event}")
#     if self.performing_trial:
#         self.mousePressEvent_(event)
#         self._add_timing_details()
#         t = self.procedure.data["current_trial"]
#         if t.status == "completed":
#             logger.debug("current_trial was completed successfully")
#             logger.debug("(final version) of current_trial looks like %s" % str(t))
#             # if t.practice is True:
#             #     self.play_feedback_sound(t.correct)
#             self._next_trial()
#
# def keyReleaseEvent(self, event):
#     """Overridden from `QtWidget`."""
#     logger.debug(f"called keyReleaseEvent() with event={event}")
#     if self.performing_trial:
#         self.keyReleaseEvent_(event)
#         self._add_timing_details()
#         t = self.procedure.data["current_trial"]
#         if self.procedure.data["current_trial"].status == "completed":
#             logger.debug("current_trial was completed successfully")
#             logger.debug("(final version) of current_trial looks like %s" % str(t))
#             # if t.practice is True:
#             #     self.play_feedback_sound(t.correct)
#             self._next_trial()
#
# def _next_trial(self):
#     """Moves on to the next trial."""
#     logger.debug("called _next_trial()")
#     self.performing_trial = False
#     logger.debug("saving a csv of the completed trials")
#     self.procedure.save_completed_trials_as_csv()
#     self._step()
#
# def next_trial(self):
#     """Moves on to the next trial (public version)."""
#     logger.debug("called next_trial()")
#     self._next_trial()
#
# def _trial_timeout(self):
#     """End a trial early because it had timed out."""
#     logger.debug("called _trial_timeout()")
#     self.procedure.skip_current_trial("timeout")
#     self._next_trial()
#
# def _block_timeout(self):
#     """End a trial early because it had timed out."""
#     logger.debug("called _block_timeout()")
#     self.procedure.skip_current_block("timeout")
#     self._next_trial()
#
# def _block_stopping_rule(self):
#     """Apply block stopping rule.
#
#     This is a little complicated. Because `self.data.data["completed_trials"]` gets
#     updated when the data object is iterated, the old trial does not get appended to
#     this list until the next one has already started. Stopping rules should be
#     called before this iteration, yet should evaluate all completed trials.
#     Therefore we temporarily edit completed_trials to include current_trial
#     (actually the old trial, but we are in-between trials at this point). This
#     is almost certainly not the best way to do this, but I don't have the time to
#     restructure everything to fix it.
#
#     """
#     logger.debug("called _block_stopping_rule()")
#     already_completed = self.procedure.data["test_completed"]
#     if already_completed:
#         return False
#     if self.procedure.data["current_trial"] is not None:
#         current_trial = dict(self.procedure.data["current_trial"])
#         old_completed_trials = copy(self.procedure.data["completed_trials"])
#         self.procedure.data["completed_trials"].append(current_trial)
#         result = self.block_stopping_rule()
#         self.procedure.data["completed_trials"] = old_completed_trials
#     else:
#         result = self.block_stopping_rule()
#     return result
#
# def block_stopping_rule(self):
#     """Override this method."""
#     return False
#
# def _block_stop(self):
#     """End a trial early because stopping rule passed."""
#     logger.debug("called _block_stop")
#     self.procedure.skip_current_block("stopping rule failed")

# def _preload_feedback_sounds(self):
#     """This should prevent lags when playing sounds."""
#     for name in ["incorrect.wav", "correct.wav"]:
#         sound = QSoundEffect()
#         sound.setSource(QUrl.fromLocalFile(self.aud_stim_paths[name]))
#         self.feedback_sounds.append(sound)
#
# def play_feedback_sound(self, correct):
#     """Play either the correct sound if true or incorrect sound if false."""
#     self.feedback_sounds[correct].play()











