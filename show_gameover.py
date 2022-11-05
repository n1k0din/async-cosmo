import asyncio
import curses
import textwrap

from curses_tools import draw_frame, get_frame_size

GAMEOVER_FRAME = textwrap.dedent(
    """
     ██████   █████  ███    ███ ███████      ██████  ██    ██ ███████ ██████
    ██       ██   ██ ████  ████ ██          ██    ██ ██    ██ ██      ██   ██
    ██   ███ ███████ ██ ████ ██ █████       ██    ██ ██    ██ █████   ██████
    ██    ██ ██   ██ ██  ██  ██ ██          ██    ██  ██  ██  ██      ██   ██
     ██████  ██   ██ ██      ██ ███████      ██████    ████   ███████ ██   ██
    """,
)


async def show_gameover(canvas: curses.window, center_row: int, center_column: int) -> None:
    """Draws gameover ASCII text."""
    rows, columns = get_frame_size(GAMEOVER_FRAME)
    corner_row = center_row - rows // 2
    corner_column = center_column - columns // 2

    while True:
        draw_frame(canvas, corner_row, corner_column, GAMEOVER_FRAME)
        await asyncio.sleep(0)
