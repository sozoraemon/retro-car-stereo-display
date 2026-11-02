import pygame
import random
from datetime import datetime
import math
from functools import lru_cache
from pathlib import Path

# -------------------------
# Settings
# -------------------------
IMAGE_PATH = Path(__file__).resolve().parent / "dpx440.png"

WIDTH = 800
HEIGHT = 480

FULLSCREEN = 1  # 0: Windowed mode, 1: Fullscreen mode
FPS = 20

# 3D spectrum analyzer area
SPEC_X = 155  # Left edge X coordinate
SPEC_Y = 125  # Top edge Y coordinate
SPEC_W = 492  # Width (pixels)
SPEC_H = 105  # Height (pixels)

# Spectrum analyzer geometry
SPEC_TOP_WIDTH = 548       # Top edge width
SPEC_BOTTOM_WIDTH = 370    # Bottom edge width
SPEC_CURVE = 12            # Arc depth (pixels)

BANDS = 24
STEPS = 18
MAX_LEVEL = 17  # Maximum number of illuminated rows (17 of 18)

OFF_COLOR = (100, 40, 100)  # Unlit color: dark purple

# Spectrum analyzer: adjacent pairs of blocks descend from top to bottom
SPEC_DROP_INTERVAL_MIN = 0.01  # Minimum interval between drops (seconds)
SPEC_DROP_INTERVAL_MAX = 0.25  # Maximum interval between drops (seconds)
SPEC_DROP_STEP_TIME = 0.1     # Time to descend one row (seconds)
SPEC_DROP_PAIR_SIZE = 2        # Number of adjacent blocks in each drop
SPEC_DROP_MAX_ACTIVE = 12      # Maximum number of simultaneous drops



# -------------------------
# Left and right side meter settings
# -------------------------
SIDE_BANDS = 18           # Number of columns per side
SIDE_LEFT_X = 125          # Left edge X coordinate of the left meter
SIDE_RIGHT_X = 580        # Left edge X coordinate of the right meter
SIDE_Y = 175              # Top edge Y coordinate of the meters
SIDE_W = 90              # Meter width (pixels)
SIDE_H = 130              # Meter height (pixels)
SIDE_GAP = 2.0            # Gap between columns (based on reference image proportions)

# Overall outline (sloped top edge; bottom edge rises near the tip)
SIDE_TOP_TIP = 0.70       # Top edge position at the tip (fraction of height)
SIDE_TIP_HEIGHT = 0.16    # Vertical gap at the tip (fraction of height)
SIDE_BOTTOM_CURVE = 3.0   # Bottom edge curvature (higher values flatten the outer edge)

# Central black gap (smooth curve rather than a straight line)
SIDE_CENTER_START = 0.48  # Central gap height at the outer edge (fraction of height)
SIDE_CENTER_SLOPE = 0.30  # Downward offset from outer edge to tip (fraction of height)
SIDE_CENTER_CURVE = 1.7   # Central gap curvature (higher values increase the drop near the outer edge)
SIDE_CENTER_GAP = 2.0     # Half-width of the black gap (pixels)

# Column curvature (smoothly joins upper and lower sections)
SIDE_COLUMN_SLANT = 3.0   # Horizontal bow near the middle of each column (pixels)
SIDE_BOTTOM_SHIFT = 12.0  # Inward shift at the bottom of each column (pixels)
SIDE_CURVE_STEPS = 12     # Number of segments per curve
SIDE_RENDER_SCALE = 3     # Render at higher resolution, then downscale to smooth edges
SIDE_OFF_COLOR = OFF_COLOR  # Unlit color

# Side meter animation
SIDE_ANIM_INTERVAL = 0.3  # Time per column step (seconds)
SIDE_ANIM_SPACING = 5      # Spacing between lit columns (skip four columns)

# Initially, all columns are unlit
side_left_on = [False] * SIDE_BANDS
side_right_on = [False] * SIDE_BANDS


# Dot-matrix display area
DOT_X = 205    # Left edge X coordinate
DOT_Y = 288    # Top edge Y coordinate
DOT_W = 384   # Width (pixels)
DOT_H = 40    # Height (pixels)

