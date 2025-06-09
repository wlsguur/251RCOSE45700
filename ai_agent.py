import pygame
import random
from utils import find_path_bfs, euclidean_dist

class AIAgent:
    directions = ["up", "down", "left", "right"]

    def __init__(self, x, y, width=30, height=30, color=(100, 100, 255), image_path=None):
        if image_path:
            raw_img = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw_img, (width, height))
        else:
            self.image = None
            self.color = color

        self.rect = self.image.get_rect(topleft=(x, y)) if self.image else pygame.Rect(x, y, width, height)

        self.state = "wandering"  # wandering, going_to_seat, seated, leaving
        self.speed = 2
        self.direction = random.choice(self.directions)
        self.target_seat = None
        self.paused_due_to_collision = False

        self.path = []
        self.path_index = 0
        self.leave_target = None
        self.offscreen = False

    def set_seated(self, seat):
        self.rect.center = seat.rect.center
        self.state = "seated"
        self.target_seat = seat
        seat.occupied = True

    def set_wandering(self):
        self.state = "wandering"
        self.target_seat = None
        self.direction = random.choice(self.directions)

    def go_to_seat(self, seat, obstacles, screen_size=(800, 600)):
        self.state = "going_to_seat"
        self.target_seat = seat
        seat.targeted = True
        obstacles = [o for o in obstacles if not self.rect.colliderect(o)]
        self.path = find_path_bfs(self.rect.center, seat.spawn_pos, obstacles,
                                  screen_width=screen_size[0], screen_height=screen_size[1],
                                  step=4, agent_size=self.rect.width)
        self.path_index = 0
        # print(f"AI {self.rect.topleft} going to seat at {seat.rect.topleft}, path: {self.path}")

    def despawn(self):
        self.state = "leaving"
        if self.target_seat:
            self.path = self.target_seat.exit_path[:]  # 경로 복사
            self.path_index = 0
            self.target_seat.leave()
            self.target_seat = None
        else:
            self.offscreen = True  # 좌석 정보 없을 경우 안전장치


    def turn_left_or_right(self):
        turn_map = {
            "up": ["left", "right"],
            "down": ["right", "left"],
            "left": ["down", "up"],
            "right": ["up", "down"]
        }
        self.direction = random.choice(turn_map[self.direction])

    # 이동 로직
    def _move(self, dx, dy, obstacles, target=None):
        next_rect = self.rect.move(dx, dy)
        if not any(next_rect.colliderect(ob) for ob in obstacles if ob != (target.rect if target else self.rect)):
            self.rect = next_rect
            return True
        return False

    def _wander(self, obstacles, screen_width, screen_height):
        if random.random() < 0.01:
            self.direction = random.choice(self.directions)

        dx = dy = 0
        if self.direction == "left": dx = -self.speed
        elif self.direction == "right": dx = self.speed
        elif self.direction == "up": dy = -self.speed
        elif self.direction == "down": dy = self.speed

        next_rect = self.rect.move(dx, dy)
        if (next_rect.left < 0 or next_rect.right > screen_width or
            next_rect.top < 0 or next_rect.bottom > screen_height or
            any(next_rect.colliderect(ob) for ob in obstacles if ob != self.rect)):
            self.turn_left_or_right()
        else:
            self.rect = next_rect

    def update(self, player_rect, obstacles, screen_width, screen_height):
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

        if self.state in ["going_to_seat", "leaving"] and self.path:
            if self.path_index < len(self.path):
                next_pos = self.path[self.path_index]
                self.rect.center = next_pos
                self.path_index += 1
            else:
                if self.state == "going_to_seat":
                    self.state = "seated"
                    self.rect.center = self.target_seat.rect.center
                    self.target_seat.occupied = True
                elif self.state == "leaving":
                    self.offscreen = True
            return

        if self.state == "wandering":
            self._wander(obstacles, screen_width, screen_height)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

def create_wandering_ai(num_ais, ai_img_path, obstacles, screen_size=(800, 600), ai_size=30):
    ai_agents = []
    width, height = screen_size

    for _ in range(num_ais):
        while True:
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            # spawn at a random screen edge
            if edge == 'top':
                x = random.randint(0, width - ai_size)
                y = 0
            elif edge == 'bottom':
                x = random.randint(0, width - ai_size)
                y = height - ai_size
            elif edge == 'left':
                x = 0
                y = random.randint(0, height - ai_size)
            elif edge == 'right':
                x = width - ai_size
                y = random.randint(0, height - ai_size)
            # x, y = topleft corner of the AI rect
            ai = AIAgent(x, y, image_path=ai_img_path)
            if ai.rect.collidelist(obstacles) == -1 and ai.rect.collidelist(ai_agents) == -1:
                break
        
        ai.set_wandering()
        ai_agents.append(ai)

    return ai_agents
