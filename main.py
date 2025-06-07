import pygame
import random
from desk import Desk
from seat import Seat
from player import Player
from ai_agent import AIAgent
import time
from utils import get_ai_to_leave, find_path_bfs, euclidean_dist, ai_to_sit

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("ToHak")
clock = pygame.time.Clock()

player = Player(400, 300,width=40, height=40, image_path="asset/img/boy_player.png")

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

screen_width, screen_height = screen.get_width(), screen.get_height()
margin = 10

for seat in all_seats:
    x, y = seat.rect.center
    targets = [
        (margin, y),
        (screen_width - margin, y),
        (x, margin),
        (x, screen_height - margin)
    ]

    target = min(targets, key=lambda p: euclidean_dist((x, y), p))
    static_obstacles = [obstacle for obstacle in static_obstacles if not seat.rect.colliderect(obstacle)]
    path = find_path_bfs((x, y), target, static_obstacles, screen_width, screen_height)
    seat.exit_path = path

# 모든 좌석에 AI 배치
ai_agents = []
for seat in all_seats:
    ai = AIAgent(seat.rect.x, seat.rect.y, image_path='asset/img/ai_agent.png')
    ai.set_seated(seat)
    ai_agents.append(ai)

# wandering AI 3명 추가
wandering_ai_spawn_zone = [(20, 50), (300, 30), (400, 100)]
for x, y in wandering_ai_spawn_zone:
    ai = AIAgent(x, y, image_path='asset/img/ai_agent.png')
    ai.set_wandering()
    ai_agents.append(ai)

# 장애물 목록
obstacles = [desk.rect for desk in desks]
for desk in desks:
    for seat in desk.seats:
        obstacles.append(seat.rect)

running = True
font = pygame.font.SysFont(None, 24)

last_despawn_time = time.time()

while running:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
        if current_time - last_despawn_time >= 5:
            ai_to_leave = get_ai_to_leave(ai_agents, player.rect)
            ai_to_leave.despawn()
            last_despawn_time = current_time
    else:
        last_despawn_time = current_time
    
    if empty_seats and not empty_seats[0].targeted:
        ai_to_sit(empty_seats[0], ai_agents, obstacles, screen_size=(screen.get_width(), screen.get_height()))
    
    # input 처리 시 obstacles 전달
    for ai in ai_agents:
        ai.update(player.rect, obstacles, screen.get_width(), screen.get_height())

    player.handle_input(obstacles, screen.get_width(), screen.get_height())

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
    
    for desk in desks:
        desk.draw(screen)
    for ai in ai_agents:
        ai.draw(screen)
    player.draw(screen)

    if sit_target and not player.seated:
        text = font.render("Press Space Bar to sit down", True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - 100, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
