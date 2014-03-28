"""Version two of the debugger
"""

import curses

from synacor.pubsub import PubSub

class Application(object):

    @property
    def screen(self):
        return self._screen

    @screen.setter
    def screen(self, screen):
        self._screen = screen

    @property
    def output_buffer(self):
        if self._output_buffer is None:
            self._output_buffer = OutputBuffer()
        return self._output_buffer

    @output_buffer.setter
    def output_buffer(self, output_buffer):
        self._output_buffer = output_buffer

    @property
    def pubsub(self):
        if self._pubsub is None:
            self._pubsub = PubSub()
        return self._pubsub

    @pubsub.setter
    def pubsub(self, pubsub):
        self.pubsub = pubsub

    def __init__(self, screen=None, output_buffer=None):
        self._screen = screen
        self._output_buffer = output_buffer
        self._dimensions = (0, 0)

        self.pubsub.subscribe(event='output', func=self.output)

    def run(self):
        try:
            self.init_curses()

            output_buffer_window = curses.newwin(height=int(self.get_window_height()/2),
                                                 width=int(self.get_window_width()/2))
            output_buffer_window.border(0)
            self.output_buffer.window = output_buffer_window

            while True:
                self.output_buffer.update()
                
        except Exception as e:
            print e
        finally:
            self.shutdown_curses()

    def output(self, ch):
        self.output_buffer.append(ch)

    def init_curses(self):
        if self.screen is None:
            self.screen = curses.initscr()
            self._dimensions = self.get_window_dimensions()

    def shutdown_curses(self, *args, **kwargs):
        curses.endwin(*args, **kwargs)

    def disable_echo(self, *args, **kwargs):
        curses.noecho(*args, **kwargs)

    def enable_echo(self, *args, **kwargs):
        curses.echo(*args, **kwargs)

    def disable_cbreak(self, *args, **kwargs):
        curses.nocbreak(*args, **kwargs)

    def enable_cbreak(self, *args, **kwargs):
        curses.cbreak(*args, **kwargs)

    def enable_keypad(self):
        self.screen.keypad(1)

    def disable_keypad(self):
        self.screen.keypad(0)

    def start_color(self):
        curses.start_color()

    def get_window_dimensions(self):
        return self.screen.getmaxyx()

    def get_window_width(self):
        return self._dimensions[1]

    def get_window_height(self):
        return self._dimensions[0]

class OutputBuffer(object):

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, buffer):
        self._buffer = buffer

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, window):
        self._window = window

    def __init__(self, window=None, buffer=None):
        self._window = window or None
        self._buffer = buffer or None
        self.dirty = False

    def update(self):
        if self.dirty:
            self.dirty = False
            self.window.refresh()

    def append(self, ch):
        if ord(ch) == 10:  # newline
            self.window.insertln()
        else:
            self.window.insch(ch)

        self.dirty = True
