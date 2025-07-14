import pygame
import sys
import math
import random

# Window settings
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Resource colors
RESOURCE_COLORS = {
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'stone': (128, 128, 128),
    'clay': (210, 105, 30),
    'oil': (0, 0, 0),
    'wool': (255, 255, 255),
    'rye': (173, 255, 47),
    'wood': (34, 139, 34)
}

SEA_COLOR = (0, 105, 148)
HEX_SIZE = 40

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Колонизаторы")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

# Players and resources
players = [
    {'name': 'Игрок 1', 'resources': {res: 0 for res in RESOURCE_COLORS}},
    {'name': 'Игрок 2', 'resources': {res: 0 for res in RESOURCE_COLORS}},
]
current_player_index = 0

# Camera
offset_x, offset_y = 0, 0
zoom = 1.0

def generate_fixed_islands(total_hexes_needed, max_radius=10):
    """Generate islands consisting of hex coordinates."""
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

# Hex helpers

def hex_to_pixel(q, r, size):
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 3/2 * r
    return x, y

def draw_hex(surface, color, x, y, size):
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        dx = size * math.cos(angle)
        dy = size * math.sin(angle)
        points.append((x + dx, y + dy))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 1)

# Axial direction vectors for neighbour calculations
DIRECTIONS = [
    (1, 0),   # East
    (1, -1),  # North-East
    (0, -1),  # North-West
    (-1, 0),  # West
    (-1, 1),  # South-West
    (0, 1),   # South-East
]


def vertex_adjacent_hexes(q, r, corner):
    """Return up to three hexes that touch a given vertex."""
    results = {(q, r)}
    dq1, dr1 = DIRECTIONS[corner % 6]
    dq2, dr2 = DIRECTIONS[(corner - 1) % 6]
    results.add((q + dq1, r + dr1))
    results.add((q + dq2, r + dr2))
    return results

# Map generation
hexes = generate_fixed_islands(total_hexes_needed=300)
random.shuffle(hexes)
hex_resource_map = {}
hex_number_map = {}

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

total_hexes = len(hexes)
remaining_hexes = set(hexes)

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
                hex_number_map[coord] = random.randint(2, 12)
        count += len(cluster)

# Structures on map (starting settlements)
# Settlements are placed on hex vertices represented as (q, r, corner)
structures = {}
start_vertices = set()
while len(start_vertices) < 4:
    hq, hr = random.choice(list(hex_resource_map.keys()))
    corner = random.randint(0, 5)
    start_vertices.add((hq, hr, corner))

start_vertices = list(start_vertices)
structures[start_vertices[0]] = {'player': 0, 'type': 'settlement'}
structures[start_vertices[1]] = {'player': 0, 'type': 'settlement'}
structures[start_vertices[2]] = {'player': 1, 'type': 'settlement'}
structures[start_vertices[3]] = {'player': 1, 'type': 'settlement'}

# Simple button implementation
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.visible = True

    def draw(self, surface):
        if not self.visible:
            return
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.visible and self.rect.collidepoint(pos)

# UI buttons
button_start_turn = Button((WIDTH//2 - 60, HEIGHT - 60, 120, 40), 'Начать ход')
button_end_turn = Button((WIDTH//2 - 60, HEIGHT - 60, 120, 40), 'Закончить')
button_end_turn.visible = False

# Dice result
dice_result = None


def roll_dice():
    return random.randint(1, 6) + random.randint(1, 6)


def produce_resources(dice_value):
    for (q, r, corner), data in structures.items():
        for hq, hr in vertex_adjacent_hexes(q, r, corner):
            if hex_number_map.get((hq, hr)) == dice_value:
                resource = hex_resource_map.get((hq, hr))
                if resource is None:
                    continue
                player = players[data['player']]
                if data['type'] == 'settlement':
                    amount = 1
                elif data['type'] == 'city':
                    amount = 2
                else:
                    amount = 3  # upgraded city
                player['resources'][resource] += amount


def draw_resources(surface, player, x):
    y = 50
    for res, color in RESOURCE_COLORS.items():
        pygame.draw.rect(surface, color, (x, y, 20, 20))
        count = player['resources'][res]
        txt = font.render(str(count), True, (0, 0, 0))
        surface.blit(txt, (x + 25, y))
        y += 30


def draw_structures(surface):
    for (q, r, corner), data in structures.items():
        hx, hy = hex_to_pixel(q, r, HEX_SIZE * zoom)
        hx += WIDTH // 2 + offset_x
        hy += HEIGHT // 2 + offset_y
        angle = math.radians(60 * corner - 30)
        vx = hx + HEX_SIZE * zoom * math.cos(angle)
        vy = hy + HEX_SIZE * zoom * math.sin(angle)
        color = (255, 0, 0) if data['player'] == 0 else (0, 0, 255)
        pygame.draw.circle(surface, color, (int(vx), int(vy)), int(8 * zoom))


# Main loop
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
            elif event.button == 1:
                if button_start_turn.is_clicked(event.pos):
                    dice_result = roll_dice()
                    produce_resources(dice_result)
                    button_start_turn.visible = False
                    button_end_turn.visible = True
                elif button_end_turn.is_clicked(event.pos):
                    button_end_turn.visible = False
                    button_start_turn.visible = True
                    dice_result = None
                    current_player_index = (current_player_index + 1) % len(players)
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
        num = hex_number_map.get((q, r))
        if num:
            num_surf = font.render(str(num), True, (0, 0, 0))
            num_rect = num_surf.get_rect(center=(x, y))
            screen.blit(num_surf, num_rect)

    draw_structures(screen)

    draw_resources(screen, players[current_player_index], 10)

    if dice_result is not None:
        dice_surf = font.render(f'Бросок: {dice_result}', True, (0,0,0))
        screen.blit(dice_surf, (WIDTH//2 - 40, 10))

    button_start_turn.draw(screen)
    button_end_turn.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
