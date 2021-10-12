import asyncio
import curses
import time

TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol='*'):
    while True:
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


def draw(canvas, tic_timeout):
    row, column = (5, 20)
    curses.curs_set(False)
    canvas.border()
    canvas.refresh()

    coroutines = [blink(canvas, row, column + i * 2) for i in range(5)]

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(tic_timeout)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw, TIC_TIMEOUT)