# Dot-matrix settings
DOT_COLOR = (160, 245, 255)  # Lit color
DOT_COLS = 5                 # Number of horizontal dots per character
DOT_ROWS = 7                 # Number of vertical dots per character
DOT_CHARS = 12               # Number of displayed characters
DOT_GAP = 1                  # Number of blank columns between characters

# Dot-matrix perspective settings
DOT_SLANT = 0.0          # Character slant (positive values shift the top right; pixels)
DOT_PERSPECTIVE = 0.09   # Perspective (higher values narrow the upper rows; range 0 to 1)
DOT_SKEW = 0.0          # Dot skew (higher values tilt the rectangles; 0 keeps them rectangular)
DOT_SIZE = 0.5          # Dot size relative to each grid cell (0.0 to 1.0)

# Dot-matrix text transition settings
DOT_CHANGE_INTERVAL = 3.0   # Time between text changes (seconds)
DOT_ANIM_DURATION = 0.5    # Duration of the text transition (seconds)

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

# Initialize each fixed pair of columns at the same height
levels = []
for _ in range(0, BANDS, SPEC_DROP_PAIR_SIZE):
    level = random.uniform(3, MAX_LEVEL)
    levels.extend([level] * SPEC_DROP_PAIR_SIZE)
targets = levels.copy()

# Manage falling blocks independently of normal level changes
spectrum_drops = []
next_spectrum_drop = (
    pygame.time.get_ticks() / 1000.0
    + random.uniform(SPEC_DROP_INTERVAL_MIN, SPEC_DROP_INTERVAL_MAX)
)

# Dot-matrix display state
dot_start_time = pygame.time.get_ticks()
dot_display_index = 0


# -------------------------
# Draw the left and right side meters
# -------------------------
@lru_cache(maxsize=16)
def make_side_meter(width, height, states, mirror):
    """Create curved left and right side meters as transparent surfaces."""
    scale = SIDE_RENDER_SCALE
    pad = math.ceil(SIDE_BOTTOM_SHIFT + SIDE_COLUMN_SLANT + 3)
    canvas_width = width + pad * 2
    large = pygame.Surface(
        (canvas_width * scale, height * scale), pygame.SRCALPHA
    )

    # Colors run from the outer edge to the tip; distribute evenly for other column counts
    colors = [
        (225, 130, 255),   # Bright purple
        (0, 220, 255),     # Cyan
        (170, 145, 255),   # Bright bluish purple
        (195, 145, 255),   # Bright purple
        (195, 145, 255),
        (195, 145, 255),
        (195, 145, 255),
        (245, 250, 255),   # White
        (155, 200, 255),   # Light blue
        (195, 145, 255),
        (195, 145, 255),
        (195, 145, 255),
        (195, 145, 255),
        (0, 235, 205),     # Turquoise
        (155, 195, 255),   # Light blue
        (195, 145, 255),
        (195, 145, 255),
        (195, 145, 255),
    ]

    def geometry(t):
        # t=0: outer edge (wide); t=1: tip (narrow)
        top = height * SIDE_TOP_TIP * t
        bottom_tip = SIDE_TOP_TIP + SIDE_TIP_HEIGHT
        bottom = height * (
            1.0 - (1.0 - bottom_tip) * t ** SIDE_BOTTOM_CURVE
        )
        center = height * (
            SIDE_CENTER_START
            + SIDE_CENTER_SLOPE * (1.0 - (1.0 - t) ** SIDE_CENTER_CURVE)
        )
        return top, center, bottom

    def edge_points(x_edge, t, upper):
        top, center, bottom = geometry(t)
        y0 = top if upper else center + SIDE_CENTER_GAP
        y1 = center - SIDE_CENTER_GAP if upper else bottom
        if y1 <= y0:
            return []

        # Bottom edges lean right on the left meter and left on the right meter
        direction = -1 if mirror else 1
        points = []
        for step in range(SIDE_CURVE_STEPS + 1):
            ratio = step / SIDE_CURVE_STEPS
            yy = y0 + (y1 - y0) * ratio
            v = (yy - top) / max(1.0, bottom - top)

            # Curve smoothly inward toward the bottom edge
            lean = (
                direction * SIDE_BOTTOM_SHIFT
                * (1.0 - t) ** 1.1 * v ** 2.3
            )
            # Middle bow follows the specified directions (left on left, right on right)
            bow = (
                -direction * SIDE_COLUMN_SLANT
                * (1.0 - 0.35 * t) * math.sin(math.pi * v)
            )
            xx = x_edge + lean + bow + pad
            points.append((round(xx * scale), round(yy * scale)))
        return points

    pitch = width / SIDE_BANDS
    for i in range(SIDE_BANDS):
        x1 = i * pitch + SIDE_GAP / 2
        x2 = (i + 1) * pitch - SIDE_GAP / 2
        if x2 <= x1:
            continue  # Skip drawing if the gap is wider than the column

        t1 = x1 / width if not mirror else 1.0 - x1 / width
        t2 = x2 / width if not mirror else 1.0 - x2 / width
        pos = SIDE_BANDS - 1 - i if mirror else i
        color_index = round(pos * (len(colors) - 1) / max(1, SIDE_BANDS - 1))
        color = colors[color_index] if states[i] else SIDE_OFF_COLOR

        for upper in (True, False):
            left = edge_points(x1, t1, upper)
            right = edge_points(x2, t2, upper)
            if left and right:
                pygame.draw.polygon(large, color, left + right[::-1])

    # Render at 3x resolution, then downscale to smooth narrow columns
    return pygame.transform.smoothscale(large, (canvas_width, height))


