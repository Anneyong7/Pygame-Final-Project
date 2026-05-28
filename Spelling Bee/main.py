import pygame
import random
import sys
import os

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# --- CONFIGURATION ---
# Screen settings
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spelling Bee Game - Ultimate Edition")

# Colors (New Cool Palette)
DARK_BG = (30, 30, 40)        # Dark Blue/Grey background
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_BLUE = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_RED = (255, 30, 30)
NEON_YELLOW = (255, 255, 0)
PURPLE = (200, 100, 255)

# Fonts
title_font = pygame.font.SysFont("impact", 70, bold=True)
font = pygame.font.SysFont("arial", 35, bold=True)
small_font = pygame.font.SysFont("arial", 25)
input_font = pygame.font.SysFont("consolas", 40)

# Clock
clock = pygame.time.Clock()

# Word List
words = [
    ("A yellow fruit", "banana"),
    ("Animal that barks", "dog"),
    ("King of the jungle", "lion"),
    ("Something you read", "book"),
    ("Used for writing", "pencil"),
    ("Flying animal with wings", "bird"),
    ("Color of the sky", "blue"),
    ("You wear this on your feet", "shoes"),
    ("A place where students study", "school"),
    ("You use this to tell time", "clock"),
    ("Opposite of Hot", "cold"),
    ("H2O", "water")
]

# Game Variables
score = 0
lives = 3
time_limit = 60

start_ticks = pygame.time.get_ticks()
user_text = ""
current_question = random.choice(words)

game_state = "menu"

# --- SOUND & MUSIC SYSTEM ---
# We try to load sounds, but if files don't exist, we just continue (No Crash)
def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    else:
        print(f"Note: '{filename}' not found. Sound skipped.")
        return None

# Load your audio files here. Ensure they exist in the folder!
# Music (Loops -1)
try:
    pygame.mixer.music.load("background.mp3") 
except:
    print("Note: 'background.mp3' not found for music.")

# SFX
correct_sound = load_sound("correct.wav")
wrong_sound = load_sound("wrong.wav")
game_over_sound = load_sound("lose.wav")

# --- HELPER FUNCTIONS ---
def draw_text(text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)

# Main Loop
running = True

