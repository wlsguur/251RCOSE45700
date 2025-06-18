import pygame
import random
from desk import Desk
from seat import Seat
from player import Player
from ai_agent import AIAgent, create_wandering_ai
import time
import numpy as np
from utils import get_ai_to_leave, find_path_bfs, euclidean_dist, ai_to_sit

player_img_path = "asset/img/boy_player.png"
ai_img_path = "asset/img/ai_agent.png"

pygame.init()
UI_height = 60
screen = pygame.display.set_mode((800, 600 + UI_height))
pygame.display.set_caption("ToHak")
clock = pygame.time.Clock()

player = Player(400, 300,width=40, height=40)

ui_region = pygame.Rect(0, 600, 800, UI_height)

# Create desks and seats
desks = []
desk_w, desk_h = 230, 110
margin_x, margin_y = 90, 100

positions = [
    (margin_x, margin_y),
    (800 - margin_x - desk_w, margin_y),
    (margin_x, 600 - margin_y - desk_h),
    (800 - margin_x - desk_w, 600 - margin_y - desk_h)
]

for x, y in positions:
    desks.append(Desk(x, y, desk_w, desk_h))

all_seats = []
for desk in desks:
    all_seats.extend(desk.seats)

# Find exit paths for each seat
static_obstacles = [desk.rect for desk in desks]
for desk in desks:
    for seat in desk.seats:
        static_obstacles.append(seat.rect)
static_obstacles.append(ui_region)

screen_width, screen_height = screen.get_width(), (screen.get_height() - UI_height)
ai_size = 30

for seat in all_seats:
    x, y = seat.rect.center
    targets = [
        (ai_size, y),
        (screen_width - ai_size, y),
        (x, ai_size),
        (x, screen_height - ai_size)
    ]

    target = min(targets, key=lambda p: euclidean_dist((x, y), p))
    static_obstacles = [obstacle for obstacle in static_obstacles if not seat.rect.colliderect(obstacle)]
    path = find_path_bfs((x, y), target, static_obstacles, screen_width, screen_height, agent_size=seat.rect.width, step=2)
    seat.exit_path = path
    assert path is not None, f"Path not found for seat at {seat.rect.topleft} to target {target}"

# 모든 좌석에 AI 배치
ai_agents = []
for seat in all_seats:
    ai = AIAgent(seat.rect.x, seat.rect.y)
    ai.set_seated(seat)
    ai_agents.append(ai)

# wandering AI 3명 추가
wandering_ai = create_wandering_ai(3, static_obstacles + [player.rect], screen_size=(screen_width, screen_height))
ai_agents.extend(wandering_ai)

running = True
font = pygame.font.SysFont(None, 24)

# Set dsppawn time for AI agents
Lambda = 1/5
time_gap = 3 + np.random.exponential(scale=1 / Lambda)
next_despawn_time = time.time() + time_gap

# Set game over time
start_time = time.time()
heart_img = pygame.image.load("asset/img/heart.png").convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))

max_hearts = 8
hearts = max_hearts
last_heart_loss_time = time.time()
heart_loss_interval = 4  # 초 단위로 하트 하나 감소

game_win = False

# Game loop
while running:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if player.seated:
        game_win = True
        end_time = time.time()
        elapsed = round(end_time - start_time, 2)
        running = False

    current_time = time.time()

    if not game_win:
        if current_time - last_heart_loss_time >= heart_loss_interval:
            hearts -= 1
            last_heart_loss_time = current_time
            if hearts <= 0:
                game_over = True
                running = False

    obstacles = []
    for desk in desks:
        obstacles.append(desk.rect)
        for seat in desk.seats:
            obstacles.append(seat.rect)

    for ai in ai_agents:
        obstacles.append(ai.rect)

    # create empty seat periodically
    empty_seats = [seat for seat in all_seats if not seat.occupied]
    current_time = time.time()

    if len(empty_seats) == 0:
        wandering_ais = [ai for ai in ai_agents if ai.state == "wandering"]
        if len(wandering_ais) < 3:
            ai_agents.extend(create_wandering_ai(
                1, obstacles + [player.rect],
                screen_size=(screen_width, screen_height),
            ))

        if current_time >= next_despawn_time:
            ai_to_leave = get_ai_to_leave(ai_agents, player.rect)
            if ai_to_leave:
                ai_to_leave.despawn()
            next_despawn_time = current_time + np.random.exponential(scale=1 / Lambda)

    
    if empty_seats and not empty_seats[0].targeted:
        ai_to_sit(empty_seats[0], ai_agents, obstacles, screen_size=(screen_width, screen_height))
    
    # input 처리 시 obstacles 전달
    for ai in ai_agents:
        ai.update(player.rect, obstacles, screen_width, screen_height)

    player.handle_input(obstacles, screen_width, screen_height)
    player.update_animation()

    ai_agents = [ai for ai in ai_agents if not ai.offscreen]

    # 플레이어와 좌석 거리 계산 → 앉기 가능 좌석 탐색
    sit_target = None
    for desk in desks:
        for seat in desk.seats:
            if seat.can_sit(player.rect):
                sit_target = seat
                break
        if sit_target:
            break

    # '앉기' 입력
    keys = pygame.key.get_pressed()
    if sit_target and keys[pygame.K_SPACE] and not player.seated:
        player.sit(sit_target)
    

    # Draw objects and UI
    pygame.draw.rect(screen, (50, 50, 50), ui_region)
    for desk in desks:
        desk.draw(screen)
    for ai in ai_agents:
        ai.draw(screen)
    
    player.draw(screen)
    for i in range(hearts):
        screen.blit(heart_img, (20 + i * 35, ui_region.top + 10))

    if sit_target and not player.seated:
        text = font.render("Press Space Bar to sit down", True, (255, 255, 255))
        screen.blit(text, (screen_width // 2 - 100, 20))

    pygame.display.flip()
    clock.tick(60)

# Print game over message
pygame.time.delay(500)
screen.fill((0, 0, 0))

if game_win:
    message = f"You win! Time: {elapsed} sec"
else:
    message = f"You starved... Game Over."

end_text = font.render(message, True, (255, 255, 255))
screen.blit(end_text, (screen.get_width() // 2 - 200, screen.get_height() // 2))
pygame.display.flip()

pygame.time.delay(3000)
pygame.quit()
