import asyncio
import curses

import curses_tools
from curses_tools import draw_frame
from obstacles import Obstacle

obstacles = []


async def fly_garbage(
    canvas: curses.window,
    column: int,
    garbage_frame: str,
    speed: float = 0.5,
) -> None:
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    garbage_frame_rows_size, garbage_frame_columns_size = curses_tools.get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, garbage_frame_rows_size, garbage_frame_columns_size)
    obstacles.append(obstacle)

    while row < rows_number:
        draw_frame(canvas, round(row), column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, round(row), column, garbage_frame, negative=True)
        row += speed
        obstacle.row = row
    obstacles.remove(obstacle)
