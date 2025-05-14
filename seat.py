import pygame

class Seat(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int = 20, height: int = 20):
        super().__init__()

        # 1️⃣ 이미지 불러오고 원하는 크기로 맞추기
        raw_img = pygame.image.load("chair.png")
        self.image = pygame.transform.smoothscale(raw_img, (width, height))

        # 2️⃣ 이미지 크기에 맞게 rect 생성 (충돌·위치 관리용)
        self.rect = self.image.get_rect(topleft=(x, y))

        # 3️⃣ 상태 변수
        self.occupied = False

        # 점유 상태일 때 깔아 줄 반투명 오버레이 한 장 만들어 둠
        self._overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        self._overlay.fill((180, 180, 0, 120))   # RGBA

    # ------------------------------------------------------------------
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
