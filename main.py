import pygame
import random
from desk import Desk
from seat import Seat
from player import Player
from ai_agent import AIAgent, create_wandering_ai
import time
import numpy as np
from utils import get_ai_to_leave, find_path_bfs, euclidean_dist, ai_to_sit
import os

player_img_path = "asset/img/boy_player.png"
ai_img_path = "asset/img/ai_agent.png"

pygame.init()
pygame.mixer.init() # 사운드 시스템 초기화

# 사운드 파일 경로 설정 및 로드
sound_path = "asset/sound/"
sit_sound = pygame.mixer.Sound(os.path.join(sound_path, "sit.mp3"))
game_over_sound = pygame.mixer.Sound(os.path.join(sound_path, "game_over.mp3"))

# 배경음악은 게임 시작 시 로드 및 재생
def play_bgm():
    pygame.mixer.music.load(os.path.join(sound_path, "stranger-things.mp3"))
    pygame.mixer.music.play(-1)

UI_height = 60
screen = pygame.display.set_mode((800, 600 + UI_height))
pygame.display.set_caption("ToHak")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont(None, 100, bold=True)
button_font = pygame.font.SysFont(None, 50, bold=True)
default_font = pygame.font.SysFont(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
DARK_GRAY = (30, 30, 30)
UI_GRAY = (50, 50, 50)

# Load background image
try:
    background_image = pygame.image.load(os.path.join('asset/img', 'background_black.png'))
    background_image = pygame.transform.scale(background_image, (800, 600 + UI_height))
except pygame.error:
    background_image = None # If image fails to load

def draw_text(text, font, color, surface, x, y, center=False):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Game State
game_state = "START_MENU"
running = True
elapsed_time = 0

# Main game loop
while running:
    screen.fill(DARK_GRAY)
    
    # Event handling
    mouse_clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_clicked = True

    # State-dependent logic and drawing
    if game_state == "START_MENU":
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(DARK_GRAY)
            
        draw_text("ToHak", title_font, WHITE, screen, 400, 250, center=True)
        
        # Start Button
        start_button_rect = pygame.Rect(screen.get_width() / 2 - 125, 400, 250, 50)
        pygame.draw.rect(screen, GREEN, start_button_rect)
        draw_text("START", button_font, WHITE, screen, 400, 425, center=True)
        
        # How to Play Button
        how_to_play_button_rect = pygame.Rect(screen.get_width() / 2 - 125, 470, 250, 50)
        pygame.draw.rect(screen, GREEN, how_to_play_button_rect)
        draw_text("How to Play", button_font, WHITE, screen, 400, 495, center=True)

        if mouse_clicked:
            if start_button_rect.collidepoint(pygame.mouse.get_pos()):
                game_state = "DIFICAULTY_SELECTION"
                
            elif how_to_play_button_rect.collidepoint(pygame.mouse.get_pos()):
                game_state = "HOW_TO_PLAY"

    elif game_state == "DIFICAULTY_SELECTION":
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        draw_text("Select Difficulty", title_font, WHITE, screen, 400, 200, center=True)

        easy_button = pygame.Rect(screen.get_width() / 2 - 125, 300, 250, 50)
        normal_button = pygame.Rect(screen.get_width() / 2 - 125, 370, 250, 50)
        hard_button = pygame.Rect(screen.get_width() / 2 - 125, 440, 250, 50)

        pygame.draw.rect(screen, GREEN, easy_button)
        pygame.draw.rect(screen, GREEN, normal_button)
        pygame.draw.rect(screen, GREEN, hard_button)

        draw_text("EASY", button_font, WHITE, screen, 400, 325, center=True)
        draw_text("NORMAL", button_font, WHITE, screen, 400, 395, center=True)
        draw_text("HARD", button_font, WHITE, screen, 400, 465, center=True)

        if mouse_clicked:
            mouse_pos = pygame.mouse.get_pos()
            if easy_button.collidepoint(mouse_pos):
                selected_difficulty = "EASY"
                Lambda = 1 / 5
                heart_loss_interval = 5
                initial_wandering = 3
                ai_step = 3
                ai_speed = 2
            elif normal_button.collidepoint(mouse_pos):
                selected_difficulty = "NORMAL"
                Lambda = 1 / 5
                heart_loss_interval = 4
                initial_wandering = 4
                ai_step = 4
                ai_speed = 3
            elif hard_button.collidepoint(mouse_pos):
                selected_difficulty = "HARD"
                Lambda = 1 / 5
                heart_loss_interval = 3
                initial_wandering = 5
                ai_step = 5
                ai_speed = 4
            game_state = "PLAYING_SETUP"
    
    elif game_state == "PLAYING_SETUP":
        # --- Initialize Game ---
        player = Player(400, 300, width=40, height=40)
        ui_region = pygame.Rect(0, 600, 800, UI_height)
        
        desks = []
        desk_w, desk_h = 230, 110
        margin_x, margin_y = 90, 100
        positions = [
            (margin_x, margin_y), (800 - margin_x - desk_w, margin_y),
            (margin_x, 600 - margin_y - desk_h), (800 - margin_x - desk_w, 600 - margin_y - desk_h)
        ]
        for x, y in positions:
            desks.append(Desk(x, y, desk_w, desk_h))
        
        all_seats = []
        for desk in desks:
            all_seats.extend(desk.seats)

        static_obstacles = [desk.rect for desk in desks]
        for desk in desks:
            for seat in desk.seats:
                static_obstacles.append(seat.rect)
        static_obstacles.append(ui_region)

        screen_width, screen_height = screen.get_width(), (screen.get_height() - UI_height)
        ai_size = 30
        for seat in all_seats:
            x, y = seat.rect.center
            targets = [(ai_size, y), (screen_width - ai_size, y), (x, ai_size), (x, screen_height - ai_size)]
            target = min(targets, key=lambda p: euclidean_dist((x, y), p))
            path_obstacles = [obstacle for obstacle in static_obstacles if not seat.rect.colliderect(obstacle)]
            path = find_path_bfs((x, y), target, path_obstacles, screen_width, screen_height, agent_size=seat.rect.width, step=2)
            seat.exit_path = path
            assert path is not None, f"Path not found for seat at {seat.rect.topleft} to target {target}"

        ai_agents = []
        for seat in all_seats:
            ai = AIAgent(seat.rect.x, seat.rect.y)
            ai.set_seated(seat)
            ai_agents.append(ai)
        
        wandering_ai = create_wandering_ai(initial_wandering, static_obstacles + [player.rect], screen_size=(screen_width, screen_height), speed=ai_speed)
        ai_agents.extend(wandering_ai)

        Lambda = 1/5
        time_gap = 3 + np.random.exponential(scale=1 / Lambda)
        next_despawn_time = time.time() + time_gap

        start_time = time.time()
        heart_img = pygame.image.load("asset/img/heart.png").convert_alpha()
        heart_img = pygame.transform.scale(heart_img, (30, 30))
        max_hearts = 8
        hearts = max_hearts
        last_heart_loss_time = time.time()
        # heart_loss_interval = 4
        
        play_bgm()
        game_state = "PLAYING"

    elif game_state == "HOW_TO_PLAY":
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(DARK_GRAY)

        draw_text("How to Play", title_font, WHITE, screen, 400, 100, center=True)
        
        rules = [
            "Use Arrow Keys to move your character.",
            "Find an empty seat and press SPACE to sit down.",
            "The hearts at the bottom are your life.",
            "They will decrease over time.",
            "Sit on a chair to win the game before you starve!"
        ]
        
        for i, rule in enumerate(rules):
            draw_text(rule, default_font, WHITE, screen, 400, 200 + i * 40, center=True)
            
        # Back Button
        back_button_rect = pygame.Rect(screen.get_width() / 2 - 100, 500, 200, 50)
        pygame.draw.rect(screen, GREEN, back_button_rect)
        draw_text("Back", button_font, WHITE, screen, 400, 525, center=True)

        if mouse_clicked and back_button_rect.collidepoint(pygame.mouse.get_pos()):
            game_state = "START_MENU"

    elif game_state == "PLAYING":
        # --- Game Logic ---
        if player.seated:
            elapsed_time = round(time.time() - start_time, 2)
            pygame.mixer.music.stop()
            game_state = "WIN"

        current_time = time.time()
        if game_state == "PLAYING" and current_time - last_heart_loss_time >= heart_loss_interval:
            hearts -= 1
            last_heart_loss_time = current_time
            if hearts <= 0:
                game_over_sound.play()
                pygame.mixer.music.stop()
                game_state = "GAME_OVER"

        if game_state == "PLAYING": # Check again in case state changed
            obstacles = [desk.rect for desk in desks]
            for seat in desk.seats: obstacles.append(seat.rect)
            for ai in ai_agents: obstacles.append(ai.rect)

            empty_seats = [seat for seat in all_seats if not seat.occupied]
            if not empty_seats:
                wandering_ais = [ai for ai in ai_agents if ai.state == "wandering"]
                if len(wandering_ais) < initial_wandering:
                    ai_agents.extend(create_wandering_ai(1, obstacles + [player.rect], screen_size=(screen_width, screen_height), speed=ai_speed))
                if time.time() >= next_despawn_time:
                    ai_to_leave = get_ai_to_leave(ai_agents, player.rect)
                    if ai_to_leave: ai_to_leave.despawn()
                    next_despawn_time = time.time() + np.random.exponential(scale=1 / Lambda)
            elif not empty_seats[0].targeted:
                ai_to_sit(empty_seats[0], ai_agents, obstacles, screen_size=(screen_width, screen_height), ai_step=ai_step)
            
            for ai in ai_agents:
                ai.update(player.rect, obstacles, screen_width, screen_height)
            player.handle_input(obstacles, screen_width, screen_height)
            player.update_animation()
            ai_agents = [ai for ai in ai_agents if not ai.offscreen]

            sit_target = None
            for desk in desks:
                for seat in desk.seats:
                    if seat.can_sit(player.rect):
                        sit_target = seat
                        break
                if sit_target: break
            
            keys = pygame.key.get_pressed()
            if sit_target and keys[pygame.K_SPACE] and not player.seated:
                sit_sound.play()
                player.sit(sit_target)

            # --- Drawing ---
            pygame.draw.rect(screen, UI_GRAY, ui_region)
            for desk in desks: desk.draw(screen)
            for ai in ai_agents: ai.draw(screen)
            player.draw(screen)
            for i in range(hearts): screen.blit(heart_img, (20 + i * 35, ui_region.top + 10))
            if sit_target and not player.seated:
                draw_text("Press Space Bar to sit down", default_font, WHITE, screen, 400, 20, center=True)
                
    elif game_state == "GAME_OVER":
        draw_text("Game Over", title_font, WHITE, screen, 400, 250, center=True)
        draw_text("You starved...", button_font, WHITE, screen, 400, 350, center=True)
        draw_text("Click to return to menu", default_font, WHITE, screen, 400, 450, center=True)
        if mouse_clicked:
            game_state = "START_MENU"
        
    elif game_state == "WIN":
        draw_text("You Win!", title_font, WHITE, screen, 400, 250, center=True)
        draw_text(f"Time: {elapsed_time} sec", button_font, WHITE, screen, 400, 350, center=True)
        draw_text("Click to return to menu", default_font, WHITE, screen, 400, 450, center=True)
        if mouse_clicked:
            game_state = "START_MENU"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
