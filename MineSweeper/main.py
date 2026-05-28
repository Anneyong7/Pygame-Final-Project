import pygame
import random
import sys

# ==============================================================================
# 1. INITIALIZATION & CONFIGURATION 
# ==============================================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

# Default Window Dimensions
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

# Fetch system native monitor dimensions for fullscreen scaling
info = pygame.display.Info()
FULLSCREEN_WIDTH = info.current_w
FULLSCREEN_HEIGHT = info.current_h

# Global Layout Variables (will update dynamically based on screen mode)
SCREEN_WIDTH = WINDOW_WIDTH
SCREEN_HEIGHT = WINDOW_HEIGHT

# Start up in Windowed mode by default
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")

is_fullscreen = False
clock = pygame.time.Clock()
FPS = 60

# Fonts
font_small = pygame.font.SysFont("Arial", 18, bold=True)
font_medium = pygame.font.SysFont("Arial", 28, bold=True)
font_large = pygame.font.SysFont("Arial", 52, bold=True)

# Creative Palette Design
COLOR_BG = (30, 30, 40)
COLOR_TEXT = (240, 240, 245)
COLOR_TEXT_MUTED = (140, 150, 160)
COLOR_TILE_HIDDEN = (90, 100, 110)
COLOR_TILE_REVEALED = (160, 165, 170)
COLOR_GRID_LINE = (45, 45, 55)
COLOR_BUTTON = (55, 120, 180)
COLOR_BUTTON_HOVER = (85, 150, 210)
COLOR_TOGGLE_BTN = (40, 160, 110)
COLOR_TOGGLE_HOVER = (60, 190, 130)

NUM_COLORS = {
    1: (40, 90, 230), 2: (30, 150, 30), 3: (220, 40, 40),
    4: (20, 20, 130), 5: (130, 20, 20), 6: (20, 130, 130)
}

# Game States System
STATE_MENU = "menu"
STATE_INSTRUCTIONS = "instructions"
STATE_SETTINGS = "settings"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAMEOVER = "gameover"
STATE_WIN = "win"
current_state = STATE_MENU
previous_state = STATE_MENU  

# Global Game Settings
music_enabled = True
difficulty = "Medium"  

# Difficulty Definitions: (rows, cols, mines, cell_size)
DIFFICULTIES = {
    "Easy": (9, 9, 10, 50),
    "Medium": (12, 16, 20, 42),
    "Hard": (16, 30, 99, 30)
}

# ==============================================================================
# 2. AUDIO GENERATION
# ==============================================================================
def create_sound(freq, duration, type="sine"):
    try:
        import numpy as np
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        if type == "noise":
            buf = np.random.uniform(-1, 1, n_samples)
        else:
            t = np.linspace(0, duration, n_samples, False)
            buf = np.sin(freq * t * 2 * np.pi)
        audio = (buf * 14000).astype(np.int16)
        return pygame.sndarray.make_sound(np.repeat(audio[:, np.newaxis], 2, axis=1))
    except:
        return None

sound_click = create_sound(580, 0.06)
sound_explosion = create_sound(90, 0.4, type="noise")
sound_win = create_sound(520, 0.3)

MUSIC_NOTES = [130.81, 146.83, 164.81, 146.83, 130.81, 164.81, 196.00, 164.81]
music_channel = pygame.mixer.Channel(7)
music_timer = 0
note_index = 0

def update_background_music():
    global music_timer, note_index
    if not music_enabled:
        return

    if current_state == STATE_PLAYING:
        if music_timer % 40 == 0:
            note = create_sound(MUSIC_NOTES[note_index], 0.3, type="sine")
            if note:
                note.set_volume(0.12)
                music_channel.play(note)
            note_index = (note_index + 1) % len(MUSIC_NOTES)
        music_timer += 1
    else:
        music_timer = 0

