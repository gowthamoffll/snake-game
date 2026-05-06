import pygame
import random
import sys
import math

pygame.init()

# ── Layout ──────────────────────────────────────────────────────────────────
CELL      = 24
COLS      = 25
ROWS      = 25
HUD_H     = 56
BORDER    = 4
PX_W      = COLS * CELL
PX_H      = ROWS * CELL
WIN_W     = PX_W + BORDER * 2
WIN_H     = PX_H + BORDER * 2 + HUD_H
FPS       = 10

# ── Colour palette (Nokia greenscreen inspired) ──────────────────────────────
BG_DARK      = (10,  20,  10)
BG_CELL_A    = (14,  28,  14)
BG_CELL_B    = (12,  24,  12)
BORDER_COL   = (30,  80,  30)
BORDER_SHINE = (60, 160,  60)

SNAKE_BODY   = (60, 200,  60)
SNAKE_SHADE  = (30, 130,  30)
SNAKE_HEAD   = (80, 230,  80)
SNAKE_EYE    = (230, 255, 230)
SNAKE_PUPIL  = (10,  40,  10)
SNAKE_TONGUE = (220,  60,  60)

APPLE_RED    = (220,  50,  40)
APPLE_DARK   = (160,  20,  20)
APPLE_SHINE  = (255, 180, 160)
APPLE_STEM   = (100,  70,  30)
APPLE_LEAF   = (60,  180,  60)

HUD_BG       = (6,   14,   6)
HUD_TEXT     = (100, 230, 100)
HUD_DIM      = (40,  100,  40)

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

def load_font(size, bold=False):
    for name in ("Courier New", "Lucida Console", "monospace"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)

font_hud   = load_font(22, bold=True)
font_title = load_font(56, bold=True)
font_sub   = load_font(22)

# ── Helpers ──────────────────────────────────────────────────────────────────
def cell_rect(gx, gy):
    return pygame.Rect(BORDER + gx * CELL, HUD_H + BORDER + gy * CELL, CELL, CELL)

def cell_center(gx, gy):
    r = cell_rect(gx, gy)
    return r.centerx, r.centery

# ── Background surface (built once) ──────────────────────────────────────────
_bg_surf = pygame.Surface((WIN_W, WIN_H))
_bg_surf.fill(BG_DARK)
for gy in range(ROWS):
    for gx in range(COLS):
        col = BG_CELL_A if (gx + gy) % 2 == 0 else BG_CELL_B
        pygame.draw.rect(_bg_surf, col, cell_rect(gx, gy))
full_border = pygame.Rect(BORDER, HUD_H + BORDER, PX_W, PX_H)
pygame.draw.rect(_bg_surf, BORDER_COL, full_border, BORDER)
pygame.draw.line(_bg_surf, BORDER_SHINE,
                 (BORDER, HUD_H + BORDER), (BORDER + PX_W, HUD_H + BORDER), 1)
pygame.draw.line(_bg_surf, BORDER_SHINE,
                 (BORDER, HUD_H + BORDER), (BORDER, HUD_H + BORDER + PX_H), 1)

# ── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(score, high):
    pygame.draw.rect(screen, HUD_BG, (0, 0, WIN_W, HUD_H))
    pygame.draw.line(screen, BORDER_COL, (0, HUD_H - 1), (WIN_W, HUD_H - 1), 1)
    screen.blit(font_hud.render("SCORE", True, HUD_DIM), (16, 8))
    screen.blit(font_hud.render(str(score), True, HUD_TEXT), (16, 28))
    bw = font_hud.size("BEST")[0]
    screen.blit(font_hud.render("BEST",  True, HUD_DIM),  (WIN_W - bw - 16, 8))
    screen.blit(font_hud.render(str(high), True, HUD_TEXT),(WIN_W - bw - 16, 28))
    t = font_hud.render("SNAKE", True, HUD_TEXT)
    screen.blit(t, t.get_rect(centerx=WIN_W // 2, top=18))

# ── Apple ────────────────────────────────────────────────────────────────────
def draw_apple(gx, gy, tick):
    cx, cy = cell_center(gx, gy)
    r = CELL // 2 - 2 + int(math.sin(tick * 0.18) * 1.5)
    pygame.draw.circle(screen, APPLE_RED,   (cx, cy + 1), r)
    pygame.draw.circle(screen, APPLE_DARK,  (cx, cy + 1), r, 2)
    pygame.draw.circle(screen, APPLE_SHINE, (cx - r//3, cy - r//3), max(r//4, 2))
    pygame.draw.line(screen, APPLE_STEM, (cx, cy - r + 1), (cx + 3, cy - r - 5), 2)
    pygame.draw.ellipse(screen, APPLE_LEAF,
                        pygame.Rect(cx + 3, cy - r - 6, 8, 5))

# ── Snake drawing ─────────────────────────────────────────────────────────────
def draw_body_segment(gx, gy, prev_cell, next_cell):
    cx, cy = cell_center(gx, gy)
    half = CELL // 2 - 2
    dirs = set()
    if prev_cell: dirs.add((prev_cell[0] - gx, prev_cell[1] - gy))
    if next_cell: dirs.add((next_cell[0]  - gx, next_cell[1]  - gy))
    for ddx, ddy in dirs:
        rx = cx + ddx * half // 2
        ry = cy + ddy * half // 2
        rw = half * 2 if ddy == 0 else half - 1
        rh = half * 2 if ddx == 0 else half - 1
        pygame.draw.rect(screen, SNAKE_BODY,
                         pygame.Rect(rx - rw // 2, ry - rh // 2, rw, rh))
    pygame.draw.circle(screen, SNAKE_BODY,  (cx, cy), half)
    pygame.draw.circle(screen, SNAKE_SHADE, (cx, cy), half, 2)
    pygame.draw.circle(screen, SNAKE_HEAD,  (cx - half//3, cy - half//3), max(half//4, 2))

def draw_tail(gx, gy, prev_cell):
    cx, cy = cell_center(gx, gy)
    pdx, pdy = prev_cell[0] - gx, prev_cell[1] - gy
    half = CELL // 2 - 4
    pygame.draw.circle(screen, SNAKE_BODY,  (cx, cy), half)
    pygame.draw.circle(screen, SNAKE_SHADE, (cx, cy), half, 1)
    rx = cx + pdx * half // 2
    ry = cy + pdy * half // 2
    rw = half * 2 if pdy == 0 else half - 1
    rh = half * 2 if pdx == 0 else half - 1
    pygame.draw.rect(screen, SNAKE_BODY,
                     pygame.Rect(rx - rw // 2, ry - rh // 2, rw, rh))

def draw_head(gx, gy, direction, tick):
    cx, cy = cell_center(gx, gy)
    half = CELL // 2 - 1
    dx, dy = direction
    pygame.draw.circle(screen, SNAKE_HEAD,  (cx, cy), half)
    pygame.draw.circle(screen, SNAKE_SHADE, (cx, cy), half, 2)
    # Eyes
    if dx != 0:
        eye_offsets = [(dx * half // 2, -half // 2 + 2),
                       (dx * half // 2,  half // 2 - 2)]
    else:
        eye_offsets = [(-half // 2 + 2, dy * half // 2),
                       ( half // 2 - 2, dy * half // 2)]
    for ox, oy in eye_offsets:
        ex, ey = cx + ox, cy + oy
        pygame.draw.circle(screen, SNAKE_EYE,   (ex, ey), 4)
        pygame.draw.circle(screen, SNAKE_PUPIL, (ex + dx, ey + dy), 2)
    # Tongue flick
    if tick % 12 < 6:
        base_x = cx + dx * (half - 2)
        base_y = cy + dy * (half - 2)
        tip_x  = cx + dx * (half + 5)
        tip_y  = cy + dy * (half + 5)
        pygame.draw.line(screen, SNAKE_TONGUE, (base_x, base_y), (tip_x, tip_y), 2)
        pygame.draw.line(screen, SNAKE_TONGUE,
                         (tip_x, tip_y), (tip_x + dx*4 + dy*3, tip_y + dy*4 + dx*3), 1)
        pygame.draw.line(screen, SNAKE_TONGUE,
                         (tip_x, tip_y), (tip_x + dx*4 - dy*3, tip_y + dy*4 - dx*3), 1)

def draw_snake(snake, direction, tick):
    n = len(snake)
    for i in range(n - 1, 0, -1):
        prev_c = snake[i - 1] if i > 0     else None
        next_c = snake[i + 1] if i < n - 1 else None
        if i == n - 1:
            draw_tail(snake[i][0], snake[i][1], snake[i - 1])
        else:
            draw_body_segment(snake[i][0], snake[i][1], prev_c, next_c)
    draw_head(snake[0][0], snake[0][1], direction, tick)

# ── Death flash ───────────────────────────────────────────────────────────────
def death_flash(snake, score, high):
    for f in range(6):
        screen.blit(_bg_surf, (0, 0))
        draw_hud(score, high)
        if f % 2 == 0:
            for gx, gy in snake:
                r = cell_rect(gx, gy).inflate(-4, -4)
                pygame.draw.rect(screen, (200, 50, 50), r, border_radius=6)
        pygame.display.flip()
        pygame.time.delay(80)

# ── Menu screen ───────────────────────────────────────────────────────────────
def show_screen(title, lines):
    overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(_bg_surf, (0, 0))
    screen.blit(overlay, (0, 0))
    t = font_title.render(title, True, SNAKE_HEAD)
    screen.blit(t, t.get_rect(center=(WIN_W // 2, WIN_H // 2 - 60)))
    for i, line in enumerate(lines):
        s = font_sub.render(line, True, HUD_TEXT)
        screen.blit(s, s.get_rect(center=(WIN_W // 2, WIN_H // 2 + 10 + i * 30)))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return

# ── Place food ────────────────────────────────────────────────────────────────
def place_food(snake):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            return pos

# ── Main game loop ────────────────────────────────────────────────────────────
def game_loop(high):
    snake     = [(COLS // 2, ROWS // 2)]
    direction = (1, 0)
    next_dir  = direction
    food      = place_food(snake)
    score     = 0
    tick      = 0

    while True:
        clock.tick(FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direction != (0,  1): next_dir = (0, -1)
                if event.key == pygame.K_DOWN  and direction != (0, -1): next_dir = (0,  1)
                if event.key == pygame.K_LEFT  and direction != (1,  0): next_dir = (-1, 0)
                if event.key == pygame.K_RIGHT and direction != (-1, 0): next_dir = (1,  0)
                if event.key == pygame.K_ESCAPE: return score

        direction = next_dir
        hx, hy   = snake[0]
        dx, dy   = direction
        new_head  = ((hx + dx) % COLS, (hy + dy) % ROWS)

        if new_head in snake:
            death_flash(snake, score, max(score, high))
            return score

        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = place_food(snake)
        else:
            snake.pop()

        screen.blit(_bg_surf, (0, 0))
        draw_hud(score, max(score, high))
        draw_apple(food[0], food[1], tick)
        draw_snake(snake, direction, tick)
        pygame.display.flip()

def main():
    high = 0
    show_screen("SNAKE", ["Arrow keys  ·  move", "SPACE  ·  start"])
    while True:
        score = game_loop(high)
        high  = max(score, high)
        show_screen("GAME OVER",
                    [f"Score : {score}",
                     f"Best  : {high}",
                     "SPACE  ·  play again"])

if __name__ == "__main__":
    main()
