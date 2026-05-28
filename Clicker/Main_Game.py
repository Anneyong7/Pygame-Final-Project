import pygame

# --- 1. SETUP (Lines 3-15) ---
pygame.init() 
pygame.mixer.init() 
screen = pygame.display.set_mode((400, 600)) 
pygame.display.set_caption("Coin Clicker Game") 

# Font sizes
font = pygame.font.Font("../Clicker/Assets/PressStart2P-Regular.ttf", 16) 
large_font = pygame.font.Font("../Clicker/Assets/PressStart2P-Regular.ttf", 40)
small_font = pygame.font.Font("../Clicker/assets/PressStart2P-Regular.ttf", 12) 
shop_font = pygame.font.Font("../Clicker/assets/PressStart2P-Regular.ttf", 13)
restart_font = pygame.font.Font("../Clicker/assets/PressStart2P-Regular.ttf", 15)
YOU_WIN_FONT = pygame.font.Font("../Clicker/assets/PressStart2P-Regular.ttf", 15)

# --- 2. COLORS (Lines 18-22) ---
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0) 
GREEN = (46, 139, 87) 
WOOD_BORDER = (93, 64, 55)   
WOOD_BASE = (161, 136, 127)   

# --- 3. LOAD IMAGES (Lines 24-30) ---
bg_image = pygame.image.load("../Clicker/assets/background.png")
bg_image = pygame.transform.scale(bg_image, (400, 600))

coin_image = pygame.image.load("../Clicker/assets/coin.png")
coin_image = pygame.transform.scale(coin_image, (200, 120))
coin_rect = coin_image.get_rect(center=(200, 200)) 

# --- 4. BUTTON HITBOXES (Lines 32-36) ---
shop1_rect = pygame.Rect(100, 320, 200, 60) 
shop2_rect = pygame.Rect(100, 400, 200, 60) 
restart_rect = pygame.Rect(100, 380, 200, 60) 
win_exit_rect = pygame.Rect(100, 460, 200, 60) # New exit button layout for the win screen