# ==============================================================================
# 3. GAME OBJECTS & DYNAMIC LAYOUT RECALCULATION
# ==============================================================================
class MinesweeperEngine:
    def __init__(self, diff_name):
        self.change_difficulty(diff_name)

    def change_difficulty(self, diff_name):
        rows, cols, mines, cell_size = DIFFICULTIES[diff_name]
        self.rows = rows
        self.cols = cols
        self.num_mines = mines
        self.cell_size = cell_size
        self.recenter_board()
        self.reset()

    def recenter_board(self):
        self.start_x = (SCREEN_WIDTH - (self.cols * self.cell_size)) // 2
        self.start_y = (SCREEN_HEIGHT - (self.rows * self.cell_size)) // 2 + 40

    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines_placed = False
        self.score = 0

    def place_mines(self, safe_r, safe_col):
        mines_left = self.num_mines
        while mines_left > 0:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.grid[r][c] != -1 and (r != safe_r or c != safe_col):
                self.grid[r][c] = -1
                mines_left -= 1

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1: continue
                count = 0
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] == -1:
                            count += 1
                self.grid[r][c] = count
        self.mines_placed = True

    def handle_click(self, mouse_pos, is_right_click):
        mx, my = mouse_pos
        if not (self.start_x <= mx < self.start_x + self.cols * self.cell_size and
                self.start_y <= my < self.start_y + self.rows * self.cell_size):
            return "continue"

        c = (mx - self.start_x) // self.cell_size
        r = (my - self.start_y) // self.cell_size

        if is_right_click:
            if not self.revealed[r][c]:
                self.flagged[r][c] = not self.flagged[r][c]
                if sound_click: sound_click.play()
            return "continue"

        if self.flagged[r][c] or self.revealed[r][c]: 
            return "continue"
        
        if not self.mines_placed:
            self.place_mines(r, c)

        if self.grid[r][c] == -1:
            if sound_explosion: sound_explosion.play()
            self.reveal_all()
            return "lose"

        if sound_click: sound_click.play()
        self.reveal_cell(r, c)
        return "win" if self.check_win() else "continue"

    def reveal_cell(self, r, c):
        if self.revealed[r][c]: return
        self.revealed[r][c] = True
        self.score += 10
        if self.grid[r][c] == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        if not self.revealed[nr][nc] and not self.flagged[nr][nc]:
                            self.reveal_cell(nr, nc)

    def reveal_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1: self.revealed[r][c] = True

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1 and not self.revealed[r][c]:
                    return False
        if sound_win: sound_win.play()
        return True

    def draw(self, surface):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.start_x + c * self.cell_size
                y = self.start_y + r * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                if self.revealed[r][c]:
                    pygame.draw.rect(surface, COLOR_TILE_REVEALED, rect)
                    if self.grid[r][c] == -1:
                        pygame.draw.circle(surface, (220, 50, 50), rect.center, self.cell_size // 4)
                    elif self.grid[r][c] > 0:
                        txt = font_small.render(str(self.grid[r][c]), True, NUM_COLORS.get(self.grid[r][c], COLOR_TEXT))
                        surface.blit(txt, txt.get_rect(center=rect.center))
                else:
                    pygame.draw.rect(surface, COLOR_TILE_HIDDEN, rect)
                    if self.flagged[r][c]:
                        pygame.draw.polygon(surface, (230, 60, 60), [
                            (rect.centerx - 4, rect.top + 10),
                            (rect.centerx + 10, rect.top + 17),
                            (rect.centerx - 4, rect.top + 24)
                        ])
                        pygame.draw.line(surface, COLOR_TEXT, (rect.centerx - 4, rect.top + 10), (rect.centerx - 4, rect.bottom - 10), 2)

                pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)


engine = MinesweeperEngine(difficulty)

# ==============================================================================
# 4. INTERACTIVE UI UTILITIES & DISPLAY EVENT CONTROLLER
# ==============================================================================
def toggle_screen_mode():
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, is_fullscreen
    is_fullscreen = not is_fullscreen
    
    if is_fullscreen:
        SCREEN_WIDTH = FULLSCREEN_WIDTH
        SCREEN_HEIGHT = FULLSCREEN_HEIGHT
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        SCREEN_WIDTH = WINDOW_WIDTH
        SCREEN_HEIGHT = WINDOW_HEIGHT
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
    engine.recenter_board()

def draw_button(surface, text, x, y, w, h, base_color, hover_color, current_event=None):
    """Renders button and checks mouse position. Returns True ONLY on a unique MOUSEBUTTONDOWN event."""
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    clicked = False
    
    # Check Hover Status
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, hover_color, rect, border_radius=6)
        # Verify if an explicit mouse down event hit this coordinate box
        if current_event and current_event.type == pygame.MOUSEBUTTONDOWN and current_event.button == 1:
            clicked = True
    else:
        pygame.draw.rect(surface, base_color, rect, border_radius=6)

    txt_surf = font_medium.render(text, True, COLOR_TEXT)
    surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))
    return clicked

