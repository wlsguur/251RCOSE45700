import pygame
import random
import os
from utils import find_path_bfs, euclidean_dist

class AIAgent:
    def __init__(self, x, y, width=30, height=30):
        self.load_animations(width, height)
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.state = "wandering"  # wandering, going_to_seat, seated, leaving
        self.speed = 2
        self.target_seat = None
        self.paused_due_to_collision = False

        self.path = []
        self.path_index = 0
        self.leave_target = None
        self.offscreen = False

        # Animation attributes
        self.is_moving = False
        self.direction = 'right' # 'left' or 'right'
        self.animation_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_delay = 100  # milliseconds
    
    def load_animations(self, width, height):
        run_path = 'asset/img/ai/run'
        self.run_frames = []
        if os.path.isdir(run_path) and os.listdir(run_path):
            for file_name in sorted(os.listdir(run_path)):
                if file_name.endswith('.png'):
                    image = pygame.image.load(os.path.join(run_path, file_name)).convert_alpha()
                    self.run_frames.append(pygame.transform.scale(image, (width, height)))

        if not self.run_frames:
            default_img_path = 'asset/img/ai_agent.png'
            if os.path.exists(default_img_path):
                image = pygame.image.load(default_img_path).convert_alpha()
                self.run_frames.append(pygame.transform.scale(image, (width, height)))
            else: # Fallback color if no image exists
                surf = pygame.Surface((width, height))
                surf.fill((100, 100, 255))
                self.run_frames.append(surf)

        self.idle_frames = [self.run_frames[0]]


    def set_seated(self, seat):
        self.rect.center = seat.rect.center
        self.state = "seated"
        self.target_seat = seat
        seat.occupied = True

    def set_wandering(self):
        self.state = "wandering"
        self.target_seat = None

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

    def _wander(self, obstacles, screen_width, screen_height):
        if random.random() < 0.01:
            directions = ["left", "right", "up", "down"]
            current_dir_index = directions.index(self.direction) if self.direction in ["left", "right", "up", "down"] else 0
            new_dir_index = (current_dir_index + random.choice([-1, 1])) % 4
            self.direction = directions[new_dir_index]

        dx = dy = 0
        if self.direction == "left": dx = -self.speed
        elif self.direction == "right": dx = self.speed
        elif self.direction == "up": dy = -self.speed
        elif self.direction == "down": dy = self.speed
        
        next_rect = self.rect.move(dx, dy)
        if (next_rect.left < 0 or next_rect.right > screen_width or
            next_rect.top < 0 or next_rect.bottom > screen_height or
            any(next_rect.colliderect(ob) for ob in obstacles if ob != self.rect)):
            # Turn on collision
            turn_map = {"up": "down", "down": "up", "left": "right", "right": "left"}
            self.direction = turn_map.get(self.direction, "right")
        else:
            self.rect = next_rect

    def update(self, player_rect, obstacles, screen_width, screen_height):
        prev_x = self.rect.x
        
        if self.state == "seated":
            self.is_moving = False
        else:
            self.is_moving = True

        if self.paused_due_to_collision:
            if not self.rect.colliderect(player_rect):
                self.paused_due_to_collision = False
            else:
                self.is_moving = False
                self.update_animation()
                return

        if self.rect.colliderect(player_rect):
            self.paused_due_to_collision = True
            self.is_moving = False
            self.update_animation()
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
        
        elif self.state == "wandering":
            self._wander(obstacles, screen_width, screen_height)

        # Update direction based on movement
        if self.rect.x < prev_x:
            self.direction = 'left'
        elif self.rect.x > prev_x:
            self.direction = 'right'
            
        self.update_animation()

    def update_animation(self):
        now = pygame.time.get_ticks()
        
        if self.is_moving:
            if now - self.last_update_time > self.animation_delay:
                self.last_update_time = now
                self.animation_index = (self.animation_index + 1) % len(self.run_frames)
                current_frame = self.run_frames[self.animation_index]
                if self.direction == 'left':
                    self.image = pygame.transform.flip(current_frame, True, False)
                else:
                    self.image = current_frame
        else:
            self.animation_index = 0
            current_frame = self.idle_frames[0]
            if self.direction == 'left':
                self.image = pygame.transform.flip(current_frame, True, False)
            else:
                self.image = current_frame

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def create_wandering_ai(num_ais, obstacles, screen_size=(800, 600), ai_size=30):
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
            ai = AIAgent(x, y)
            if ai.rect.collidelist(obstacles) == -1 and ai.rect.collidelist(ai_agents) == -1:
                break
        
        ai.set_wandering()
        ai_agents.append(ai)

    return ai_agents
