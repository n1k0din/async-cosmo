import asyncio
import curses
import itertools
import time
from collections import namedtuple
from pathlib import Path
from random import choice, randint
from statistics import median

import curses_tools
from fire import fire_shot
from space_garbage import fly_garbage

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = '+*.:@^'
MAX_FIRST_LAG = 50
NUM_OF_STARS = 100

Star = namedtuple('Star', 'row column symbol first_lag')


def read_frames_from_files(paths: list[str]) -> list[str]:
    """Read text files to list of strings."""
    return [Path(path).read_text() for path in paths]


def generate_random_star(
    max_height: int,
    max_width: int,
    padding: int = 1,
    star_symbols: str = STAR_SYMBOLS,
    max_first_lag: int = MAX_FIRST_LAG,
) -> Star:
    """Returns Star with random parameters."""
    row = randint(padding, max_height - padding)
    column = randint(padding, max_width - padding)
    symbol = choice(star_symbols)
    lag = randint(0, max_first_lag)
    return Star(row, column, symbol, lag)


async def wait_ticks(num_of_ticks: int) -> None:
    """sleep(n) for asyncio."""
    for _ in range(num_of_ticks):
        await asyncio.sleep(0)


async def draw_rocket(
    canvas: curses.window,
    start_row: int,
    start_column: int,
    rocket_frames: list[str],
    speed: int = 1,
) -> None:
    """Draws animated rocket by the specified coordinates."""
    height, width = canvas.getmaxyx()

    row = start_row
    column = start_column

    for frame in itertools.cycle(rocket_frames):

        rocket_rows, rocket_columns = curses_tools.get_frame_size(frame)

        rows_direction, columns_direction, _space_pressed = curses_tools.read_controls(canvas)

        row = int(median([1, row + speed * rows_direction, height - rocket_rows - 1]))
        column = int(median([1, column + speed * columns_direction, width - rocket_columns - 1]))

        curses_tools.draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        curses_tools.draw_frame(canvas, row, column, frame, negative=True)


async def blink_star(canvas: curses.window, star: Star) -> None:
    """Add blinking star to canvas."""
    while True:
        await wait_ticks(star.first_lag)

        canvas.addstr(star.row, star.column, star.symbol, curses.A_DIM)
        await wait_ticks(20)

        canvas.addstr(star.row, star.column, star.symbol)
        await wait_ticks(3)

        canvas.addstr(star.row, star.column, star.symbol, curses.A_BOLD)
        await wait_ticks(5)

        canvas.addstr(star.row, star.column, star.symbol)
        await wait_ticks(3)


def draw(
    canvas: curses.window,
    rocket_frames: list[str],
    garbage_frames: list[str],
    num_of_stars: int = NUM_OF_STARS,
    tic_timeout: float = TIC_TIMEOUT,
) -> None:
    """Draw objects at canvas."""
    canvas.nodelay(True)
    curses.curs_set(False)
    canvas.border()

    height, width = canvas.getmaxyx()
    max_height, max_width = height - 1, width - 1

    coroutines = []

    for _ in range(num_of_stars):
        coroutines.append(blink_star(canvas, generate_random_star(max_height, max_width)))

    coroutines.append(fire_shot(canvas, max_height // 2, max_width // 2 + 1))
    coroutines.append(draw_rocket(canvas, max_height // 2, max_width // 2 - 1, rocket_frames))
    coroutines.append(fly_garbage(canvas, randint(0, max_width), choice(garbage_frames)))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.border()
        canvas.refresh()
        time.sleep(tic_timeout)


if __name__ == '__main__':
    rocket_frames_paths = [
        'frames/rocket/rocket_frame_1.txt',
        'frames/rocket/rocket_frame_2.txt',
    ]

    garbage_frames_paths = [
        'frames/garbage/duck.txt',
        'frames/garbage/hubble.txt',
        'frames/garbage/lamp.txt',
        'frames/garbage/trash_small.txt',
        'frames/garbage/trash_large.txt',
        'frames/garbage/trash_xl.txt',
    ]

    rocket_frames = read_frames_from_files(rocket_frames_paths)
    garbage_frames = read_frames_from_files(garbage_frames_paths)

    curses.update_lines_cols()
    curses.wrapper(draw, rocket_frames, garbage_frames)