def draw_side_meter(surface, x, y, width, height, states, mirror=False):
    # Cache unchanged lighting patterns to reduce rendering load
    meter = make_side_meter(int(width), int(height), tuple(states), mirror)
    pad = math.ceil(SIDE_BOTTOM_SHIFT + SIDE_COLUMN_SLANT + 3)
    surface.blit(meter, (int(x) - pad, int(y)))


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
# Draw the dot matrix (fixed dots with vertical text transitions)
# -------------------------
def draw_dot_matrix(surface, current_text, next_text, progress):

    current_text = current_text.upper()[:DOT_CHARS].ljust(DOT_CHARS)
    next_text = next_text.upper()[:DOT_CHARS].ljust(DOT_CHARS)

    total_cols = DOT_CHARS * DOT_COLS + (DOT_CHARS - 1) * DOT_GAP

    pitch_x = DOT_W / total_cols
    pitch_y = DOT_H / DOT_ROWS

    center_x = DOT_X + DOT_W / 2

    # Convert text into a grid of lit dots with 7 rows
    def make_matrix(text):

        matrix = [[False] * total_cols for _ in range(DOT_ROWS)]

        for char_index, char in enumerate(text):

            pattern = FONT_5X7.get(char, FONT_5X7[" "])

            for row in range(DOT_ROWS):
                for col in range(DOT_COLS):

                    grid_col = char_index * (DOT_COLS + DOT_GAP) + col
                    matrix[row][grid_col] = pattern[row][col] == "1"

        return matrix

    current_matrix = make_matrix(current_text)
    next_matrix = make_matrix(next_text)

    # Convert progress from 0 to 1 into a shift across 7 rows
    shift = int(progress * DOT_ROWS)

    for grid_col in range(total_cols):

        # Leave inter-character spacer columns empty
        if grid_col % (DOT_COLS + DOT_GAP) >= DOT_COLS:
            continue

        for row in range(DOT_ROWS):

            # Show the current text during normal display
            if progress == 0:
                on = current_matrix[row][grid_col]

            # Turn off the current text as soon as the transition begins
            # Reveal only the next text, row by row from the bottom
            else:
                source_row = row - (DOT_ROWS - shift)

                if 0 <= source_row < DOT_ROWS:
                    on = next_matrix[source_row][grid_col]
                else:
                    on = False

            depth = row / (DOT_ROWS - 1)

            scale = 1.0 - DOT_PERSPECTIVE * (1.0 - depth)
            slant = DOT_SLANT * (1.0 - depth)

            base_x = DOT_X + (grid_col + 0.5) * pitch_x
            base_y = DOT_Y + (row + 0.5) * pitch_y

            x = center_x + (base_x - center_x) * scale + slant
            y = base_y

            dot_w = pitch_x * DOT_SIZE * scale
            dot_h = pitch_y * DOT_SIZE * scale

            skew = dot_w * DOT_SKEW

            points = [
                (x - dot_w / 2 + skew, y - dot_h / 2),
                (x + dot_w / 2 + skew, y - dot_h / 2),
                (x + dot_w / 2 - skew, y + dot_h / 2),
                (x - dot_w / 2 - skew, y + dot_h / 2)
            ]

            color = DOT_COLOR if on else OFF_COLOR

            pygame.draw.polygon(surface, color, points)