while running:

    # Draw Background
    screen.fill(DARK_BG)
    
    # Draw some decorative grid lines for "Cool Design"
    for i in range(0, WIDTH, 40):
        pygame.draw.line(screen, (40, 40, 55), (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (40, 40, 55), (0, i), (WIDTH, i))

    # TIMER LOGIC
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    time_left = max(0, time_limit - seconds)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # MENU CONTROLS
        if game_state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Start Music when game starts
                    try:
                        pygame.mixer.music.play(-1) # -1 means loop forever
                    except:
                        pass # Music file didn't load
                    game_state = "instructions"

        # INSTRUCTIONS SCREEN
        elif game_state == "instructions":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = "game"

        # GAME SCREEN
        elif game_state == "game":
            if event.type == pygame.KEYDOWN:
                # BACKSPACE
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                # ENTER (CHECK ANSWER)
                elif event.key == pygame.K_RETURN:
                    correct_answer = current_question[1]
                    
                    if user_text.lower() == correct_answer.lower():
                        score += 1
                        if correct_sound: correct_sound.play()
                    else:
                        lives -= 1
                        if wrong_sound: wrong_sound.play()
                    
                    user_text = ""
                    current_question = random.choice(words)

                # TYPING
                else:
                    # Limit text length to avoid drawing off screen
                    if len(user_text) < 15:
                        user_text += event.unicode

        # GAME OVER SCREEN
        elif game_state == "gameover":
            if event.type == pygame.KEYDOWN:
                # Restart Game
                if event.key == pygame.K_r:
                    score = 0
                    lives = 3
                    user_text = ""
                    start_ticks = pygame.time.get_ticks()
                    current_question = random.choice(words)
                    try:
                        pygame.mixer.music.play(-1) # Restart music
                    except: pass
                    game_state = "game"
                # Quit Game
                elif event.key == pygame.K_q:
                    running = False

    # ==========================================
    # DRAWING STATES
    # ==========================================

    # --- MENU STATE ---
    if game_state == "menu":
        # Title
        draw_text("SPELLING BEE", title_font, NEON_YELLOW, WIDTH//2, 180, center=True)
        draw_text("CHALLENGE", title_font, NEON_BLUE, WIDTH//2, 250, center=True)
        
        # Blinking text effect
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_text("Press SPACE to Start", font, WHITE, WIDTH//2, 400, center=True)

    # --- INSTRUCTIONS STATE ---
    elif game_state == "instructions":
        draw_text("INSTRUCTIONS", title_font, PURPLE, WIDTH//2, 100, center=True)
        
        instructions = [
            "1. Read the definition carefully.",
            "2. Type the correct spelling.",
            "3. Press ENTER to submit.",
            "4. Don't run out of time or lives!"
        ]
        
        y_offset = 200
        for line in instructions:
            draw_text(line, small_font, WHITE, WIDTH//2, y_offset, center=True)
            y_offset += 50

        draw_text("Press ENTER to Play", font, NEON_GREEN, WIDTH//2, 500, center=True)

    # --- GAME STATE ---
    elif game_state == "game":
        # Top Bar UI
        pygame.draw.rect(screen, (20, 20, 30), (0, 0, WIDTH, 80))
        
        draw_text(f"Score: {score}", small_font, NEON_GREEN, 20, 30)
        draw_text(f"Lives: {lives}", small_font, NEON_RED, 150, 30)
        
        # Timer Color change based on time left
        timer_color = WHITE
        if time_left < 10: timer_color = NEON_RED
        draw_text(f"Time: {time_left}", font, timer_color, WIDTH - 150, 20)

        # The Question Box
        box_rect = pygame.Rect(100, 150, WIDTH - 200, 350)
        pygame.draw.rect(screen, (50, 50, 70), box_rect, border_radius=20)
        pygame.draw.rect(screen, NEON_BLUE, box_rect, 3, border_radius=20)

        # Definition Text
        definition = current_question[0]
        draw_text("DEFINITION:", small_font, (150, 150, 150), WIDTH//2, 180, center=True)
        draw_text(definition, font, WHITE, WIDTH//2, 230, center=True)

        # Input Field
        input_box = pygame.Rect(180, 310, 440, 60)
        pygame.draw.rect(screen, BLACK, input_box, border_radius=10)
        pygame.draw.rect(screen, NEON_BLUE, input_box, 2, border_radius=10)
        
        # Render User Text
        input_surface = input_font.render(user_text, True, WHITE)
        # Center text in box
        text_rect = input_surface.get_rect(center=input_box.center)
        screen.blit(input_surface, text_rect)
        
        # Cursor effect (blinking block)
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = text_rect.right + 5
            pygame.draw.rect(screen, WHITE, (cursor_x, text_rect.top, 5, text_rect.height))

        # Win/Lose Conditions
        if score >= 10:
            game_state = "gameover"
            pygame.mixer.music.stop() # Stop music
            if game_over_sound: game_over_sound.play()

        if lives <= 0 or time_left <= 0:
            game_state = "gameover"
            pygame.mixer.music.stop()
            if game_over_sound: game_over_sound.play()

    # --- GAME OVER STATE ---
    elif game_state == "gameover":
        if score >= 10:
            draw_text("YOU WIN!", title_font, NEON_GREEN, WIDTH//2, 180, center=True)
            draw_text("Great Spelling!", font, WHITE, WIDTH//2, 280, center=True)
        else:
            draw_text("GAME OVER", title_font, NEON_RED, WIDTH//2, 180, center=True)
            draw_text("Better luck next time.", font, WHITE, WIDTH//2, 280, center=True)

        draw_text(f"Final Score: {score}", font, NEON_YELLOW, WIDTH//2, 380, center=True)
        
        draw_text("Press 'R' to Restart or 'Q' to Quit", small_font, (150, 150, 150), WIDTH//2, 500, center=True)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()