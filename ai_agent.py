import pygame
import random

class AIAgent:
    directions = ["up", "down", "left", "right"]

    def __init__(self, x, y, width=30, height=30, color=(100, 100, 255),image_path=None):
        # 이미지 로드 및 크기 조정
        if image_path:
            raw_img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_img, (width, height))
            
        else:
            self.image = None
            self.color = color

        # rect 생성 (이미지 있으면 이미지 크기에 맞춰 center, 없으면 x,y 기준)
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x, y, width, height)

        self.state = "wandering"  # seated, wandering, going_to_seat
        self.speed = 2
        self.target_seat = None
        self.paused_due_to_collision = False
        self.direction = random.choice(self.directions)

    def set_seated(self, seat):
        self.rect.center = seat.rect.center
        self.state = "seated"
        self.target_seat = seat
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
    
    def despawn(self, screen_width=800, screen_height=600):
        self.state = "leaving"
        self.target_seat.leave()
        self.target_seat = None

        x, y = self.rect.center

        distances = {
            "left": x,
            "right": screen_width - x,
            "top": y,
            "bottom": screen_height - y
        }

        closest_dir = min(distances, key=distances.get)

        if closest_dir == "left":
            self.leave_target = (-40, y)
        elif closest_dir == "right":
            self.leave_target = (screen_width + 40, y)
        elif closest_dir == "top":
            self.leave_target = (x, -40)
        elif closest_dir == "bottom":
            self.leave_target = (x, screen_height + 40)


    def update(self, player_rect, obstacles, screen_width, screen_height):
        safe_obstacles = [o for o in obstacles if o != self.rect]
        # import pdb; pdb.set_trace()
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
            if random.random() < 0.01:
                self.direction = random.choice(self.directions)

            dx = dy = 0
            if self.direction == "left":
                dx = -self.speed
            elif self.direction == "right":
                dx = self.speed
            elif self.direction == "up":
                dy = -self.speed
            else:
                dy = self.speed

            next_rect = self.rect.move(dx, dy)
            if (next_rect.left < 0 or next_rect.right > screen_width or
                next_rect.top < 0 or next_rect.bottom > screen_height or
                any(next_rect.colliderect(o) for o in obstacles if o != self.rect)):
                self.turn_left_or_right()
            else:
                self.rect = next_rect
        
        elif self.state == "leaving":
            if self.leave_target:
                dx = self.leave_target[0] - self.rect.centerx
                dy = self.leave_target[1] - self.rect.centery
                distance = max(1, (dx**2 + dy**2)**0.5)
                move_x = self.speed * dx / distance
                move_y = self.speed * dy / distance
                self.rect.centerx += int(move_x)
                self.rect.centery += int(move_y)

                if (self.rect.right < 0 or self.rect.left > screen_width or
                    self.rect.bottom < 0 or self.rect.top > screen_height):
                    self.offscreen = True
            return

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
        if hasattr(self, "image") and self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
