import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# --- Константы для настройки игры ---
# Размеры окна
WIDTH = 800
HEIGHT = 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра с квадратиком")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Скорость игрока (шаг за раз, как в змейке)
PLAYER_SPEED = 5

# Параметры кружков-мишеней
CIRCLE_RADIUS = 15
CIRCLE_COLOR = BLUE
MAX_CIRCLES = 2 # Одновременно на поле
BOUNCING_SPEED = 3 # Скорость для отскакивающих кружков

# Параметры игрока (квадратика)
PLAYER_SIZE = 40
PLAYER_COLOR = GREEN
BARREL_LENGTH = 20 # Длина дула

# Параметры снаряда
BULLET_RADIUS = 5
BULLET_COLOR = RED
BULLET_SPEED = 10

# --- Игровые переменные ---
score = 0
start_time = pygame.time.get_ticks() # Время начала игры в миллисекундах

# Шрифты
font = pygame.font.Font(None, 36) # Стандартный шрифт, размер 36

# --- Классы игровых объектов ---

class Player:
    """
    Класс для управления игровым квадратиком.
    Отвечает за его позицию, движение, поворот дула и отрисовку.
    """
    def __init__(self):
        # Создаем прямоугольник для игрока по центру экрана
        self.rect = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT // 2 - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.color = PLAYER_COLOR
        self.barrel_angle = 0 # Угол поворота дула в радианах
        self.barrel_end_pos = (0, 0) # Конечная точка дула

    def update(self, mouse_pos):
        """
        Обновляет состояние игрока, в частности, поворачивает дуло в сторону мыши.
        """
        # Вычисляем разницу координат между курсором мыши и центром игрока
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        # Вычисляем угол поворота дула с помощью atan2 (обеспечивает правильный угол во всех квадрантах)
        self.barrel_angle = math.atan2(dy, dx)

        # Вычисляем конечную точку дула, исходящую из центра игрока
        self.barrel_end_pos = (
            self.rect.centerx + BARREL_LENGTH * math.cos(self.barrel_angle),
            self.rect.centery + BARREL_LENGTH * math.sin(self.barrel_angle)
        )

    def move(self, dx, dy):
        """
        Перемещает игрока на заданное смещение (dx, dy), умноженное на скорость.
        Ограничивает движение игрока пределами экрана.
        """
        self.rect.x += dx * PLAYER_SPEED
        self.rect.y += dy * PLAYER_SPEED

        # Ограничиваем движение игрока пределами экрана
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def draw(self, screen):
        """
        Отрисовывает квадратик и его дуло на экране.
        """
        pygame.draw.rect(screen, self.color, self.rect)
        # Рисуем дуло от центра квадратика до вычисленной конечной точки
        pygame.draw.line(screen, BLACK, self.rect.center, self.barrel_end_pos, 3)

class Bullet:
    """
    Класс для управления снарядами, вылетающими из дула игрока.
    Отвечает за их движение и отрисовку.
    """
    def __init__(self, start_pos, target_pos):
        self.pos = list(start_pos) # Текущая позиция снаряда (используем список, чтобы можно было изменять)
        self.color = BULLET_COLOR
        self.radius = BULLET_RADIUS

        # Вычисляем направление движения снаряда
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: # Избегаем деления на ноль, если start_pos и target_pos совпадают
            self.direction = (0, 0)
        else:
            # Нормализуем вектор направления, чтобы получить единичный вектор
            self.direction = (dx / dist, dy / dist)

    def update(self):
        """
        Обновляет позицию снаряда, перемещая его в заданном направлении.
        """
        self.pos[0] += self.direction[0] * BULLET_SPEED
        self.pos[1] += self.direction[1] * BULLET_SPEED

    def draw(self, screen):
        """
        Отрисовывает снаряд (круг) на экране.
        """
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

    def is_offscreen(self):
        """
        Проверяет, вышел ли снаряд за пределы игрового окна.
        """
        return (self.pos[0] < 0 or self.pos[0] > WIDTH or
                self.pos[1] < 0 or self.pos[1] > HEIGHT)

