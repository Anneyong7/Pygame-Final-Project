"""
Tic-Tac-Toe with Minimax AI
Python Programming - Pygame Final Project
Author: Kurt Ahron Dela Cruz
Game ID: G68
"""

import pygame
import sys
import math
import random

# ─── INIT ────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 600, 720
FPS = 60

# Colors
BG_COLOR       = (255, 255, 255)
GRID_COLOR     = (180, 180, 180)
X_COLOR        = (30, 100, 255)
O_COLOR        = (220, 40, 40)
WIN_LINE_COLOR = (34, 180, 34)
TEXT_COLOR     = (0, 0, 0)
DIM_TEXT       = (100, 100, 100)
BTN_COLOR      = (230, 230, 230)
BTN_HOVER      = (200, 200, 200)
BTN_BORDER     = (160, 160, 160)
SCORE_BG       = (240, 240, 240)

# Difficulty button accent colors
EASY_COLOR     = (34, 160, 34)     # green
NORMAL_COLOR   = (200, 140, 0)     # orange
HARD_COLOR     = (200, 30, 30)     # red

CELL_SIZE     = 160
GRID_ORIGIN_X = (SCREEN_W - CELL_SIZE * 3) // 2
GRID_ORIGIN_Y = 180
LINE_WIDTH    = 4
PIECE_PAD     = 28

# ─── SOUND ───────────────────────────────────────────────────────────────────
try:
    import numpy as np
    def make_sound(freq, dur, vol=0.35, wave="sine"):
        sr = 44100
        t = np.linspace(0, dur / 1000, int(sr * dur / 1000), False)
        sig = np.sin(2 * np.pi * freq * t) if wave == "sine" else np.sign(np.sin(2 * np.pi * freq * t))
        fade = np.ones_like(sig)
        fl = min(800, len(sig) // 4)
        fade[:fl] = np.linspace(0, 1, fl)
        fade[-fl:] = np.linspace(1, 0, fl)
        sig = (sig * fade * vol * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.column_stack([sig, sig]))

    SFX_PLACE_X = make_sound(440, 80)
    SFX_PLACE_O = make_sound(330, 80)
    SFX_WIN     = make_sound(660, 400)
    SFX_LOSE    = make_sound(180, 500, wave="square")
    SFX_DRAW    = make_sound(260, 300)
    SFX_CLICK   = make_sound(550, 50, vol=0.2)
    SOUNDS_OK   = True
except Exception:
    SOUNDS_OK = False

def play(sfx):
    if SOUNDS_OK:
        try: sfx.play()
        except: pass

# ─── FONTS ───────────────────────────────────────────────────────────────────
pygame.font.init()
FONT_TITLE = pygame.font.Font(None, 52)
FONT_LARGE = pygame.font.Font(None, 34)
FONT_MED   = pygame.font.Font(None, 26)
FONT_SMALL = pygame.font.Font(None, 20)

# ─── GAME LOGIC ──────────────────────────────────────────────────────────────
def empty_board():
    return [[None] * 3 for _ in range(3)]

def check_winner(board):
    lines = []
    for r in range(3): lines.append([(r,0),(r,1),(r,2)])
    for c in range(3): lines.append([(0,c),(1,c),(2,c)])
    lines += [[(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]]
    for line in lines:
        vals = [board[r][c] for r,c in line]
        if vals[0] and vals[0] == vals[1] == vals[2]:
            return vals[0], line
    return None, None

def is_full(board):
    return all(board[r][c] is not None for r in range(3) for c in range(3))

def minimax(board, is_maximizing, alpha=-math.inf, beta=math.inf):
    winner, _ = check_winner(board)
    if winner == "O": return 10
    if winner == "X": return -10
    if is_full(board): return 0
    if is_maximizing:
        best = -math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = "O"
                    best = max(best, minimax(board, False, alpha, beta))
                    board[r][c] = None
                    alpha = max(alpha, best)
                    if beta <= alpha: break
        return best
    else:
        best = math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = "X"
                    best = min(best, minimax(board, True, alpha, beta))
                    board[r][c] = None
                    beta = min(beta, best)
                    if beta <= alpha: break
        return best

def get_empty_cells(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]

def ai_move(board, difficulty):
    """
    easy   — fully random
    normal — 40% random, 60% minimax
    hard   — always minimax (unbeatable)
    """
    empty = get_empty_cells(board)
    if not empty:
        return None

    if difficulty == "easy":
        return random.choice(empty)

    elif difficulty == "normal":
        # 40% chance to play randomly
        if random.random() < 0.4:
            return random.choice(empty)
        else:
            return _best_minimax(board)

    else:  # hard
        return _best_minimax(board)

def _best_minimax(board):
    best_score = -math.inf
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] is None:
                board[r][c] = "O"
                score = minimax(board, False)
                board[r][c] = None
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move

# ─── DRAWING HELPERS ─────────────────────────────────────────────────────────
def cell_rect(row, col):
    return pygame.Rect(
        GRID_ORIGIN_X + col * CELL_SIZE,
        GRID_ORIGIN_Y + row * CELL_SIZE,
        CELL_SIZE, CELL_SIZE
    )

def draw_grid(surf):
    for i in range(1, 3):
        x = GRID_ORIGIN_X + i * CELL_SIZE
        pygame.draw.line(surf, GRID_COLOR, (x, GRID_ORIGIN_Y), (x, GRID_ORIGIN_Y + CELL_SIZE * 3), LINE_WIDTH)
        y = GRID_ORIGIN_Y + i * CELL_SIZE
        pygame.draw.line(surf, GRID_COLOR, (GRID_ORIGIN_X, y), (GRID_ORIGIN_X + CELL_SIZE * 3, y), LINE_WIDTH)
    pygame.draw.rect(surf, GRID_COLOR, (GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE * 3, CELL_SIZE * 3), LINE_WIDTH)

def draw_x(surf, row, col, alpha=255):
    r = cell_rect(row, col)
    pad = PIECE_PAD
    color = (*X_COLOR, alpha)
    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.line(s, color, (pad, pad), (CELL_SIZE-pad, CELL_SIZE-pad), 7)
    pygame.draw.line(s, color, (CELL_SIZE-pad, pad), (pad, CELL_SIZE-pad), 7)
    surf.blit(s, (r.x, r.y))

def draw_o(surf, row, col, alpha=255):
    r = cell_rect(row, col)
    color = (*O_COLOR, alpha)
    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2 - PIECE_PAD, 7)
    surf.blit(s, (r.x, r.y))