# -------------------------
# Draw the 3D spectrum analyzer
# -------------------------
def draw_spectrum(surface, levels, drops):

    # Draw from back to front
    for depth in range(STEPS):

        t = depth / (STEPS - 1)

        # Trapezoid with a wider top and narrower bottom
        width = (
            SPEC_TOP_WIDTH
            + (SPEC_BOTTOM_WIDTH - SPEC_TOP_WIDTH) * t
        )

        # Center horizontally
        x_start = SPEC_X + (SPEC_W - width) / 2
        base_y = SPEC_Y + SPEC_H * t

        dot_w = width / BANDS * 0.7
        dot_h = 4  # Uniform dot height for all rows (pixels)

        # Set dot color based on row position
        if t < 0.35:
            color = (70, 190, 235)
        elif t < 0.7:
            color = (210, 250, 255)
        else:
            color = (80, 245, 180)

        for band in range(BANDS):

            # Horizontal position
            x = x_start + band * width / BANDS

            # Position relative to center (-1 to 1)
            center_pos = (
                (band + 0.5) / BANDS * 2 - 1
            )

            # Adjust the Y coordinate to form an arc
            curve_y = SPEC_CURVE * center_pos ** 2

            y = base_y + curve_y

            # Lit or unlit state
            on = depth < levels[band]

            draw_color = color if on else OFF_COLOR

            # Overlay a randomly falling pair of adjacent blocks
            # Keep the original animation running without changing levels
            if any(
                drop["depth"] == depth
                and drop["band"] <= band < drop["band"] + SPEC_DROP_PAIR_SIZE
                for drop in drops
            ):
                draw_color = color

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

    # Vary levels with a bias across frequency bands
    if frame % 5 == 0:

        # Reference levels for low, mid, and high frequencies
        low = random.uniform(0, MAX_LEVEL)
        mid = random.uniform(0, MAX_LEVEL - 2)
        high = random.uniform(0, MAX_LEVEL - 4)

        # Generate one target per fixed pair and assign it to both columns
        targets = [0.0] * BANDS

        for i in range(0, BANDS, SPEC_DROP_PAIR_SIZE):
            # Preserve the low-to-high frequency trend
            if i < BANDS // 2:
                t = i / (BANDS // 2)
                base = low * (1 - t) + mid * t
            else:
                t = (i - BANDS // 2) / (BANDS // 2)
                base = mid * (1 - t) + high * t

            value = base + random.uniform(-1.5, 1.5)
            target = max(1, min(MAX_LEVEL, value))

            for band in range(i, min(i + SPEC_DROP_PAIR_SIZE, BANDS)):
                targets[band] = target

    # Apply fast rises and slow falls to each fixed pair
    for i in range(0, BANDS, SPEC_DROP_PAIR_SIZE):
        level = levels[i]
        target = targets[i]

        if level < target:
            level = min(level + 2, target)
        elif level > target:
            level = max(level - 0.7, target)

        for band in range(i, min(i + SPEC_DROP_PAIR_SIZE, BANDS)):
            levels[band] = level


    # Background image
    screen.blit(image, (0, 0))
    
    # -------------------------
    # Dot-matrix text transitions
    # -------------------------
    now = datetime.now()
    weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    dot_texts = [
        "KENWOOD",
        "     DPX-440",
        f"{weekdays[now.weekday()]}-{now:%H:%M:%S}"
    ]

    # Elapsed time since the current text started
    elapsed = (pygame.time.get_ticks() - dot_start_time) / 1000.0

    # Switch to the next text after 3 seconds
    if elapsed >= DOT_CHANGE_INTERVAL:
        dot_display_index = (dot_display_index + 1) % len(dot_texts)
        dot_start_time = pygame.time.get_ticks()
        elapsed = 0.0

    # Current and next text
    current_text = dot_texts[dot_display_index]
    next_text = dot_texts[(dot_display_index + 1) % len(dot_texts)]

    # Transition during the last 0.5 seconds of each 3-second interval
    anim_start = DOT_CHANGE_INTERVAL - DOT_ANIM_DURATION

    if elapsed < anim_start:
        progress = 0.0
    else:
        progress = min(
            1.0,
            (elapsed - anim_start) / DOT_ANIM_DURATION
        )

    draw_dot_matrix(screen, current_text, next_text, progress)

    # -------------------------
    # Spectrum analyzer: adjacent blocks fall from top to bottom
    # -------------------------
    spectrum_now = pygame.time.get_ticks() / 1000.0

    # Calculate the current row from elapsed time; remove pairs past the bottom
    for drop in spectrum_drops:
        drop["depth"] = int(
            (spectrum_now - drop["start"]) / SPEC_DROP_STEP_TIME
        )
    spectrum_drops = [
        drop for drop in spectrum_drops if 0 <= drop["depth"] < STEPS
    ]

    # When the next drop is due, choose an unoccupied pair of columns
    if spectrum_now >= next_spectrum_drop:

        if len(spectrum_drops) < SPEC_DROP_MAX_ACTIVE:

            # Columns currently occupied by falling blocks
            occupied_bands = set()

            for drop in spectrum_drops:
                for band in range(
                    drop["band"],
                    drop["band"] + SPEC_DROP_PAIR_SIZE
                ):
                    occupied_bands.add(band)

            # Only consider positions where both columns are free
            available_bands = [
                band
                for band in range(0, BANDS - SPEC_DROP_PAIR_SIZE + 1, SPEC_DROP_PAIR_SIZE)
                if all(
                    b not in occupied_bands
                    for b in range(band, band + SPEC_DROP_PAIR_SIZE)
                )
            ]

            # Start a new drop only if space is available
            if available_bands:
                spectrum_drops.append({
                    "band": random.choice(available_bands),
                    "start": spectrum_now,
                    "depth": 0,
                })

        next_spectrum_drop = spectrum_now + random.uniform(
            SPEC_DROP_INTERVAL_MIN, SPEC_DROP_INTERVAL_MAX
        )

    # Overlay falling blocks on the existing spectrum analyzer
    draw_spectrum(screen, levels, spectrum_drops)            

    # -------------------------
    # Left and right side meter animation
    # -------------------------
    # Cycle a five-column-spaced lighting pattern through five steps
    # Keep the lighting pattern continuous when the cycle wraps
    side_step = int(
        pygame.time.get_ticks() / 1000.0 / SIDE_ANIM_INTERVAL
    ) % SIDE_ANIM_SPACING

    for i in range(SIDE_BANDS):

        # Both meters animate from the inner edge toward the outer edge
        side_left_on[i] = (
            SIDE_BANDS - 1 - i - side_step
        ) % SIDE_ANIM_SPACING == 0

        side_right_on[i] = (
            i - side_step
        ) % SIDE_ANIM_SPACING == 0

    # Left side meter
    draw_side_meter(
        screen,
        SIDE_LEFT_X,
        SIDE_Y,
        SIDE_W,
        SIDE_H,
        side_left_on,
        mirror=False
    )

    # Right side meter (mirrored)
    draw_side_meter(
        screen,
        SIDE_RIGHT_X,
        SIDE_Y,
        SIDE_W,
        SIDE_H,
        side_right_on,
        mirror=True
    )
    

    pygame.display.flip()
    clock.tick(FPS)
    frame += 1

pygame.quit()




