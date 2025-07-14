import pygame
import sys
import math
import random

# Настройки окна
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Цвета ресурсов
RESOURCE_COLORS = {
    'gold': (255, 215, 0),       # 5%
    'silver': (192, 192, 192),   # 10%
    'stone': (128, 128, 128),    # 13%
    'clay': (210, 105, 30),      # 15%
    'oil': (0, 0, 0),            # 2%
    'wool': (255, 255, 255),     # 15%
    'rye': (173, 255, 47),       # 15%
    'wood': (34, 139, 34)        # 25%
}

SEA_COLOR = (0, 105, 148)
HEX_SIZE = 40

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Колонизаторы")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

# Камера
offset_x, offset_y = 0, 0
zoom = 1.0

# Генерация фиксированного количества шестиугольников с островами
def generate_fixed_islands(total_hexes_needed, max_radius=10):
    hexes = set()
    attempts = 0
    while len(hexes) < total_hexes_needed and attempts < 100:
        attempts += 1
        cx = random.randint(-max_radius, max_radius)
        cy = random.randint(-max_radius, max_radius)
        size = random.randint(5, 20)
        frontier = [(cx, cy)]
        visited = set(frontier)
        count = 0
        while frontier and len(hexes) < total_hexes_needed and count < size:
            q, r = frontier.pop(0)
            if (q, r) not in hexes:
                hexes.add((q, r))
                count += 1
            for dq, dr in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]:
                neighbor = (q + dq, r + dr)
                if neighbor not in visited and random.random() < 0.6:
                    frontier.append(neighbor)
                    visited.add(neighbor)
    return list(hexes)

# Центрированная гекс-сетка (сторона вверх у карты, вершина вверх у ячеек)
def hex_to_pixel(q, r, size):
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 3/2 * r
    return x, y

def draw_hex(surface, color, x, y, size):
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)  # Вершина вверх (ориентация)
        dx = size * math.cos(angle)
        dy = size * math.sin(angle)
        points.append((x + dx, y + dy))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 1)

# Создание карты из ровно 120 шестиугольников
hexes = generate_fixed_islands(total_hexes_needed=300)
random.shuffle(hexes)
hex_resource_map = {}

# Процентное распределение ресурсов
resource_distribution = {
    'gold': 0.05,
    'silver': 0.08,
    'stone': 0.15,
    'clay': 0.15,
    'oil': 0.02,
    'wool': 0.15,
    'rye': 0.15,
    'wood': 0.25
}

# Генерация месторождений (по несколько кластеров на ресурс)
total_hexes = len(hexes)
remaining_hexes = set(hexes)
allocated = 0

for resource, percent in resource_distribution.items():
    target_count = round(percent * total_hexes)
    count = 0
    deposit_attempts = 0
    while count < target_count and deposit_attempts < 10:
        deposit_attempts += 1
        deposit_size = random.randint(2, max(3, target_count // 3))
        start = random.choice(list(remaining_hexes))
        cluster = [start]
        visited = {start}
        frontier = [start]

        while frontier and len(cluster) < deposit_size:
            q, r = frontier.pop(0)
            for dq, dr in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]:
                neighbor = (q + dq, r + dr)
                if neighbor in remaining_hexes and neighbor not in visited and random.random() < 0.5:
                    frontier.append(neighbor)
                    cluster.append(neighbor)
                    visited.add(neighbor)
                    if len(cluster) + count >= target_count:
                        break

        for coord in cluster:
            if coord in remaining_hexes:
                hex_resource_map[coord] = resource
                remaining_hexes.remove(coord)
        count += len(cluster)

# Главный цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                zoom *= 1.1
            elif event.button == 5:
                zoom /= 1.1
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                offset_x += event.rel[0]
                offset_y += event.rel[1]

    screen.fill(SEA_COLOR)

    for q, r in hexes:
        x, y = hex_to_pixel(q, r, HEX_SIZE * zoom)
        x += WIDTH // 2 + offset_x
        y += HEIGHT // 2 + offset_y

        resource = hex_resource_map.get((q, r), None)
        color = RESOURCE_COLORS[resource] if resource else (200, 200, 200)

        draw_hex(screen, color, x, y, HEX_SIZE * zoom)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
