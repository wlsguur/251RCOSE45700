import pygame
from seat import Seat

class Desk:
    def __init__(self, x, y, width=200, height=120):
        self.rect = pygame.Rect(x, y, width, height)
        self.seats = []
        self.create_seats()

    def create_seats(self):
        seat_width, seat_height = 30, 30
        gap = 40

        # 책상 위쪽에 좌석 3개
        for i in range(3):
            sx = self.rect.x + 25 + i * (seat_width + gap)
            sy = self.rect.y - seat_height - 10
            self.seats.append(Seat(sx, sy, seat_width, seat_height))

        # 책상 아래쪽에 좌석 3개
        for i in range(3):
            sx = self.rect.x + 25 + i * (seat_width + gap)
            sy = self.rect.y + self.rect.height + 10
            self.seats.append(Seat(sx, sy, seat_width, seat_height))

    def draw(self, screen):
        pygame.draw.rect(screen, (120, 80, 40), self.rect)
        for seat in self.seats:
            seat.draw(screen)
