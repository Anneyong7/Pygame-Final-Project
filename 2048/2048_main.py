import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 470
SCREEN_HEIGHT = 565
GRID_SIZE = 4
CELL_SIZE = 90
PADDING = 15
TOP_BAR_HEIGHT = 90

BG_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TEXT_DARK = (119, 110, 101)
TEXT_LIGHT = (249, 246, 242)
CANVAS_BG = (250, 248, 239)

COLOR_MAP = {
    2: (238, 228, 218),    4: (237, 224, 200),    8: (242, 177, 121),
    16: (245, 149, 99),   32: (245, 124, 95),   64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97),  512: (237, 200, 80),
    1024: (237, 197, 63), 2048: (237, 194, 46)
}

class Full2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2048 - PUZZLE GAME")
        
        self.font_large = pygame.font.SysFont("arial", 40, bold=True)
        self.font_med = pygame.font.SysFont("arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("arial", 16, bold=True)
        

        self.load_audio()
        
        self.game_state = "MENU"
        self.reset_game()

    def load_audio(self):
        """Loads required background music and movement sound effects using absolute script paths."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            bgm_path = os.path.join(script_dir, "assets", "audio", "background.mp3")
            move_path = os.path.join(script_dir, "assets", "audio", "effects.wav")
            
            if os.path.exists(bgm_path) and os.path.exists(move_path):
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.2)
                self.move_sound = pygame.mixer.Sound(move_path)
                self.move_sound.set_volume(0.5)
                print("Audio loaded successfully!")
            else:
                print(f"Looking for BGM at: {bgm_path}")
                print(f"Looking for Move SFX at: {move_path}")
                print("Audio files missing inside assets/audio/ folder. Running in silent mode.")
                self.move_sound = None
        except Exception as e:
            print(f"Audio initialization skip: {e}")
            self.move_sound = None

    def reset_game(self):
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.spawn_tile()
        self.spawn_tile()

    def spawn_tile(self):
        empty_spots = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.grid[r][c] == 0]
        if empty_spots:
            r, c = random.choice(empty_spots)
            self.grid[r][c] = 2

    def slide_and_merge(self, row):
        non_zeros = [num for num in row if num != 0]
        for i in range(len(non_zeros) - 1):
            if non_zeros[i] == non_zeros[i + 1]:
                non_zeros[i] *= 2
                self.score += non_zeros[i]
                non_zeros[i + 1] = 0
        final_row = [num for num in non_zeros if num != 0]
        return final_row + [0] * (GRID_SIZE - len(final_row))

    def move(self, direction):
        old_grid = [row[:] for row in self.grid]

        if direction == "LEFT":
            for r in range(GRID_SIZE): self.grid[r] = self.slide_and_merge(self.grid[r])
        elif direction == "RIGHT":
            for r in range(GRID_SIZE): self.grid[r] = self.slide_and_merge(self.grid[r][::-1])[::-1]
        elif direction == "UP":
            for c in range(GRID_SIZE):
                col = [self.grid[r][c] for r in range(GRID_SIZE)]
                merged = self.slide_and_merge(col)
                for r in range(GRID_SIZE): self.grid[r][c] = merged[r]
        elif direction == "DOWN":
            for c in range(GRID_SIZE):
                col = [self.grid[r][c] for r in range(GRID_SIZE)][::-1]
                merged = self.slide_and_merge(col)
                for r in range(GRID_SIZE): self.grid[r][c] = merged[::-1][r]

        if self.grid != old_grid:
            if self.move_sound:
                self.move_sound.play()
            self.spawn_tile()
            self.check_loss()

    def check_loss(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] == 0: return
                if r < GRID_SIZE - 1 and self.grid[r][c] == self.grid[r+1][c]: return
                if c < GRID_SIZE - 1 and self.grid[r][c] == self.grid[r][c+1]: return
        self.game_state = "GAME_OVER"

    def draw_playing_screen(self):
        self.screen.fill(CANVAS_BG)

        score_lbl = self.font_small.render("SCORE", True, TEXT_LIGHT)
        score_val = self.font_med.render(str(self.score), True, TEXT_LIGHT)
        
        score_box = pygame.Rect(PADDING, PADDING, 140, 55)
        pygame.draw.rect(self.screen, BG_COLOR, score_box, border_radius=4)
        self.screen.blit(score_lbl, (score_box.centerx - score_lbl.get_width()//2, score_box.y + 5))
        self.screen.blit(score_val, (score_box.centerx - score_val.get_width()//2, score_box.y + 23))

        menu_hint = self.font_small.render("Press [M] for Menu", True, TEXT_DARK)
        self.screen.blit(menu_hint, (SCREEN_WIDTH - menu_hint.get_width() - PADDING, PADDING + 20))

        grid_y_start = TOP_BAR_HEIGHT
        grid_width_height = SCREEN_WIDTH - (PADDING * 2)
        pygame.draw.rect(self.screen, BG_COLOR, (PADDING, grid_y_start, grid_width_height, grid_width_height), border_radius=6)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.grid[r][c]
                x = PADDING + c * (CELL_SIZE + PADDING) + PADDING
                y = grid_y_start + PADDING + r * (CELL_SIZE + PADDING) + PADDING
                
                cell_color = COLOR_MAP.get(val, (60, 58, 50)) if val > 0 else EMPTY_COLOR
                pygame.draw.rect(self.screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE), border_radius=4)

                if val > 0:
                    text_color = TEXT_DARK if val <= 4 else TEXT_LIGHT
                    text_surface = self.font_med.render(str(val), True, text_color)
                    text_rect = text_surface.get_rect(center=(x + CELL_SIZE/2, y + CELL_SIZE/2))
                    self.screen.blit(text_surface, text_rect)

    def draw_menu_screen(self):
        self.screen.fill(CANVAS_BG)
        title = self.font_large.render("2048 PUZZLE", True, TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
        
        opt1 = self.font_med.render("Press [SPACE] to Play", True, TEXT_DARK)
        opt2 = self.font_med.render("Press [I] for How to Play", True, TEXT_DARK)
        opt3 = self.font_med.render("Press [ESC] to Exit", True, TEXT_DARK)
        
        self.screen.blit(opt1, (SCREEN_WIDTH//2 - opt1.get_width()//2, 260))
        self.screen.blit(opt2, (SCREEN_WIDTH//2 - opt2.get_width()//2, 320))
        self.screen.blit(opt3, (SCREEN_WIDTH//2 - opt3.get_width()//2, 380))

    def draw_instructions_screen(self):
        self.screen.fill(CANVAS_BG)
        
        title = self.font_large.render("HOW TO PLAY", True, TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        rules = [
            "1. Use ARROW KEYS to shift tiles.",
            "2. When two tiles with the same number",
            "    touch, they merge into one!",
            "3. Every move spawns a new '2' tile.",
            "4. Build up grid values to reach 2048.",
            "5. The game ends when the board fills",
            "    up completely and no moves remain."
        ]
        
        y_offset = 140
        for rule in rules:
            rule_surface = self.font_small.render(rule, True, TEXT_DARK)
            self.screen.blit(rule_surface, (PADDING + 20, y_offset))
            y_offset += 40

        back_hint = self.font_med.render("Press [B] to Return to Menu", True, (246, 94, 59))
        self.screen.blit(back_hint, (SCREEN_WIDTH//2 - back_hint.get_width()//2, 480))

    def draw_game_over_screen(self):
        self.draw_playing_screen()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 220))
        self.screen.blit(overlay, (0,0))
        
        go_title = self.font_large.render("GAME OVER", True, (246, 94, 59))
        go_sub = self.font_med.render("Press [R] to Restart", True, TEXT_DARK)
        go_menu = self.font_med.render("Press [M] for Main Menu", True, TEXT_DARK)
        
        self.screen.blit(go_title, (SCREEN_WIDTH//2 - go_title.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(go_sub, (SCREEN_WIDTH//2 - go_sub.get_width()//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(go_menu, (SCREEN_WIDTH//2 - go_menu.get_width()//2, SCREEN_HEIGHT//2 + 60))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.game_state == "MENU":
                        if event.key == pygame.K_SPACE:  self.game_state = "PLAYING"
                        elif event.key == pygame.K_i:     self.game_state = "INSTRUCTIONS"
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

                    elif self.game_state == "INSTRUCTIONS":
                        if event.key == pygame.K_b:      self.game_state = "MENU"

                    elif self.game_state == "PLAYING":
                        if event.key == pygame.K_m:      self.game_state = "MENU"
                        elif event.key == pygame.K_LEFT:  self.move("LEFT")
                        elif event.key == pygame.K_RIGHT: self.move("RIGHT")
                        elif event.key == pygame.K_UP:    self.move("UP")
                        elif event.key == pygame.K_DOWN:  self.move("DOWN")

                    elif self.game_state == "GAME_OVER":
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_state = "PLAYING"
                        elif event.key == pygame.K_m:
                            self.reset_game()
                            self.game_state = "MENU"

            if self.game_state == "MENU":          self.draw_menu_screen()
            elif self.game_state == "INSTRUCTIONS": self.draw_instructions_screen()
            elif self.game_state == "PLAYING":      self.draw_playing_screen()
            elif self.game_state == "GAME_OVER":    self.draw_game_over_screen()

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    Full2048().run()  