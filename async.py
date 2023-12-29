import asyncio
import curses
from itertools import cycle, islice
from random import choice, randint, randrange
from statistics import median
from time import sleep

from curses_tools import draw_frame, get_frame_size, read_controls
from fire_animation import fire

STARS_AMOUNT = 100
STAR_CHARS = '+*.:'
TIC_TIMEOUT = 0.1
MOOVING_SPEED = 1


def check_bounds(canvas, row, col, frame):
    (num_row, num_col) = canvas.getmaxyx()
    (height, width) = get_frame_size(frame)
    row = median([1, row, num_row-height-1])
    col = median([1, col, num_col-width-1])
    return (row, col)


async def animate_spaceship(canvas, start_row, start_col, frames, ticks):
    last_frame = ''
    row = start_row
    col = start_col
    for frame in cycle(frames):
        for _ in range(ticks):
            draw_frame(canvas, row, col, last_frame, negative=True, )
            (rows_direction, cols_direction, _, ) = read_controls(canvas)
            (row, col) = check_bounds(
                    canvas, row+rows_direction*MOOVING_SPEED,
                    col+cols_direction*MOOVING_SPEED, frame, )
            draw_frame(canvas, row, col, frame, )
            last_frame = frame
            await asyncio.sleep(0)


async def blink(canvas, row, col, symbol='*'):
    animation = [(curses.A_DIM, 20), (curses.A_NORMAL, 3),
                 (curses.A_BOLD, 5), (curses.A_NORMAL, 3), ]
    start_step = randrange(len(animation))
    animation = cycle(list(islice(animation, start_step, None))
                      + list(islice(animation, start_step)))

    for (attr, ticks) in animation:
        for _ in range(ticks):
            canvas.addstr(row, col, symbol, attr)
            await asyncio.sleep(0)

def create_starset(max_row, max_col, num, symbols=['*']):
    return [(randint(1,max_row-2), randint(1, max_col-2), choice(symbols)) for
            _ in range(num)]


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()
    canvas.refresh()
    (max_row, max_col) = canvas.getmaxyx()
    center_row = max_row // 2
    center_col = max_col // 2

    with open("files/rocket_frame_1.txt", 'r') as my_file:
        rocket_frame_1 = my_file.read()
    with open("files/rocket_frame_2.txt", 'r') as my_file:
        rocket_frame_2 = my_file.read()
    
    stars = create_starset(max_row, max_col, STARS_AMOUNT, STAR_CHARS)
    frames = [blink(canvas, row, col, symbol) for 
                    (row, col, symbol) in stars]
    frames.append(fire(canvas, center_row, center_col,
                       rows_speed=0.3, columns_speed=0))
    frames.append(animate_spaceship(canvas, center_row, center_col, 
                                    [rocket_frame_1, rocket_frame_2, ], 2, ))
    while True:
        for frame in frames.copy():
            try:
                frame.send(None)
            except StopIteration:
                frames.remove(frame)
        canvas.refresh()
        sleep(TIC_TIMEOUT)

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
