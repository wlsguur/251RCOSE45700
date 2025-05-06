import pygame

class Player:
    def __init__(self, x, y, width=30, height=30, color=(0, 200, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 4
        self.seated = False

    def handle_input(self, obstacles, screen_width=800, screen_height=600):
        if self.seated:
            return

        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0

        if keys[pygame.K_LEFT]:
            move_x = -self.speed
        elif keys[pygame.K_RIGHT]:
            move_x = self.speed
        elif keys[pygame.K_UP]:
            move_y = -self.speed
        elif keys[pygame.K_DOWN]:
            move_y = self.speed

        # 이동 후보 위치 계산
        next_rect = self.rect.move(move_x, move_y)

        # 화면 경계 충돌 방지
        if next_rect.left < 0 or next_rect.right > screen_width:
            move_x = 0
        if next_rect.top < 0 or next_rect.bottom > screen_height:
            move_y = 0

        next_rect = self.rect.move(move_x, move_y)

        # 장애물과 충돌하지 않는 경우만 이동
        if not any(next_rect.colliderect(obs) for obs in obstacles):
            self.rect = next_rect

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def sit(self, seat):
        self.rect.center = seat.rect.center
        self.seated = True
        seat.sit()
