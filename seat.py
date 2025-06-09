import pygame

class Seat(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int = 20, height: int = 20, spawn_pos: tuple = None):
        super().__init__()

        raw_img = pygame.image.load("chair.png")
        self.image = pygame.transform.smoothscale(raw_img, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.occupied = False
        self.targeted = False
        self.spawn_pos = spawn_pos  # (x, y) tuple
        self.exit_path = None

        # 점유 상태일 때 깔아 줄 반투명 오버레이
        self._overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        self._overlay.fill((180, 180, 0, 120))   # RGBA

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
        if self.occupied:
            screen.blit(self._overlay, self.rect)

    def can_sit(self, player_rect: pygame.Rect) -> bool:
        return (not self.occupied) and self.rect.colliderect(player_rect.inflate(10, 10))

    def sit(self):
        self.occupied = True
        
    def leave(self):
        self.occupied = False
        self.targeted = False
