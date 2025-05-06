import pygame

class Seat:
    def __init__(self, x, y, width=20, height=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.occupied = False
        self.color_empty = (200, 200, 0)
        self.color_occupied = (150, 0, 0)

    def draw(self, screen):
        color = self.color_occupied if self.occupied else self.color_empty
        pygame.draw.rect(screen, color, self.rect)

    def can_sit(self, player_rect):
        # 좌석 바로 앞에 플레이어가 있는지 확인 (단순 거리 기반)
        return not self.occupied and self.rect.colliderect(player_rect.inflate(10, 10))

    def sit(self):
        self.occupied = True