# ==============================================================================
# 5. CORE SYSTEM LOOPS
# ==============================================================================
running = True

while running:
    update_background_music()
    screen.fill(COLOR_BG)

    active_click_event = None

    # --------------------------------------------------------------------------
    # EVENT MANAGER CHANNELS
    # --------------------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggle_screen_mode()
            elif event.key == pygame.K_ESCAPE:
                if current_state == STATE_MENU:
                    running = False
                elif current_state == STATE_PLAYING:
                    current_state = STATE_PAUSED
                elif current_state == STATE_PAUSED:
                    current_state = STATE_PLAYING
                elif current_state == STATE_SETTINGS:
                    current_state = previous_state  
                else:
                    current_state = STATE_MENU

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Capture the single distinct mouse click down for button checks below
            active_click_event = event
            
            if current_state == STATE_PLAYING:
                status = "continue"
                if event.button == 1:
                    status = engine.handle_click(event.pos, is_right_click=False)
                elif event.button == 3:
                    status = engine.handle_click(event.pos, is_right_click=True)

                if status == "lose":   current_state = STATE_GAMEOVER
                elif status == "win":  current_state = STATE_WIN

    # --------------------------------------------------------------------------
    # STATE MANAGER WINDOWS
    # --------------------------------------------------------------------------
    
    # STATE 1: START MENU
    if current_state == STATE_MENU:
        title = font_large.render("MINESWEEPER", True, COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))

        if draw_button(screen, "PLAY GAME", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            engine.reset()
            current_state = STATE_PLAYING

        if draw_button(screen, "SETTINGS", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 25, 300, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            previous_state = STATE_MENU
            current_state = STATE_SETTINGS

        if draw_button(screen, "HOW TO PLAY", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            current_state = STATE_INSTRUCTIONS

        if draw_button(screen, "EXIT GAME", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 125, 300, 55, (170, 55, 55), (200, 85, 85), active_click_event):
            running = False
            
        # Top right scaling button
        label = "WINDOW MODE" if is_fullscreen else "FULLSCREEN"
        if draw_button(screen, label, SCREEN_WIDTH - 230, 25, 200, 45, COLOR_TOGGLE_BTN, COLOR_TOGGLE_HOVER, active_click_event):
            toggle_screen_mode()

    # STATE 2: GAME INSTRUCTIONS
    elif current_state == STATE_INSTRUCTIONS:
        title = font_large.render("GAME INSTRUCTIONS", True, COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))

        instructions = [
            "* LEFT-CLICK on any tile on the board grid to reveal it.",
            "* RIGHT-CLICK on any tile to place or pick up a red hazard Flag.",
            "* Numbers indicate exactly how many hidden mines touch that block.",
            "* Avoid clicking on explosive Mine obstacles buried in the field!",
            "* Clear all safe map fields entirely to secure objective victory.",
            "Click the button below or press 'ESC' to return to the Main Menu."
        ]
        
        y_offset = SCREEN_HEIGHT // 3 + 20
        for line in instructions:
            text = font_small.render(line, True, COLOR_TEXT if not line.startswith("Click") else (55, 200, 100))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, y_offset)))
            y_offset += 45

        if draw_button(screen, "BACK TO MENU", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 120, 240, 50, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            current_state = STATE_MENU

    # STATE 3: SETTINGS MENU
    elif current_state == STATE_SETTINGS:
        title = font_large.render("SETTINGS", True, COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)))

        diff_label = font_medium.render(f"Difficulty: {difficulty}", True, COLOR_TEXT_MUTED)
        screen.blit(diff_label, diff_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))

        x_start = SCREEN_WIDTH // 2 - 230
        for idx, opt in enumerate(["Easy", "Medium", "Hard"]):
            btn_color = COLOR_TOGGLE_BTN if difficulty == opt else COLOR_BUTTON
            hover_color = COLOR_TOGGLE_HOVER if difficulty == opt else COLOR_BUTTON_HOVER
            if draw_button(screen, opt, x_start + (idx * 160), SCREEN_HEIGHT // 3 + 35, 140, 45, btn_color, hover_color, active_click_event):
                difficulty = opt
                engine.change_difficulty(difficulty)  

        audio_label = font_medium.render("Background Music", True, COLOR_TEXT_MUTED)
        screen.blit(audio_label, audio_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

        music_status_text = "ENABLED" if music_enabled else "MUTED"
        music_btn_color = COLOR_TOGGLE_BTN if music_enabled else (170, 55, 55)
        music_hover_color = COLOR_TOGGLE_HOVER if music_enabled else (200, 85, 85)
        
        if draw_button(screen, music_status_text, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 65, 200, 45, music_btn_color, music_hover_color, active_click_event):
            music_enabled = not music_enabled

        if draw_button(screen, "BACK", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 120, 200, 50, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            current_state = previous_state
            engine.recenter_board()  

    # STATE 4: ACTIVE PLAYING GAMEPLAY SCREEN
    elif current_state == STATE_PLAYING:
        score_txt = font_medium.render(f"SCORE: {engine.score}", True, COLOR_TEXT)
        screen.blit(score_txt, (50, 30))

        flag_count = sum(row.count(True) for row in engine.flagged)
        mines_txt = font_medium.render(f"MINES RETAINED: {max(0, engine.num_mines - flag_count)}", True, COLOR_TEXT)
        screen.blit(mines_txt, (SCREEN_WIDTH - mines_txt.get_width() - 250, 30))

        engine.draw(screen)

        hint_txt = font_small.render("Controls: Left Click = Dig | Right Click = Flag | ESC = Pause | F11 = Fullscreen", True, COLOR_TEXT_MUTED)
        screen.blit(hint_txt, (SCREEN_WIDTH // 2 - hint_txt.get_width() // 2, SCREEN_HEIGHT - 45))
        
        label = "WINDOW MODE" if is_fullscreen else "FULLSCREEN"
        if draw_button(screen, label, SCREEN_WIDTH - 230, 25, 200, 45, COLOR_TOGGLE_BTN, COLOR_TOGGLE_HOVER, active_click_event):
            toggle_screen_mode()

    # STATE 5: PAUSE MENU OVERLAY
    elif current_state == STATE_PAUSED:
        engine.draw(screen)  

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = font_large.render("GAME PAUSED", True, COLOR_TEXT)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        if draw_button(screen, "RESUME GAME", SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 80, 260, 50, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            current_state = STATE_PLAYING

        if draw_button(screen, "SETTINGS", SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 15, 260, 50, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            previous_state = STATE_PAUSED
            current_state = STATE_SETTINGS

        if draw_button(screen, "RESTART GAME", SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 50, 260, 50, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            engine.reset()
            current_state = STATE_PLAYING

        if draw_button(screen, "QUIT TO MAIN MENU", SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 115, 260, 50, (170, 55, 55), (200, 85, 85), active_click_event):
            engine.reset()
            engine.recenter_board()
            current_state = STATE_MENU

    # STATE 6: GAME OVER SCREEN
    elif current_state == STATE_GAMEOVER:
        engine.draw(screen)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0,0))

        msg = font_large.render("BOOM! GAME OVER", True, (240, 60, 60))
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))

        final_score = font_medium.render(f"Final Score Earned: {engine.score}", True, COLOR_TEXT)
        screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))

        if draw_button(screen, "TRY AGAIN", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50, 240, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            engine.reset()
            current_state = STATE_PLAYING

        if draw_button(screen, "MAIN MENU", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 120, 240, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            current_state = STATE_MENU

    # STATE 7: WINNING SCREEN
    elif current_state == STATE_WIN:
        engine.draw(screen)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0,0))

        msg = font_large.render("VICTORY COMPLETED!", True, (60, 240, 60))
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))

        final_score = font_medium.render(f"High Score Achieved: {engine.score}", True, COLOR_TEXT)
        screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))

        if draw_button(screen, "PLAY AGAIN", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50, 240, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            engine.reset()
            current_state = STATE_PLAYING

        if draw_button(screen, "MAIN MENU", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 120, 240, 55, COLOR_BUTTON, COLOR_BUTTON_HOVER, active_click_event):
            current_state = STATE_MENU

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()