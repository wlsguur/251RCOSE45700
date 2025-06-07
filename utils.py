from math import hypot
from collections import deque
import pygame

def get_ai_to_leave(ai_agents, player_rect):
    px, py = player_rect.center

    wandering_ais = [ai for ai in ai_agents if ai.state == "wandering"]
    if not wandering_ais:
        return None

    avg_x = sum(ai.rect.centerx for ai in wandering_ais) / len(wandering_ais)
    avg_y = sum(ai.rect.centery for ai in wandering_ais) / len(wandering_ais)

    mid_x = (px + avg_x) / 2
    mid_y = (py + avg_y) / 2

    seated_ais = [ai for ai in ai_agents if ai.state == "seated"]
    if not seated_ais:
        return None

    def dist_to_mid(ai):
        dx = ai.rect.centerx - mid_x
        dy = ai.rect.centery - mid_y
        return hypot(dx, dy)

    return min(seated_ais, key=dist_to_mid)

def find_path_bfs(start, goal, obstacles, screen_width=800, screen_height=600, step=1):
    """
    start: (x, y) 튜플 (시작점 중심 좌표)
    goal: (x, y) 튜플 (도착점 중심 좌표)
    obstacles: pygame.Rect 리스트
    step: 이동 단위 (작게 할수록 세밀, 크게 할수록 성능↑)
    return: [(x1, y1), (x2, y2), ...] 식의 경로 리스트 또는 None
    """
    
    def is_blocked(x, y):
        point_rect = pygame.Rect(x, y, step, step)
        if not (0 <= x < screen_width and 0 <= y < screen_height):
            return True
        return any(point_rect.colliderect(ob) for ob in obstacles)

    start = (round(start[0] / step) * step, round(start[1] / step) * step)
    goal = (round(goal[0] / step) * step, round(goal[1] / step) * step)

    queue = deque()
    queue.append(start)
    visited = {start: None}
    # import pdb; pdb.set_trace()
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = visited[current]
            path.reverse()
            return path

        x, y = current
        for dx, dy in [(-step, 0), (step, 0), (0, -step), (0, step)]:
            next_pos = (x + dx, y + dy)
            if next_pos not in visited and not is_blocked(*next_pos):
                visited[next_pos] = current
                queue.append(next_pos)

    return None

def euclidean_dist(p1, p2):
    return hypot(p1[0] - p2[0], p1[1] - p2[1])