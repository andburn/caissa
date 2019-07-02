import time
import sys

from gpiozero import Button
from signal import pause
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial)

file_btn = Button(15)
rank_btn = Button(17)
ok_btn = Button(27)
cancel_btn = Button(22)

state = "WAIT"
rank_file = {
        "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7,
        "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0 
        }
files = ["a", "b", "c", "d", "e", "f", "g", "h"]
cfile = 0 
crank = 7 
move = []

def reset_square():
    global cfile, crank
    cfile = 0
    crank = 7
    show_square()

def reset():
    global move, state
    state = "WAIT"
    move = []
    reset_square()
    show_square()

def show_square():
    global cfile, crank

    with canvas(device) as draw:
        draw.point([cfile, crank], fill="white")

def flash_square(duration):
    global cfile, crank
    rate = 0.3
    total = 0

    while total < duration:
        with canvas(device) as draw:
            draw.point([cfile, crank], fill="white")
            time.sleep(rate)
            draw.point([cfile, crank], fill="black")
            time.sleep(rate)
            total += rate * 2

def print_move(move):
    print(move_str(move))

def move_str(move):
    if len(move) != 4:
        print("Invalid move:", move)
        return
    
    return "{}{}{}{}".format(files[move[0]], 8-move[1], files[move[2]], 8-move[3])

def next_file():
    global cfile
    cfile = (cfile + 1) % 8
    show_square()

def next_rank():
    global crank 
    crank = (crank - 1) % 8 
    show_square()

def confirm():
    global move, cfile, crank, state

    move.append(cfile)
    move.append(crank)
    
    if len(move) >= 4:
        state = "MOVED"
        #print_move(move)
        #reset()

def show_move(text):
    if len(text) != 4:
        print("invalid move - must be length 4")
        sys.exit(1) 

    coords = []
    for x in text:
        if x not in rank_file:
            print("Unknown coord: ", x)
            sys.exit(1)
        coords.append(rank_file[x])

    with canvas(device) as draw:
        draw.point(coords, fill="white")

    # for opponent move, keep on screen till btn press
    cancel_btn.wait_for_press(20)

def show_char(c):
    with canvas(device) as draw:
        text(draw, (0, 0), c, fill="white", font=CP437_FONT) 
    time.sleep(0.5)

def wait_on_move():
    global move, state
    
    reset()
    show_square()
    while state != "MOVED":
        time.sleep(1) 
   
    return move_str(move)

file_btn.when_pressed = next_file
rank_btn.when_pressed = next_rank
ok_btn.when_pressed = confirm