class CircleTarget:
    """
    Класс для управления кружками-мишенями.
    Отвечает за их позицию, движение (если движутся) и отрисовку.
    """
    def __init__(self):
        self.radius = CIRCLE_RADIUS
        self.color = CIRCLE_COLOR
        # Случайная позиция при создании, чтобы кружок не выходил за границы
        self.pos = [random.randint(self.radius, WIDTH - self.radius),
                    random.randint(self.radius, HEIGHT - self.radius)]
        self.is_bouncing = False # Флаг, указывающий, движется ли кружок
        self.direction = [0, 0] # Вектор направления для отскакивающих кружков

    def set_bouncing_direction(self):
        """
        Устанавливает случайное начальное направление для отскакивающего кружка.
        """
        angle = random.uniform(0, 2 * math.pi) # Случайный угол в радианах
        self.direction = [BOUNCING_SPEED * math.cos(angle), BOUNCING_SPEED * math.sin(angle)]
        self.is_bouncing = True

    def update(self):
        """
        Обновляет позицию кружка, если он движется.
        Обрабатывает отскоки от стенок.
        """
        if self.is_bouncing:
            self.pos[0] += self.direction[0]
            self.pos[1] += self.direction[1]

            # Отскок от стенок: меняем направление по соответствующей оси
            if self.pos[0] - self.radius < 0 or self.pos[0] + self.radius > WIDTH:
                self.direction[0] *= -1 # Меняем горизонтальное направление
            if self.pos[1] - self.radius < 0 or self.pos[1] + self.radius > HEIGHT:
                self.direction[1] *= -1 # Меняем вертикальное направление

    def draw(self, screen):
        """
        Отрисовывает кружок на экране.
        """
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

# --- Создание игровых объектов ---
player = Player()
bullets = [] # Список для хранения всех активных снарядов
circles = [] # Список для хранения всех активных кружков-мишеней

# --- Главный игровой цикл ---
running = True
clock = pygame.time.Clock() # Объект для контроля частоты кадров

while running:
    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Закрываем игру при нажатии кнопки "закрыть"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3: # Правая кнопка мыши (кнопка 1 - левая, 2 - средняя)
                # Создаем новый снаряд, исходящий из конца дула
                bullets.append(Bullet(player.barrel_end_pos, pygame.mouse.get_pos()))

    # --- Движение игрока по нажатию клавиш ---
    keys = pygame.key.get_pressed()
    # Обрабатываем нажатия A, S, W, D для перемещения
    if keys[pygame.K_a]: # Влево
        player.move(-1, 0)
    if keys[pygame.K_d]: # Вправо
        player.move(1, 0)
    if keys[pygame.K_w]: # Вверх
        player.move(0, -1)
    if keys[pygame.K_s]: # Вниз
        player.move(0, 1)

    # --- Обновление состояний игровых объектов ---
    # Обновляем поворот дула игрока в сторону курсора мыши
    player.update(pygame.mouse.get_pos())

    # Обновляем все активные снаряды и удаляем те, что вышли за экран
    for bullet in bullets[:]: # Итерируем по копии списка, чтобы безопасно удалять элементы
        bullet.update()
        if bullet.is_offscreen():
            bullets.remove(bullet)

    # Генерируем новые кружки, если их меньше MAX_CIRCLES
    while len(circles) < MAX_CIRCLES:
        new_circle = CircleTarget()
        if score >= 10:
            new_circle.set_bouncing_direction() # Запускаем движение, если счет >= 10
        circles.append(new_circle)

    # Обновляем все активные кружки
    for circle in circles:
        circle.update()

    # --- Проверка столкновений снарядов с кружками ---
    # Перебираем все снаряды и все кружки
    for bullet in bullets[:]:
        for circle in circles[:]:
            # Вычисляем расстояние между центром снаряда и центром кружка
            distance = math.sqrt((bullet.pos[0] - circle.pos[0])**2 + (bullet.pos[1] - circle.pos[1])**2)
            # Если расстояние меньше суммы радиусов, значит, произошло столкновение
            if distance < bullet.radius + circle.radius:
                # Столкновение произошло! Удаляем снаряд и кружок
                bullets.remove(bullet)
                circles.remove(circle)
                score += 1 # Увеличиваем счет
                break # Выходим из внутреннего цикла, так как снаряд уже удален

    # --- Отрисовка ---
    SCREEN.fill(WHITE) # Заполняем весь экран белым цветом (очистка предыдущего кадра)

    # Отрисовываем все игровые объекты
    player.draw(SCREEN)
    for bullet in bullets:
        bullet.draw(SCREEN)
    for circle in circles:
        circle.draw(SCREEN)

    # --- Отображение таймера и счета ---
    # Вычисляем прошедшее время в секундах
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    timer_text = font.render(f"Время: {elapsed_time}", True, BLACK) # Рендерим текст таймера
    score_text = font.render(f"Счет: {score}", True, BLACK) # Рендерим текст счета

    # Размещаем текст в правом верхнем углу
    SCREEN.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))
    SCREEN.blit(score_text, (WIDTH - score_text.get_width() - 10, 50))

    # --- Обновление экрана ---
    pygame.display.flip() # Обновляем весь экран, чтобы показать изменения

    # --- Ограничение FPS (кадров в секунду) ---
    clock.tick(60) # Устанавливаем максимальную частоту кадров в 60 FPS

# Завершение работы Pygame
pygame.quit()
