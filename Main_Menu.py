import pygame
import subprocess
import sys

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Coin Clicker")
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 40)

# --- Colors ---
PEACH = (255, 218, 185)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 139, 87)
RED = (200, 0, 0)

# --- Button Areas ---
play_button = pygame.Rect(100, 250, 200, 60)
exit_button = pygame.Rect(100, 350, 200, 60)

running = True

# --- Menu Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Clicked Play
            if play_button.collidepoint(mouse_pos):
                # This opens your main game file. 
                # Ensure your main game is named "clicker_game.py"
                subprocess.run([sys.executable, "clicker_main.py"])
                
            # Clicked Exit
            if exit_button.collidepoint(mouse_pos):
                running = False

    # --- Drawing ---
    screen.fill(PEACH)

    # Draw Title
    title_text = font.render("COIN CLICKER", True, BLACK)
    screen.blit(title_text, (80, 100))

    # Draw Buttons
    pygame.draw.rect(screen, GREEN, play_button)
    pygame.draw.rect(screen, RED, exit_button)

    # Draw Button Text
    play_text = small_font.render("Play", True, WHITE)
    screen.blit(play_text, (170, 265))
    
    exit_text = small_font.render("Exit", True, WHITE)
    screen.blit(exit_text, (170, 365))

    pygame.display.flip()

pygame.quit()