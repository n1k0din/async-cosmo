import asyncio
import curses
import itertools
import time
from pathlib import Path
from random import choice, randint

from curses_tools import draw_frame

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = '+*.:'
MAX_FIRST_LAG = 50
NUM_OF_STARS = 100


def read_frames_from_files(paths):
    return [Path(path).read_text() for path in paths]


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def rocket(canvas, row, column, rocket_frames):
    for frame in itertools.cycle(rocket_frames):
        draw_frame(canvas, row, column, frame)
        canvas.refresh()
        for _ in range(2):
            await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)


async def blink(canvas, row, column, first_lag, symbol='*'):
    while True:
        for _ in range(first_lag):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas, star_symbols, num_of_stars, max_first_lag, rocket_frames, tic_timeout):
    curses.curs_set(False)

    height, width = canvas.getmaxyx()

    coroutines = [rocket(canvas, height // 2, width // 2, rocket_frames)]

    for _star in range(num_of_stars):
        row = randint(0, height - 1)
        column = randint(0, width - 1)
        symbol = choice(star_symbols)
        lag = randint(0, max_first_lag)
        coroutines.append(blink(canvas, row, column, lag, symbol))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        time.sleep(tic_timeout)


if __name__ == '__main__':
    rocket_frames_paths = [
        'frames/rocket/rocket_frame_1.txt',
        'frames/rocket/rocket_frame_2.txt',
    ]

    rocket_frames = read_frames_from_files(rocket_frames_paths)    

    curses.update_lines_cols()
    curses.wrapper(draw, STAR_SYMBOLS, NUM_OF_STARS, MAX_FIRST_LAG, rocket_frames, TIC_TIMEOUT)
