import pygame
import random

class AIAgent:
    directions = ["up", "down", "left", "right"]

    def __init__(self, x, y, width=30, height=30, color=(100, 100, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.state = "wandering"  # seated, wandering, going_to_seat
        self.speed = 2
        self.target_seat = None
        self.paused_due_to_collision = False
        self.direction = random.choice(self.directions)  # 현재 진행 방향

    def set_seated(self, seat):
        self.rect.center = seat.rect.center
        self.state = "seated"
        seat.occupied = True

    def set_wandering(self):
        self.state = "wandering"
        self.target_seat = None
        self.direction = random.choice(self.directions)

    def go_to_seat(self, seat):
        self.state = "going_to_seat"
        self.target_seat = seat
        self.target_seat.occupied = True  # Reserve the seat
    
    def turn_left_or_right(self):
        turn_map = {
            "up": ["left", "right"],
            "down": ["right", "left"],
            "left": ["down", "up"],
            "right": ["up", "down"]
        }
        self.direction = random.choice(turn_map[self.direction])


    def update(self, player_rect, obstacles, screen_width, screen_height):
        safe_obstacles = [o for o in obstacles if o != self.rect]
        import pdb; pdb.set_trace()
        if self.state == "seated":
            return

        if self.paused_due_to_collision:
            if not self.rect.colliderect(player_rect):
                self.paused_due_to_collision = False
            else:
                return

        if self.rect.colliderect(player_rect):
            self.paused_due_to_collision = True
            return

        if self.state == "wandering":
            dx, dy = 0, 0
            if self.direction == "left":
                dx = -self.speed
            elif self.direction == "right":
                dx = self.speed
            elif self.direction == "up":
                dy = -self.speed
            elif self.direction == "down":
                dy = self.speed

            next_rect = self.rect.move(dx, dy)

            # 화면 경계나 장애물 충돌 시 방향 전환 (좌/우 회전)
            if (next_rect.left < 1 or next_rect.right > screen_width-1 or
                next_rect.top < 1 or next_rect.bottom > screen_height-1 or
                any(next_rect.colliderect(o) for o in safe_obstacles)):
                self.turn_left_or_right()
                print('help')
            else:
                self.rect = next_rect


        elif self.state == "going_to_seat" and self.target_seat:
            dx = self.target_seat.rect.centerx - self.rect.centerx
            dy = self.target_seat.rect.centery - self.rect.centery

            # 선택된 축 중 하나만 이동 (x 또는 y 중 큰 차이 우선)
            if abs(dx) > abs(dy):
                move_x = self.speed if dx > 0 else -self.speed
                move_y = 0
                self.direction = "right" if dx > 0 else "left"
            else:
                move_y = self.speed if dy > 0 else -self.speed
                move_x = 0
                self.direction = "down" if dy > 0 else "up"

            next_rect = self.rect.move(move_x, move_y)

            if not any(next_rect.colliderect(o) for o in safe_obstacles if o != self.target_seat.rect):
                self.rect = next_rect

            if self.rect.colliderect(self.target_seat.rect):
                self.state = "seated"
                self.rect.center = self.target_seat.rect.center

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
