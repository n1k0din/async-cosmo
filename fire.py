import asyncio
import curses

from space_garbage import obstacles, obstacles_in_last_collisions


async def fire_shot(
    canvas: curses.window,
    start_row: float,
    start_column: float,
    rows_speed: float = -0.3,
    columns_speed: float = 0,
) -> None:
    """Display animation of gun shot, direction and speed can be specified."""
    row, column = start_row, start_column
    round_row, round_column = round(row), round(column)

    canvas.addstr(round_row, round_column, '*')
    await asyncio.sleep(0)

    canvas.addstr(round_row, round_column, 'O')
    await asyncio.sleep(0)
    canvas.addstr(round_row, round_column, ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
