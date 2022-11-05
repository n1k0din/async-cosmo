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
from game_scenario import PHRASES, get_garbage_delay_tics
from physics import update_speed
from show_gameover import show_gameover
from space_garbage import fly_garbage, obstacles

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = '+*.:@^'
MAX_FIRST_LAG = 50
NUM_OF_STARS = 100
START_YEAR = 1957

Star = namedtuple('Star', 'row column symbol first_lag')
coroutines = []
current_year = START_YEAR


def read_frames_from_files(paths: list[str]) -> list[str]:
    """Read text files to list of strings."""
    return [Path(path).read_text() for path in paths]


async def start_countdown() -> None:
    """Starts year global countdown."""
    global current_year
    for year in itertools.count(start=START_YEAR):
        current_year = year
        await sleep(10)


async def fill_year_info_table(canvas: curses.window) -> None:
    """Fill game info table with current year and phrase."""
    while True:
        phrase = f': {PHRASES[current_year]}' if current_year in PHRASES else ''
        canvas.addstr(0, 0, f'{current_year}{phrase}')
        await asyncio.sleep(0)
        canvas.erase()


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


async def blink_star(canvas: curses.window, star: Star) -> None:
    """Add blinking star to canvas."""
    while True:
        await sleep(star.first_lag)

        canvas.addstr(star.row, star.column, star.symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(star.row, star.column, star.symbol)
        await sleep(3)

        canvas.addstr(star.row, star.column, star.symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(star.row, star.column, star.symbol)
        await sleep(3)


async def sleep(num_of_ticks: int) -> None:
    """time.sleep for asyncio."""
    for _ in range(num_of_ticks):
        await asyncio.sleep(0)


def has_gun() -> bool:
    """Check for having gun to destroy garbage."""
    return current_year >= 2020


async def run_spaceship(
    canvas: curses.window,
    max_height: int,
    max_width: int,
    rocket_frames: list[str],
) -> None:
    """Draws animated rocket by the specified coordinates."""
    height, width = canvas.getmaxyx()

    height_middle = max_height // 2
    width_middle = max_width // 2
    row = height_middle
    column = width_middle

    row_speed = 0.0
    column_speed = 0.0

    for frame in itertools.cycle(rocket_frames):
        rocket_rows, rocket_columns = curses_tools.get_frame_size(frame)

        for obstacle in obstacles:
            if obstacle.has_collision(row, column, rocket_rows, rocket_columns):
                coroutines.append(show_gameover(canvas, height_middle, width_middle))
                return

        rows_direction, columns_direction, is_space_pressed = curses_tools.read_controls(canvas)
        if is_space_pressed and has_gun():
            coroutines.append(fire_shot(canvas, row, column + rocket_columns // 2))

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)
        row = round(median([1, row + row_speed, height - rocket_rows - 1]))
        column = round(median([1, column + column_speed, width - rocket_columns - 1]))

        curses_tools.draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        curses_tools.draw_frame(canvas, row, column, frame, negative=True)


async def fill_orbit_with_garbage(
    canvas: curses.window,
    max_width: int,
    garbage_frames: list[str],
) -> None:
    """Fills the orbit with garbage."""
    while True:
        delay = get_garbage_delay_tics(current_year)
        if not delay:
            await asyncio.sleep(0)
            continue
        await sleep(delay)
        coroutines.append(fly_garbage(canvas, randint(0, max_width), choice(garbage_frames)))


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
    padding = 1
    max_height, max_width = height - padding, width - padding

    year_info_table = canvas.derwin(max_height - padding, padding)

    for _ in range(num_of_stars):
        coroutines.append(blink_star(canvas, generate_random_star(max_height, max_width)))

    coroutines.append(run_spaceship(canvas, max_height, max_width, rocket_frames))
    coroutines.append(fill_orbit_with_garbage(canvas, max_width, garbage_frames))
    coroutines.append(start_countdown())
    coroutines.append(fill_year_info_table(year_info_table))

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
