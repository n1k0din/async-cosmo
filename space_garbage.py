import asyncio
import curses

from curses_tools import draw_frame, get_frame_size
from explosion import explode
from obstacles import Obstacle

obstacles = []
obstacles_in_last_collisions = []


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
    garbage_frame_rows_size, garbage_frame_columns_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, garbage_frame_rows_size, garbage_frame_columns_size)
    obstacles.append(obstacle)

    while row < rows_number:
        rounded_row = round(row)
        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            obstacles.remove(obstacle)
            await explode(
                canvas=canvas,
                center_row=rounded_row + garbage_frame_rows_size // 2,
                center_column=column + garbage_frame_columns_size // 2,
            )
            return
        draw_frame(canvas, rounded_row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, rounded_row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row = row
    obstacles.remove(obstacle)
