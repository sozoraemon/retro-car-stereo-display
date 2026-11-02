import pygame
import random
from datetime import datetime
from pathlib import Path

# -------------------------
# Configuration
# -------------------------

IMAGE_PATH = Path(__file__).resolve().parent / "w779jb.png"

WIDTH = 800
HEIGHT = 480

FULLSCREEN = 1  # 0: Windowed mode, 1: Fullscreen mode
FPS = 30

# Upper dot-matrix display area
DOT_X = 214    # X coordinate of the left edge
DOT_Y = 86    # Y coordinate of the top edge
DOT_W = 376   # Width (pixels)
DOT_H = 32    # Height (pixels)

# Dot-matrix settings
DOT_COLOR = (160, 245, 255)  # Lit color
DOT_COLS = 5                 # Dots per character (horizontal)
DOT_ROWS = 7                 # Dots per character (vertical)
DOT_CHARS = 12               # Number of displayed characters
DOT_GAP = 2                  # Blank columns between characters

# 3D spectrum analyzer area

SPEC_ALL_ON = False  # True: light all segments (color check) / False: animation

SPEC_X = 154  # X coordinate of the left edge
SPEC_Y = 144  # Y coordinate of the top edge
SPEC_W = 500  # Overall width = bottom width
SPEC_H = 100  # Height (pixels)

SPEC_TOP_W = 330  # Top width
SPEC_CURVE = -12   # Vertical curvature

BANDS = 24
STEPS = 18
MAX_LEVEL = 18  # Maximum number of lit rows

OFF_COLOR = (65, 65, 65)  # Unlit color: dark gray
SPEC_RED = (255, 100, 35)  # Accent color

# Spectrum colors (18 rows from top to bottom, RGB values)
SPEC_COLORS = [
    (0, 110, 255),    # Row 1: Vivid blue
    (160, 240, 255),  # Row 2: Pale cyan
    (145, 235, 255),  # Row 3: Bright cyan
    (130, 225, 255),  # Row 4: Light sky blue
    (115, 215, 255),  # Row 5: Sky blue
    (100, 205, 255),  # Row 6: Sky blue
    (0, 95, 255),     # Row 7: Deep blue
    (75, 185, 255),   # Row 8: Cyan blue
    (170, 245, 255),  # Row 9: Pale cyan
    (55, 165, 255),   # Row 10: Bright blue
    (170, 245, 255),  # Row 11: Pale cyan
    (35, 145, 255),   # Row 12: Vivid blue
    (170, 245, 255),  # Row 13: Pale cyan
    (0, 95, 255),     # Row 14: Deep blue
    (0, 95, 255),     # Row 15: Deep blue
    (85, 195, 255),   # Row 16: Bright cyan blue
    (170, 245, 255),  # Row 17: Pale cyan
    (0, 110, 255),    # Row 18: Vivid blue
]

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
# 5x7 dot-matrix font
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
# Draw dot-matrix display
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
# Draw 3D spectrum analyzer
# -------------------------


def draw_spectrum(surface, levels):

    for depth in range(STEPS):

        t = depth / (STEPS - 1)

        # Increase the width from top to bottom
        width = SPEC_TOP_W + (SPEC_W - SPEC_TOP_W) * t

        # Center relative to SPEC_W
        x_start = SPEC_X + (SPEC_W - width) / 2
        y = SPEC_Y + SPEC_H * t

        dot_w = width / BANDS * 0.7
        dot_h = 2 + 3 * t

        # Get the color assigned to this row
        color = SPEC_COLORS[depth]

        for band in range(BANDS):

            x = x_start + band * width / BANDS

            # Curved fan shape with a lower center and raised sides
            pos = (band - (BANDS - 1) / 2) / (BANDS / 2)
            curve = SPEC_CURVE * pos ** 2
            dot_y = y + curve

            # Color the middle 14 dots of the fourth row from bottom and the middle 10 dots of the seventh row from top orange
            if (depth == STEPS - 4 and 5 <= band < 19) or (depth == 6 and 7 <= band < 17):
                dot_color = SPEC_RED
            else:
                dot_color = color
    
            # Light all segments or illuminate symmetrically outward from the vertical center
            center = (STEPS - 1) / 2
            distance = abs(depth - center)
            on = SPEC_ALL_ON or distance < levels[band] / 2

            # Use the assigned color when lit, or the dark unlit color otherwise
            draw_color = dot_color if on else OFF_COLOR

            pygame.draw.rect(
                surface,
                draw_color,
                (
                    int(x),
                    int(dot_y),
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

    # Vary levels with frequency-dependent characteristics
    if frame % 5 == 0:

        # Base levels for low, mid, and high frequencies
        low = random.uniform(0, MAX_LEVEL)
        mid = random.uniform(0, MAX_LEVEL)
        high = random.uniform(0, MAX_LEVEL)

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
            value = base + random.uniform(-2.5, 2.5)

            targets.append(max(0, min(MAX_LEVEL, value)))

    # Rise quickly and fall slowly (updated every frame)
    for i in range(BANDS):

        if levels[i] < targets[i]:
            levels[i] = min(levels[i] + 2, targets[i])
        elif levels[i] > targets[i]:
            levels[i] = max(levels[i] - 0.7, targets[i])
            
            
            
    # Background image of the stereo unit
    screen.blit(image, (0, 0))
    
    # Get the current weekday and time
    now = datetime.now()
    weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    DOT_TEXT = f"{weekdays[now.weekday()]}-{now:%H:%M:%S}"

    # Render the upper dot-matrix display
    draw_dot_matrix(screen, DOT_TEXT)    

    # Draw the 3D spectrum analyzer directly onto the screen
    draw_spectrum(screen, levels)            


    pygame.display.flip()
    clock.tick(FPS)
    frame += 1

pygame.quit()
