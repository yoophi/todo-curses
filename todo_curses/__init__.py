import configparser
import curses
import curses.textpad
import random
import sys
from pathlib import Path

from appdirs import user_config_dir

__version__ = '0.1.0'

from dataclasses import dataclass

from faker import Faker

basic_config = """
[global]
name = 
"""

logo_text = (
    ' _            _           ',
    '| |_ ___   __| | ___  ___ ',
    '| __/ _ \ / _` |/ _ \/ __|',
    '| || (_) | (_| | (_) \__ \\',
    ' \__\___/ \__,_|\___/|___/',
)

logo_w = max([len(item) for item in logo_text])
logo_h = len(logo_text) + 1


@dataclass
class Todo:
    id: int
    text: str
    done: bool


class TodoApi:
    def __init__(self):
        self.faker = Faker()
        self.index = 0
        self.todos = []
        for n in range(int(random.random() * 100) + 30):
            todo = Todo(
                id=n,
                text=self.faker.sentence(),
                done=(random.random() > 0.8),
            )
            self.todos.append(todo)

    @property
    def total(self):
        return len(self.todos)


class TodoScreen:
    def __init__(self, name):
        super().__init__()

        self.api = TodoApi()
        self.todo_offset = 0
        self.item_per_page = 0

        self.scr_h, self.scr_w = 0, 0
        self.cursor_x, self.cursor_y = 3, 8
        self.cursor_min_y, self.cursor_max_y = 8, 0
        self.screen = curses.initscr()
        self.win = None
        self.init_curses()

        self.name = name

    # def setup_input(self):
    #     inp = curses.newwin(8, 55, 0, 0)
    #     inp.addstr(1, 1, "Please enter your username:")
    #     sub = inp.subwin(2, 1)
    #     sub.border()
    #     sub2 = sub.subwin(3, 2)
    #     tb = curses.textpad.Textbox(sub2)
    #     inp.refresh()

    def run(self):
        self.assess_screen()

        while True:
            self.screen.clear()
            self.draw_frame()
            self.screen.refresh()

            c = self.screen.getch()

            # inp = curses.newwin(8, 55, 0, 0)
            # inp.addstr(1, 1, "Please enter your username:")
            # sub = inp.subwin(2, 1)
            # sub.border()
            # sub2 = sub.subwin(3, 2)
            # tb = curses.textpad.Textbox(sub2)
            # inp.refresh()
            # val = tb.edit(enter_is_terminate)

            # self.screen.addstr(3, 3, val)

            # v = self.setup_input()

            if c in [27, int(b"q"[0])]:  # ESC, q
                raise KeyboardInterrupt

            if c in [int(b"x"[0])]:  # x
                self.api.todos[self.todo_offset + self.api.index].done = not self.api.todos[self.todo_offset + self.api.index].done

            if c in [curses.KEY_DOWN, b"j"[0]]:
                if self.cursor_y >= self.cursor_max_y:
                    if self.todo_offset < self.api.total - self.item_per_page:
                        self.todo_offset += 1

                    continue
                self.cursor_y += 1
                self.api.index += 1
                self.reset_cursor_pos()
            elif c in [curses.KEY_UP, b"k"[0]]:
                if self.cursor_y <= self.cursor_min_y:
                    if self.todo_offset > 0:
                        self.todo_offset -= 1
                    continue
                self.cursor_y -= 1
                self.api.index -= 1
                self.reset_cursor_pos()

    def init_curses(self):
        curses.noecho()
        curses.mousemask(1)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        self.screen.keypad(True)

    def assess_screen(self):
        self.scr_h, self.scr_w = self.screen.getmaxyx()
        self.cursor_max_y = self.scr_h - 3

    def draw_frame(self):
        header = " Todo ('q' or Ctrl+C to exit) "

        nlines = self.scr_h - logo_h
        ncols = self.scr_w
        self.item_per_page = (nlines - 4)

        w = 13
        self.screen.addstr(0, 0, 'Version: ', curses.color_pair(2))
        self.screen.addstr(0, w, __version__, curses.color_pair(1))

        self.screen.addstr(1, 0, 'Total: ', curses.color_pair(2))
        self.screen.addstr(1, w, str(self.api.total), curses.color_pair(1))

        self.screen.addstr(2, 0, 'Index: ', curses.color_pair(2))
        self.screen.addstr(2, w, str(self.api.index), curses.color_pair(1))

        self.screen.addstr(3, 0, 'ItemPerPage: ', curses.color_pair(2))
        self.screen.addstr(3, w, str(self.item_per_page), curses.color_pair(1))
        self.screen.addstr(4, 0, (
            f'c_min_y: {self.cursor_min_y}, c_max_y: {self.cursor_max_y} '
            f'todo_offset: {self.todo_offset} '
        ))

        for n, line in enumerate(logo_text):
            self.screen.addstr(n, self.scr_w - logo_w, line, curses.color_pair(2))

        self.win = self.screen.subwin(nlines, ncols, self.scr_h - nlines, 0)
        self.win.border()
        self.win.addstr(0, 2, header)
        self.win.refresh()

        for n, item in enumerate(self.api.todos[self.todo_offset:self.todo_offset + self.item_per_page]):
            filled_text = f"[{'x' if item.done else ' '}] {item.id:04d} {item.text}".ljust(self.scr_w - 4)
            if n == self.api.index:
                self.win.addstr(n + 2, 2, filled_text, curses.color_pair(3))
            else:
                self.win.addstr(n + 2, 2, filled_text)

        self.reset_cursor_pos()

    def reset_cursor_pos(self):
        self.screen.move(self.cursor_y, self.cursor_x)
        # self.win.move(self.cursor_y, self.cursor_x)
        # self.box.move(self.cursor_y, self.cursor_x)


def main():
    config_dir = Path(user_config_dir("todo"))
    config_file = config_dir / "todo.conf"
    if not config_dir.exists():
        config_dir.mkdir(parents=True)

    if not config_file.exists():
        with config_file.open("w") as fh:
            fh.write(basic_config)

    config = configparser.ConfigParser()
    config.read(config_file.as_posix())

    name = config.get("global", "name", fallback="")

    if name == "":
        raise RuntimeError(f"Fill name in {config_file}")

    try:
        screen = TodoScreen(name)
        screen.run()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        curses.endwin()


if __name__ == "__main__":
    main()
