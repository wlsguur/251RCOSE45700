import pygame

class Player:
    def __init__(self, x, y, width=30, height=30, image_path=None, speed=4):
        # 이미지 로드 및 크기 조정
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        else:
            # 이미지가 없으면 기본 색상 사각형
            self.image = None
            self.color = (0, 200, 0)

        # rect는 이미지 크기에 맞춰 생성
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x, y, width, height)

        self.speed = speed
        self.seated = False
        self.current_seat = None

    def handle_input(self, obstacles, screen_width=800, screen_height=600):
        if self.seated:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.stand()
            return

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        dy = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])   * self.speed

        next_rect = self.rect.move(dx, dy)
        if (0 <= next_rect.left and next_rect.right <= screen_width and
            0 <= next_rect.top  and next_rect.bottom <= screen_height and
            not any(next_rect.colliderect(obs) for obs in obstacles)):
            self.rect = next_rect

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    def sit(self, seat):
        self.rect.center = seat.rect.center
        self.seated = True
        self.current_seat = seat
        seat.sit()

    def stand(self):
        if self.current_seat:
            self.current_seat.leave()
        self.seated = False
        self.current_seat = None