# --- 5. AUDIO SETUP (Lines 39-43) ---
click_sound = pygame.mixer.Sound("../Clicker/assets/ClickSound.mp3")
purchase_sound = pygame.mixer.Sound("../Clicker/assets/PurchaseSound.mp3")
pygame.mixer.music.load("../Clicker/assets/bg_music.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1) 

# --- 6. GAME VARIABLES (Lines 46-51) ---
coins = 0 
click_value = 1 
auto_clickers = 0 
multiplier_cost = 1
auto_cost = 2 
game_state = "PLAYING" 

# --- 7. AUTO-CLICK TIMER (Lines 54-57) ---
AUTO_EVENT = pygame.USEREVENT + 1 
pygame.time.set_timer(AUTO_EVENT, 1000) 

running = True 

# --- 8. MAIN GAME LOOP ---
while running:
    
    # --- 9. EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False 
            
        if event.type == AUTO_EVENT and game_state == "PLAYING": 
            coins += (auto_clickers * 2) 

        if event.type == pygame.MOUSEBUTTONDOWN: 
            mouse_pos = event.pos 
            
            if game_state == "PLAYING":
                if coin_rect.collidepoint(mouse_pos):
                    click_sound.play() 
                    coins += click_value 
                    
                elif shop1_rect.collidepoint(mouse_pos): 
                    if coins >= multiplier_cost: 
                        purchase_sound.play() 
                        coins -= multiplier_cost 
                        click_value *= 2 
                        multiplier_cost *= 2 
                        
                elif shop2_rect.collidepoint(mouse_pos): 
                    if coins >= auto_cost: 
                        purchase_sound.play() 
                        coins -= auto_cost 
                        auto_clickers += 1 
                        auto_cost += 50 
            
            else:
                # Inside the Win Screen options
                if restart_rect.collidepoint(mouse_pos):
                    game_state = "PLAYING"
                    coins = 0
                    click_value = 1
                    auto_clickers = 0
                    multiplier_cost = 100
                    auto_cost = 50
                elif win_exit_rect.collidepoint(mouse_pos): # Checks if Exit is clicked
                    running = False

    # --- 10. GAME LOGIC ---
    if game_state == "PLAYING":
        if coins >= 1000000:
            game_state = "WON"

    # --- 11. DRAWING BACKGROUND ---
    screen.blit(bg_image, (0, 0)) 

    # --- 12. DRAWING ACTIVE GAME ---
    if game_state == "PLAYING":
        screen.blit(coin_image, coin_rect.topleft)
        
        # Shop 1
        pygame.draw.rect(screen, WOOD_BORDER, shop1_rect) 
        pygame.draw.rect(screen, WOOD_BASE, shop1_rect.inflate(-8, -8))
        pygame.draw.circle(screen, WOOD_BORDER, (shop1_rect.left + 12, shop1_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (shop1_rect.right - 12, shop1_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (shop1_rect.left + 12, shop1_rect.bottom - 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (shop1_rect.right - 12, shop1_rect.bottom - 12), 3)

        # Shop 2
        pygame.draw.rect(screen, WOOD_BORDER, shop2_rect) 
        pygame.draw.rect(screen, WOOD_BASE, shop2_rect.inflate(-8, -8))
        pygame.draw.circle(screen, WOOD_BORDER, (shop2_rect.left + 12, shop2_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (shop2_rect.right - 12, shop2_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (shop2_rect.left + 12, shop2_rect.bottom - 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (shop2_rect.right - 12, shop2_rect.bottom - 12), 3)

        # --- Draw Stats Text ---
        score_text = large_font.render(f"{coins}", True, WHITE)
        score_rect = score_text.get_rect(center=(200, 50))
        screen.blit(score_text, score_rect)
        
        click_stat = small_font.render(f"{click_value} per click", True, WHITE)
        click_rect = click_stat.get_rect(center=(200, 85))
        screen.blit(click_stat, click_rect)
        
        auto_stat = small_font.render(f"{auto_clickers * 2} per second", True, WHITE)
        auto_rect = auto_stat.get_rect(center=(200, 105))
        screen.blit(auto_stat, auto_rect)

        # Shop Text
        shop1_text = shop_font.render("2x Click", True, WHITE)
        shop1_cost_text = shop_font.render(f"Cost: {multiplier_cost}", True, WHITE)
        screen.blit(shop1_text, (shop1_rect.x + 50, shop1_rect.y + 10))
        screen.blit(shop1_cost_text, (shop1_rect.x + 50, shop1_rect.y + 35))
        
        shop2_text = shop_font.render("+2 Auto/sec", True, WHITE)
        shop2_cost_text = shop_font.render(f"Cost: {auto_cost}", True, WHITE)
        screen.blit(shop2_text, (shop2_rect.x + 35, shop2_rect.y + 10))
        screen.blit(shop2_cost_text, (shop2_rect.x + 35, shop2_rect.y + 35))

    # --- 13. DRAWING GAME OVER ---
    else:
        # Title text drop shadow effect
        result_text = YOU_WIN_FONT.render("You are now a Millionaire!", True, BLACK)
        screen.blit(result_text, (5, 200))
        result_text = YOU_WIN_FONT.render("You are now a Millionaire!", True, WHITE)
        screen.blit(result_text, (7, 200))
        
        # --- Draw Rustic Restart Button ---
        pygame.draw.rect(screen, WOOD_BORDER, restart_rect) 
        pygame.draw.rect(screen, WOOD_BASE, restart_rect.inflate(-8, -8))
        pygame.draw.circle(screen, WOOD_BORDER, (restart_rect.left + 12, restart_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (restart_rect.right - 12, restart_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (restart_rect.left + 12, restart_rect.bottom - 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (restart_rect.right - 12, restart_rect.bottom - 12), 3)

        restart_text = restart_font.render("Restart Game", True, WHITE)
        restart_rect_text = restart_text.get_rect(center=restart_rect.center)
        screen.blit(restart_text, restart_rect_text)

        # --- Draw Rustic Exit Button ---
        pygame.draw.rect(screen, WOOD_BORDER, win_exit_rect) 
        pygame.draw.rect(screen, WOOD_BASE, win_exit_rect.inflate(-8, -8))
        pygame.draw.circle(screen, WOOD_BORDER, (win_exit_rect.left + 12, win_exit_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (win_exit_rect.right - 12, win_exit_rect.top + 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (win_exit_rect.left + 12, win_exit_rect.bottom - 12), 3)
        pygame.draw.circle(screen, WOOD_BORDER, (win_exit_rect.right - 12, win_exit_rect.bottom - 12), 3)

        exit_text = restart_font.render("Exit Game", True, WHITE)
        exit_rect_text = exit_text.get_rect(center=win_exit_rect.center)
        screen.blit(exit_text, exit_rect_text)

    # --- 14. UPDATE DISPLAY ---
    pygame.display.flip() 

# --- 15. SHUTDOWN ---
pygame.quit()