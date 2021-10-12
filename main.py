import asyncio
import curses
import time
from random import choice, randint

TIC_TIMEOUT = 0.1
STAR_SYMBOLS = '+*.:'
MAX_FIRST_LAG = 50
NUM_OF_STARS = 100


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


def draw(canvas, star_symbols, num_of_stars, max_first_lag, tic_timeout):
    curses.curs_set(False)

    height, width = canvas.getmaxyx()

    coroutines = []
    for _star in range(num_of_stars):
        row = randint(0, height - 1)
        column = randint(0, width - 1)
        symbol = choice(star_symbols)
        lag = randint(0, max_first_lag)
        coroutines.append(blink(canvas, row, column, lag, symbol))

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw, STAR_SYMBOLS, NUM_OF_STARS, MAX_FIRST_LAG, TIC_TIMEOUT)