def draw_pieces(surf, board, anim_cell=None, anim_alpha=255):
    for r in range(3):
        for c in range(3):
            if board[r][c]:
                a = anim_alpha if anim_cell == (r,c) else 255
                if board[r][c] == "X": draw_x(surf, r, c, a)
                else: draw_o(surf, r, c, a)

def draw_win_line(surf, line, progress=1.0, color=WIN_LINE_COLOR):
    if not line: return
    r0,c0 = line[0]; r1,c1 = line[2]
    sx,sy = cell_rect(r0,c0).center
    ex,ey = cell_rect(r1,c1).center
    cx = sx + (ex-sx)*progress
    cy = sy + (ey-sy)*progress
    pygame.draw.line(surf, color, (sx,sy), (int(cx),int(cy)), 6)

def draw_button(surf, rect, text, hovered=False, accent=None, font=FONT_MED):
    color = BTN_HOVER if hovered else BTN_COLOR
    pygame.draw.rect(surf, color, rect, border_radius=8)
    border_color = accent if accent else BTN_BORDER
    pygame.draw.rect(surf, border_color, rect, 2, border_radius=8)
    label = font.render(text, True, accent if accent else TEXT_COLOR)
    surf.blit(label, label.get_rect(center=rect.center))

def draw_bg(surf):
    surf.fill(BG_COLOR)
    for i in range(0, SCREEN_W, 40):
        pygame.draw.line(surf, (220,220,220), (i,0), (i,SCREEN_H), 1)
    for j in range(0, SCREEN_H, 40):
        pygame.draw.line(surf, (220,220,220), (0,j), (SCREEN_W,j), 1)

