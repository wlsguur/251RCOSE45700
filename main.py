# main.py (좌석 생성 + 플레이어 앉기까지 구현)
import pygame
import random
from desk import Desk
from seat import Seat
from player import Player
from ai_agent import AIAgent

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Seat Game - 앉기 기능")
clock = pygame.time.Clock()

# 플레이어 초기 위치 (화면 가운데)
player = Player(400, 300,width=40, height=40, image_path="asset/img/boy_player.png")

# 책상들 생성 (화면을 4분할 후 각 사분면에 배치)
desks = []
desk_w, desk_h = 230, 110
margin_x, margin_y = 90, 100

positions = [
    (margin_x, margin_y),                         # 좌상
    (800 - margin_x - desk_w, margin_y),          # 우상
    (margin_x, 600 - margin_y - desk_h),          # 좌하
    (800 - margin_x - desk_w, 600 - margin_y - desk_h)  # 우하
]

for x, y in positions:
    desks.append(Desk(x, y, desk_w, desk_h))

all_seats = []
for desk in desks:
    all_seats.extend(desk.seats)

# 모든 좌석에 AI 배치
ai_agents = []
# for seat in all_seats:
#     ai = AIAgent(seat.rect.x, seat.rect.y)
#     ai.set_seated(seat)
#     ai_agents.append(ai)

# wandering AI 3명 추가
wandering_ai_spawn_zone = [(20, 50), (300, 30), (400, 100)]
for x, y in wandering_ai_spawn_zone:
    ai = AIAgent(x, y,image_path='asset/img/ai_agent.png')
    ai.set_wandering()
    ai_agents.append(ai)

# 장애물 목록
obstacles = [desk.rect for desk in desks]
for desk in desks:
    for seat in desk.seats:
        obstacles.append(seat.rect)

# 게임 루프
running = True
font = pygame.font.SysFont(None, 24)

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


    # input 처리 시 obstacles 전달
    for ai in ai_agents:
        ai.update(player.rect, obstacles, screen.get_width(), screen.get_height())

    player.handle_input(obstacles, screen.get_width(), screen.get_height())


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
    
    elif sit_target and keys[pygame.K_SPACE] and player.seated:
        player.stand()

    # 그리기
    for desk in desks:
        desk.draw(screen)
    for ai in ai_agents:
        ai.draw(screen)
    player.draw(screen)

    # 안내 메시지
    if sit_target and not player.seated:
        text = font.render("Press Space Bar to sit down", True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - 100, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
