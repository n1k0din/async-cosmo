import asyncio
import curses

from curses_tools import draw_frame


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

    row = float(0)

    while row < rows_number:
        draw_frame(canvas, round(row), column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, round(row), column, garbage_frame, negative=True)
        row += speed