def draw_text_centered(surf, text, font, color, y):
    label = font.render(text, True, color)
    surf.blit(label, label.get_rect(centerx=SCREEN_W//2, y=y))

# ─── SCREENS ─────────────────────────────────────────────────────────────────

class MenuScreen:
    def __init__(self, scores=None):
        self.scores   = scores if scores is not None else {"X": 0, "O": 0, "D": 0}
        self.btn_play  = pygame.Rect(200, 330, 200, 52)
        self.btn_inst  = pygame.Rect(200, 400, 200, 52)
        self.btn_exit  = pygame.Rect(200, 470, 200, 52)
        self.btn_reset = pygame.Rect(200, 540, 200, 40)
        self.tick = 0

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_play.collidepoint(event.pos):
                play(SFX_CLICK); return "difficulty"
            if self.btn_inst.collidepoint(event.pos):
                play(SFX_CLICK); return "instructions"
            if self.btn_exit.collidepoint(event.pos):
                pygame.quit(); sys.exit()
            if self.btn_reset.collidepoint(event.pos):
                play(SFX_CLICK)
                self.scores["X"] = 0
                self.scores["O"] = 0
                self.scores["D"] = 0
                return None
        return None

    def draw(self, surf):
        self.tick += 1
        draw_bg(surf)
        t1 = FONT_TITLE.render("TIC", True, X_COLOR)
        t2 = FONT_TITLE.render("TAC", True, TEXT_COLOR)
        t3 = FONT_TITLE.render("TOE", True, O_COLOR)
        tw = t1.get_width() + t2.get_width() + t3.get_width() + 24
        sx = (SCREEN_W - tw) // 2
        y  = 80 + int(math.sin(self.tick * 0.03) * 6)
        surf.blit(t1, (sx, y))
        surf.blit(t2, (sx + t1.get_width() + 12, y))
        surf.blit(t3, (sx + t1.get_width() + t2.get_width() + 24, y))
        draw_text_centered(surf, "Player 1 vs Player 2", FONT_SMALL, DIM_TEXT, y+64)

        # ── Score board ──────────────────────────────────────────────────────
        board_rect = pygame.Rect(80, 168, SCREEN_W - 160, 130)
        pygame.draw.rect(surf, SCORE_BG, board_rect, border_radius=10)
        pygame.draw.rect(surf, BTN_BORDER, board_rect, 2, border_radius=10)

        draw_text_centered(surf, "SCOREBOARD", FONT_SMALL, DIM_TEXT, 176)

        # Player 1
        p1_lbl = FONT_LARGE.render(f"Player 1 (X)", True, X_COLOR)
        p1_pts = FONT_LARGE.render(f"{self.scores['X']} pts", True, X_COLOR)
        surf.blit(p1_lbl, p1_lbl.get_rect(midleft=(board_rect.x + 16, 212)))
        surf.blit(p1_pts, p1_pts.get_rect(midright=(board_rect.right - 16, 212)))

        # Divider
        mid_y = 234
        pygame.draw.line(surf, BTN_BORDER, (board_rect.x + 12, mid_y), (board_rect.right - 12, mid_y), 1)

        # Player 2
        p2_lbl = FONT_LARGE.render(f"Player 2 (O)", True, O_COLOR)
        p2_pts = FONT_LARGE.render(f"{self.scores['O']} pts", True, O_COLOR)
        surf.blit(p2_lbl, p2_lbl.get_rect(midleft=(board_rect.x + 16, 256)))
        surf.blit(p2_pts, p2_pts.get_rect(midright=(board_rect.right - 16, 256)))

        # Draws (small, bottom right of card)
        draw_lbl = FONT_SMALL.render(f"Draws: {self.scores['D']}", True, DIM_TEXT)
        surf.blit(draw_lbl, draw_lbl.get_rect(midright=(board_rect.right - 10, board_rect.bottom - 10)))

        mx, my = pygame.mouse.get_pos()
        draw_button(surf, self.btn_play,  "PLAY",        self.btn_play.collidepoint(mx,my))
        draw_button(surf, self.btn_inst,  "HOW TO PLAY", self.btn_inst.collidepoint(mx,my))
        draw_button(surf, self.btn_exit,  "EXIT",        self.btn_exit.collidepoint(mx,my))
        draw_button(surf, self.btn_reset, "RESET SCORES", self.btn_reset.collidepoint(mx,my), font=FONT_SMALL)
        draw_text_centered(surf, "Player 1 is X   |   Player 2 is O", FONT_SMALL, DIM_TEXT, 598)
        draw_text_centered(surf, "First to align 3 wins!", FONT_SMALL, DIM_TEXT, 618)


class DifficultyScreen:
    def __init__(self):
        self.btn_easy   = pygame.Rect(175, 280, 250, 64)
        self.btn_normal = pygame.Rect(175, 370, 250, 64)
        self.btn_hard   = pygame.Rect(175, 460, 250, 64)
        self.btn_back   = pygame.Rect(200, 570, 200, 48)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_easy.collidepoint(event.pos):
                play(SFX_CLICK); return "easy"
            if self.btn_normal.collidepoint(event.pos):
                play(SFX_CLICK); return "normal"
            if self.btn_hard.collidepoint(event.pos):
                play(SFX_CLICK); return "hard"
            if self.btn_back.collidepoint(event.pos):
                play(SFX_CLICK); return "menu"
        return None

    def draw(self, surf):
        draw_bg(surf)
        draw_text_centered(surf, "SELECT DIFFICULTY", FONT_LARGE, TEXT_COLOR, 80)
        draw_text_centered(surf, "How tough do you want Player 2?", FONT_SMALL, DIM_TEXT, 130)

        mx, my = pygame.mouse.get_pos()

        # Easy
        draw_button(surf, self.btn_easy, "EASY",
                    self.btn_easy.collidepoint(mx,my), EASY_COLOR, FONT_LARGE)
        draw_text_centered(surf, "Player 2 plays randomly", FONT_SMALL, DIM_TEXT, self.btn_easy.bottom + 4)

        # Normal
        draw_button(surf, self.btn_normal, "NORMAL",
                    self.btn_normal.collidepoint(mx,my), NORMAL_COLOR, FONT_LARGE)
        draw_text_centered(surf, "Player 2 makes some mistakes", FONT_SMALL, DIM_TEXT, self.btn_normal.bottom + 4)

        # Hard
        draw_button(surf, self.btn_hard, "HARD",
                    self.btn_hard.collidepoint(mx,my), HARD_COLOR, FONT_LARGE)
        draw_text_centered(surf, "Player 2 is unbeatable", FONT_SMALL, DIM_TEXT, self.btn_hard.bottom + 4)

        draw_button(surf, self.btn_back, "BACK", self.btn_back.collidepoint(mx,my))


class InstructionsScreen:
    def __init__(self):
        self.btn_back = pygame.Rect(200, 620, 200, 48)

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_back.collidepoint(event.pos):
                play(SFX_CLICK); return "menu"
        return None

    def draw(self, surf):
        draw_bg(surf)
        draw_text_centered(surf, "HOW TO PLAY", FONT_LARGE, TEXT_COLOR, 60)
        lines = [
            ("P1",    "Player 1 is  X  (Blue)"),
            ("P2",    "Player 2 is  O  (Red)"),
            ("TURN",  "Click any empty cell to place your X"),
            ("WIN",   "Get 3 in a row: horizontal,"),
            ("",      "vertical, or diagonal"),
            ("DRAW",  "All 9 cells filled = Draw"),
            ("DIFF",  "Choose Easy / Normal / Hard"),
            ("",      "before each game"),
            ("SCORE", "Tracked across rounds"),
        ]
        y = 140
        for label, text in lines:
            if label:
                lbl = FONT_SMALL.render(f"[ {label} ]", True, X_COLOR)
                surf.blit(lbl, (60, y))
            txt = FONT_SMALL.render(text, True, TEXT_COLOR)
            surf.blit(txt, (180, y))
            y += 36
        mx, my = pygame.mouse.get_pos()
        draw_button(surf, self.btn_back, "BACK", self.btn_back.collidepoint(mx,my))


class GameScreen:
    def __init__(self, scores, difficulty):
        self.board      = empty_board()
        self.difficulty = difficulty
        self.current_turn = "X"
        self.winner     = None
        self.win_line   = None
        self.game_over  = False
        self.is_draw    = False
        self.scores     = scores

        self.ai_delay   = 0
        self.anim_cell  = None
        self.anim_alpha = 0
        self.win_progress = 0.0

        # always-visible bottom buttons (during gameplay)
        self.btn_menu   = pygame.Rect(60,  660, 180, 44)
        self.btn_replay = pygame.Rect(360, 660, 180, 44)

        # game-over overlay buttons
        self.btn_play_again = pygame.Rect(100, 580, 180, 52)
        self.btn_go_menu    = pygame.Rect(320, 580, 180, 52)

        # difficulty label colors
        self.diff_color = {"easy": EASY_COLOR, "normal": NORMAL_COLOR, "hard": HARD_COLOR}[difficulty]
        self.diff_label = difficulty.upper()

    def pixel_to_cell(self, px, py):
        col = (px - GRID_ORIGIN_X) // CELL_SIZE
        row = (py - GRID_ORIGIN_Y) // CELL_SIZE
        if 0 <= row < 3 and 0 <= col < 3:
            return row, col
        return None

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # game-over overlay buttons
            if self.game_over:
                if self.btn_play_again.collidepoint(mx, my):
                    play(SFX_CLICK); return "restart"
                if self.btn_go_menu.collidepoint(mx, my):
                    play(SFX_CLICK); return "menu"
                return None
            # in-game buttons
            if self.btn_menu.collidepoint(mx, my):
                play(SFX_CLICK); return "menu"
            if self.btn_replay.collidepoint(mx, my):
                play(SFX_CLICK); return "restart"
            if not self.game_over and self.current_turn == "X" and self.ai_delay == 0:
                cell = self.pixel_to_cell(mx, my)
                if cell:
                    r, c = cell
                    if self.board[r][c] is None:
                        self.place(r, c, "X")
        return None

    def place(self, r, c, piece):
        self.board[r][c] = piece
        self.anim_cell   = (r, c)
        self.anim_alpha  = 0
        play(SFX_PLACE_X if piece == "X" else SFX_PLACE_O)

        winner, line = check_winner(self.board)
        if winner:
            self.winner    = winner
            self.win_line  = line
            self.game_over = True
            self.scores[winner] += 1
            play(SFX_WIN if winner == "X" else SFX_LOSE)
        elif is_full(self.board):
            self.is_draw   = True
            self.game_over = True
            self.scores["D"] += 1
            play(SFX_DRAW)
        else:
            self.current_turn = "O" if piece == "X" else "X"
            if self.current_turn == "O":
                self.ai_delay = 45

    def update(self):
        if self.anim_cell and self.anim_alpha < 255:
            self.anim_alpha = min(255, self.anim_alpha + 25)
        if self.game_over and self.win_line and self.win_progress < 1.0:
            self.win_progress = min(1.0, self.win_progress + 0.06)
        if not self.game_over and self.current_turn == "O" and self.ai_delay > 0:
            self.ai_delay -= 1
            if self.ai_delay == 0:
                move = ai_move(self.board, self.difficulty)
                if move:
                    self.place(move[0], move[1], "O")

    def draw(self, surf):
        draw_bg(surf)

        # score bar
        pygame.draw.rect(surf, SCORE_BG, (0, 0, SCREEN_W, 80))
        sx_label = FONT_MED.render(f"PLAYER 1 (X): {self.scores['X']}", True, X_COLOR)
        d_label  = FONT_MED.render(f"DRAW: {self.scores['D']}", True, DIM_TEXT)
        ai_label = FONT_MED.render(f"PLAYER 2 (O): {self.scores['O']}", True, O_COLOR)
        surf.blit(sx_label, sx_label.get_rect(midleft=(10, 40)))
        surf.blit(d_label,  d_label.get_rect(center=(SCREEN_W//2, 40)))
        surf.blit(ai_label, ai_label.get_rect(midright=(SCREEN_W-10, 40)))

        # difficulty badge
        badge = FONT_SMALL.render(self.diff_label, True, self.diff_color)
        badge_rect = badge.get_rect(topright=(SCREEN_W - 10, 4))
        surf.blit(badge, badge_rect)

        # turn / result
        if not self.game_over:
            if self.current_turn == "X":
                turn_text, turn_color = "PLAYER 1 TURN", X_COLOR
            else:
                turn_text  = "PLAYER 2 THINKING..." if self.ai_delay > 0 else "PLAYER 2 TURN"
                turn_color = O_COLOR
            draw_text_centered(surf, turn_text, FONT_MED, turn_color, 95)
        else:
            if self.winner == "X":
                msg, col = "PLAYER 1 WINS!", (34, 180, 34)
            elif self.winner == "O":
                msg, col = "PLAYER 2 WINS!", (220, 40, 40)
            else:
                msg, col = "DRAW!", (100, 100, 100)
            draw_text_centered(surf, msg, FONT_LARGE, col, 90)

        draw_grid(surf)

        anim_alpha = self.anim_alpha if self.anim_cell else 255
        draw_pieces(surf, self.board, self.anim_cell, anim_alpha)

        if not self.game_over and self.current_turn == "X":
            mx, my = pygame.mouse.get_pos()
            cell = self.pixel_to_cell(mx, my)
            if cell:
                r, c = cell
                if self.board[r][c] is None:
                    rect = cell_rect(r, c)
                    hl = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(hl, (30, 100, 255, 20), hl.get_rect())
                    surf.blit(hl, rect.topleft)

        mx, my = pygame.mouse.get_pos()

        if self.game_over:
            # dim overlay over the board
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (255, 255, 255, 200),
                             (60, 530, 480, 130), border_radius=12)
            pygame.draw.rect(overlay, (180, 180, 180, 255),
                             (60, 530, 480, 130), 2, border_radius=12)
            surf.blit(overlay, (0, 0))

            # draw win line ON TOP of the overlay so it stays visible
            if self.win_line:
                line_color = (34, 180, 34) if self.winner == "X" else (220, 40, 40)
                draw_win_line(surf, self.win_line, self.win_progress, line_color)

            draw_button(surf, self.btn_play_again, "PLAY AGAIN",
                        self.btn_play_again.collidepoint(mx, my), EASY_COLOR, FONT_MED)
            draw_button(surf, self.btn_go_menu, "MENU",
                        self.btn_go_menu.collidepoint(mx, my), None, FONT_MED)
        else:
            draw_button(surf, self.btn_menu,   "MENU",   self.btn_menu.collidepoint(mx, my))
            draw_button(surf, self.btn_replay, "REPLAY", self.btn_replay.collidepoint(mx, my))


# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def main():
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Tic-Tac-Toe  |  Kurt Ahron Dela Cruz")
    clock  = pygame.time.Clock()

    scores     = {"X": 0, "O": 0, "D": 0}
    difficulty = "normal"   # default, updated when player picks
    current_screen = MenuScreen(scores)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            result = current_screen.handle(event)

            if result == "difficulty":
                current_screen = DifficultyScreen()
            elif result in ("easy", "normal", "hard"):
                difficulty = result
                current_screen = GameScreen(scores, difficulty)
            elif result == "menu":
                current_screen = MenuScreen(scores)
            elif result == "instructions":
                current_screen = InstructionsScreen()
            elif result == "restart":
                current_screen = DifficultyScreen()  # pick difficulty again on replay

        if hasattr(current_screen, "update"):
            current_screen.update()

        current_screen.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
