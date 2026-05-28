import pygame
import subprocess
import sys

# --- 1. SETUP ---
pygame.init()
screen = pygame.display.set_mode((400, 600))
pygame.display.set_caption("Coin Clicker - Main Menu")

# Using the retro font to match the main game theme
title_font = pygame.font.Font("clicker/assets/PressStart2P-Regular.ttf", 26)
button_font = pygame.font.Font("clicker/assets/PressStart2P-Regular.ttf", 18)

# --- 2. COLORS ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WOOD_BORDER = (93, 64, 55)   
WOOD_BASE = (161, 136, 127)  
TEXT_CREAM = (255, 236, 179) 

# --- 3. LOAD BACKGROUND ---
# Draws your custom 400x600 image directly
bg_image = pygame.image.load("clicker/assets/background.png")

# --- 4. BUTTON AREAS ---
play_button = pygame.Rect(100, 250, 200, 60)
exit_button = pygame.Rect(100, 350, 200, 60)

running = True

# --- 5. MENU LOOP ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Clicked Play -> Launches your main game file
            if play_button.collidepoint(mouse_pos):
                subprocess.run([sys.executable, "Main_Game.py"], cwd="clicker")
                
            # Clicked Exit
            if exit_button.collidepoint(mouse_pos):
                running = False

    # --- 6. DRAWING ---
    # Draw background image first
    screen.blit(bg_image, (0, 0))

    # Draw Title (Centered with a clean drop shadow)
    title_shadow = title_font.render("Be a Millionare", True, BLACK)
    title_shadow_rect = title_shadow.get_rect(center=(202, 122))
    screen.blit(title_shadow, title_shadow_rect)

    title_text = title_font.render("Be a Millionare", True, WHITE)
    title_rect = title_text.get_rect(center=(200, 120))
    screen.blit(title_text, title_rect)

    # --- Draw Rustic Play Button ---
    pygame.draw.rect(screen, WOOD_BORDER, play_button) 
    pygame.draw.rect(screen, WOOD_BASE, play_button.inflate(-8, -8))
    pygame.draw.circle(screen, WOOD_BORDER, (play_button.left + 12, play_button.top + 12), 3)
    pygame.draw.circle(screen, WOOD_BORDER, (play_button.right - 12, play_button.top + 12), 3)
    pygame.draw.circle(screen, WOOD_BORDER, (play_button.left + 12, play_button.bottom - 12), 3)
    pygame.draw.circle(screen, WOOD_BORDER, (play_button.right - 12, play_button.bottom - 12), 3)

    # --- Draw Rustic Exit Button ---
    pygame.draw.rect(screen, WOOD_BORDER, exit_button) 
    pygame.draw.rect(screen, WOOD_BASE, exit_button.inflate(-8, -8))
    pygame.draw.circle(screen, WOOD_BORDER, (exit_button.left + 12, exit_button.top + 12), 3)
    pygame.draw.circle(screen, WOOD_BORDER, (exit_button.right - 12, exit_button.top + 12), 3)
    pygame.draw.circle(screen, WOOD_BORDER, (exit_button.left + 12, exit_button.bottom - 12), 3)
    pygame.draw.circle(screen, WOOD_BORDER, (exit_button.right - 12, exit_button.bottom - 12), 3)

    # --- Draw Button Text (Perfectly Centered inside hitboxes) ---
    play_text = button_font.render("PLAY", True, TEXT_CREAM)
    play_rect = play_text.get_rect(center=play_button.center)
    screen.blit(play_text, play_rect)
    
    exit_text = button_font.render("EXIT", True, TEXT_CREAM)
    exit_rect = exit_text.get_rect(center=exit_button.center)
    screen.blit(exit_text, exit_rect)

    pygame.display.flip()

pygame.quit()