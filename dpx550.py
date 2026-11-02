import pygame
import random
from datetime import datetime
import math
from pathlib import Path

# -------------------------
# Configuration
# -------------------------
IMAGE_PATH = Path(__file__).resolve().parent / "dpx550.png"

WIDTH = 800
HEIGHT = 480

FULLSCREEN = 1  # 0: Windowed mode, 1: Fullscreen mode
FPS = 30

# Upper dot-matrix display area
DOT_X = 191    # X coordinate of the left edge
DOT_Y = 54    # Y coordinate of the top edge
DOT_W = 420   # Width (pixels)
DOT_H = 43    # Height (pixels)

# Dot-matrix settings
DOT_COLOR = (160, 245, 255)  # Lit color
DOT_COLS = 5                 # Number of dot columns per character
DOT_ROWS = 7                 # Number of dot rows per character
DOT_CHARS = 12               # Number of displayed characters
DOT_GAP = 2                  # Number of blank columns between characters

# 3D spectrum analyzer area
SPEC_X = 190  # X coordinate of the left edge
SPEC_Y = 140  # Y coordinate of the top edge
SPEC_W = 440  # Width (pixels)
SPEC_H = 149  # Height (pixels)

BANDS = 24
STEPS = 18
MAX_LEVEL = 14  # Maximum lit levels (14 out of 18)

OFF_COLOR = (100, 40, 100)  # Unlit color: dark purple

# -------------------------
# Initialization
# -------------------------
pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.FULLSCREEN if FULLSCREEN else 0
)
pygame.mouse.set_visible(False)

clock = pygame.time.Clock()

image = pygame.image.load(IMAGE_PATH).convert()
image = pygame.transform.smoothscale(image, (WIDTH, HEIGHT))

levels = [random.uniform(3, MAX_LEVEL) for _ in range(BANDS)]
targets = levels.copy()

# -------------------------
# 5x7 dot font
# -------------------------
FONT_5X7 = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "C": ["01111","10000","10000","10000","10000","10000","01111"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "F": ["11111","10000","10000","11110","10000","10000","10000"],
    "G": ["01111","10000","10000","10111","10001","10001","01111"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["00111","00010","00010","00010","10010","10010","01100"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","10101","01010"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],

    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01110","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],

    " ": ["00000"] * 7,
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    ":": ["00000","00100","00100","00000","00100","00100","00000"],
    ".": ["00000","00000","00000","00000","00000","00100","00100"],
    "/": ["00001","00001","00010","00100","01000","10000","10000"],
    "+": ["00000","00100","00100","11111","00100","00100","00000"],
    "=": ["00000","00000","11111","00000","11111","00000","00000"],
    "_": ["00000","00000","00000","00000","00000","00000","11111"],
    "!": ["00100","00100","00100","00100","00100","00000","00100"],
    "?": ["01110","10001","00001","00010","00100","00000","00100"],
    "%": ["11001","11001","00010","00100","01000","10011","10011"],
    "(": ["00010","00100","01000","01000","01000","00100","00010"],
    ")": ["01000","00100","00010","00010","00010","00100","01000"],
    "*": ["00000","10101","01110","11111","01110","10101","00000"],
    "#": ["01010","01010","11111","01010","11111","01010","01010"],
}

# -------------------------
# Draw the dot-matrix display
# -------------------------
def draw_dot_matrix(surface, text):

    text = text.upper()[:DOT_CHARS].ljust(DOT_CHARS)

    # 12 characters x 5 columns + 11 gaps x 2 columns = 82 columns
    total_cols = DOT_CHARS * DOT_COLS + (DOT_CHARS - 1) * DOT_GAP

    pitch_x = DOT_W / total_cols
    pitch_y = DOT_H / DOT_ROWS

    dot_w = max(1, int(pitch_x * 0.72))
    dot_h = max(1, int(pitch_y * 0.72))

    for char_index, char in enumerate(text):

        pattern = FONT_5X7.get(char, FONT_5X7[" "])

        for row in range(DOT_ROWS):
            for col in range(DOT_COLS):

                grid_col = char_index * (DOT_COLS + DOT_GAP) + col

                x = DOT_X + grid_col * pitch_x + (pitch_x - dot_w) / 2
                y = DOT_Y + row * pitch_y + (pitch_y - dot_h) / 2

                color = DOT_COLOR if pattern[row][col] == "1" else OFF_COLOR

                pygame.draw.rect(
                    surface,
                    color,
                    (int(x), int(y), dot_w, dot_h)
                )

# -------------------------
# Draw the 3D spectrum analyzer
# -------------------------
def draw_spectrum(surface, levels):

    # Draw from back to front
    for depth in range(STEPS):

        t = depth / (STEPS - 1)

        # Perspective projection (linearly widening trapezoid)
        width = SPEC_W * (0.75 + 0.45 * t)
        x_start = SPEC_X + (SPEC_W - width) / 2
        y = SPEC_Y + SPEC_H * t

        dot_w = width / BANDS * 0.7
        dot_h = 2 + 3 * t

        # Dot colors are fixed by position
        if t < 0.35:
            color = (235, 255, 240)   # Back: pale green, nearly white
        elif t < 0.7:
            color = (190, 255, 210)   # Back: whitish green
        else:
            color = (0, 240, 150)     # Front: green

        for band in range(BANDS):

            x = x_start + band * width / BANDS

            # Lit or unlit
            on = depth >= STEPS - levels[band]

            if on:
                draw_color = color
            else:
                draw_color = OFF_COLOR

            pygame.draw.rect(
                surface,
                draw_color,
                (
                    int(x),
                    int(y),
                    max(1, int(dot_w)),
                    max(1, int(dot_h))
                )
            )

# -------------------------
# Main loop
# -------------------------
running = True
frame = 0

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Vary levels by frequency band
    if frame % 5 == 0:

        # Base levels for low, mid, and high frequencies
        low = random.uniform(7, MAX_LEVEL)
        mid = random.uniform(5, MAX_LEVEL - 2)
        high = random.uniform(3, MAX_LEVEL - 4)

        targets = []

        for i in range(BANDS):

            # Smoothly interpolate base levels across frequency bands
            if i < BANDS // 2:
                t = i / (BANDS // 2)
                base = low * (1 - t) + mid * t
            else:
                t = (i - BANDS // 2) / (BANDS // 2)
                base = mid * (1 - t) + high * t

            # Add slight variation to each band
            value = base + random.uniform(-1.5, 1.5)

            targets.append(max(3, min(MAX_LEVEL, value)))

    # Rise quickly and fall slowly (updated every frame)
    for i in range(BANDS):

        if levels[i] < targets[i]:
            levels[i] = min(levels[i] + 2, targets[i])
        elif levels[i] > targets[i]:
            levels[i] = max(levels[i] - 0.7, targets[i])
            
            
            
    # Stereo faceplate image
    screen.blit(image, (0, 0))
    
    # Get the current day of the week and time
    now = datetime.now()
    weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    DOT_TEXT = f"{weekdays[now.weekday()]}-{now:%H:%M:%S}"

    # Draw the upper dot-matrix display
    draw_dot_matrix(screen, DOT_TEXT)    

    # Draw the 3D spectrum analyzer directly on screen
    draw_spectrum(screen, levels)            


    pygame.display.flip()
    clock.tick(FPS)
    frame += 1

pygame.quit()