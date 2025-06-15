import pygame
import os

class Player:
    def __init__(self, x, y, width=30, height=30, image_path='asset/img/boy_player.png', speed=4):
        self.load_animations(width, height)
        self.image = self.idle_frames[0]
        
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = speed
        self.seated = False
        self.current_seat = None
        self.spawn_center = None
        self.is_moving = False
        self.animation_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.animation_delay = 100 # milliseconds
        self.direction = 'right'

    def load_animations(self, width, height):
        # NOTE: 달리기 애니메이션을 위해서는 'asset/img/player/run' 폴더에 여러 이미지 파일이 필요합니다.
        # NOTE: 지금은 임시로 'boy_player.png'만 사용합니다.
        run_path = 'asset/img/player/run'

        self.run_frames = []
        if os.path.isdir(run_path):
             for file_name in sorted(os.listdir(run_path)):
                if file_name.endswith('.png'):
                    image = pygame.image.load(os.path.join(run_path, file_name)).convert_alpha()
                    self.run_frames.append(pygame.transform.scale(image, (width, height)))

        if not self.run_frames:
            # 달리기 프레임이 없을 경우, 기본 이미지로 대체
            player_img = pygame.image.load('asset/img/boy_player.png').convert_alpha()
            self.run_frames = [pygame.transform.scale(player_img, (width, height))]

        # 서있을 때 프레임 -> 달리기 애니메이션의 첫번째 프레임 사용
        self.idle_frames = [self.run_frames[0]]


    def handle_input(self, obstacles, screen_width=800, screen_height=600):
        keys = pygame.key.get_pressed()
        if self.seated:
            if keys[pygame.K_ESCAPE]:
                self.stand()
            return

        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        dy = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])

        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'

        if dx != 0 or dy != 0:
            self.is_moving = True
        else:
            self.is_moving = False

        next_rect = self.rect.move(dx * self.speed, dy * self.speed)
        
        if (0 <= next_rect.left and next_rect.right <= screen_width and
            0 <= next_rect.top  and next_rect.bottom <= screen_height and
            not any(next_rect.colliderect(obs) for obs in obstacles)):
            self.rect = next_rect

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

    def sit(self, seat):
        self.spawn_center = seat.spawn_pos
        self.rect.center = seat.rect.center
        self.seated = True
        self.current_seat = seat
        seat.sit()

    def stand(self):
        if self.current_seat:
            self.current_seat.leave()
        self.seated = False
        self.current_seat = None
        self.rect.center = self.spawn_center