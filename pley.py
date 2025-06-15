import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# --- Константы для настройки игры ---
# Размеры окна
WIDTH = 1200
HEIGHT = 800
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
BOUNCING_SPEED = 3 # Скорость для отскакивающих кружков
BULLET_SPEED = 10

# Параметры игрока (квадратика) - ОПРЕДЕЛЯЮТСЯ РАНЬШЕ!
PLAYER_SIZE = 40
PLAYER_COLOR = GREEN
BARREL_LENGTH = 20 # Длина дула

# Параметры кружков-мишеней - ОПРЕДЕЛЯЮТСЯ РАНЬШЕ!
CIRCLE_RADIUS = 15
CIRCLE_COLOR = BLUE
# Максимальное количество кружков на экране
MAX_CIRCLES = 30

# Параметры защитного круга вокруг игрока
HAZARD_RADIUS = 50
HAZARD_RED_DURATION = 2000  # миллисекунды
HAZARD_BLACK_DURATION = 500

# Параметры снаряда
BULLET_RADIUS = 5
BULLET_COLOR = RED


# НОВЫЕ КОНСТАНТЫ: Минимальное безопасное расстояние
# Теперь они определяются ПОСЛЕ PLAYER_SIZE и CIRCLE_RADIUS
# Минимальное расстояние от центра нового кружка до центра игрока:
# (радиус кружка) + (половина размера игрока) + (небольшой отступ)
MIN_SPAWN_DISTANCE = CIRCLE_RADIUS + (PLAYER_SIZE / 2) + 10

# Минимальное расстояние между центрами двух кружков:
# (два радиуса кружка) + (небольшой отступ)
MIN_CIRCLE_DISTANCE = (CIRCLE_RADIUS * 2) + 10


# --- Игровые переменные ---
score = 0
start_time = pygame.time.get_ticks() # Время начала игры в миллисекундах
game_over = False # Флаг для состояния конца игры

# Шрифты
font = pygame.font.Font(None, 36) # Стандартный шрифт, размер 36
game_over_font = pygame.font.Font(None, 72) # Шрифт для сообщения "Игра окончена"

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
        self.is_alive = True # Флаг состояния жизни игрока

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
    # МЕТОД __init__ ИЗМЕНЕН! Теперь принимает ссылки на игрока и другие кружки
    def __init__(self, player_obj, existing_circles):
        self.radius = CIRCLE_RADIUS
        self.color = CIRCLE_COLOR
        self.is_bouncing = False # Флаг, указывающий, движется ли кружок
        self.direction = [0, 0] # Вектор направления для отскакивающих кружков

        # НОВОЕ: Генерация позиции с учетом минимального расстояния
        spawn_successful = False
        attempts = 0
        max_attempts = 100 # Ограничиваем попытки, чтобы избежать бесконечного цикла

        while not spawn_successful and attempts < max_attempts:
            # Генерируем случайную позицию в пределах экрана
            new_x = random.randint(self.radius, WIDTH - self.radius)
            new_y = random.randint(self.radius, HEIGHT - self.radius)
            temp_pos = [new_x, new_y]

            # Проверяем расстояние до игрока
            distance_to_player = math.sqrt(
                (temp_pos[0] - player_obj.rect.centerx)**2 +
                (temp_pos[1] - player_obj.rect.centery)**2
            )

            # Если слишком близко к игроку, пробуем снова
            if distance_to_player < MIN_SPAWN_DISTANCE:
                attempts += 1
                continue

            # Проверяем расстояние до других кружков
            is_too_close_to_other_circles = False
            for other_circle in existing_circles:
                distance_to_other_circle = math.sqrt(
                    (temp_pos[0] - other_circle.pos[0])**2 +
                    (temp_pos[1] - other_circle.pos[1])**2
                )
                if distance_to_other_circle < MIN_CIRCLE_DISTANCE:
                    is_too_close_to_other_circles = True
                    break # Нашли слишком близкий кружок, нет смысла проверять дальше

            # Если слишком близко к другому кружку, пробуем снова
            if is_too_close_to_other_circles:
                attempts += 1
                continue

            # Если все проверки пройдены, позиция подходит
            self.pos = temp_pos
            spawn_successful = True

        # Если не удалось найти подходящую позицию за max_attempts, размещаем где попало (маловероятно)
        if not spawn_successful:
            self.pos = [random.randint(self.radius, WIDTH - self.radius),
                        random.randint(self.radius, HEIGHT - self.radius)]
            # print("Предупреждение: не удалось найти свободное место для кружка!") # Можно включить для отладки

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

# --- Инициализация кружков при старте игры (два кружка, как ты и просил) ---
# НОВОЕ: Передаем player и circles в конструктор CircleTarget
circles.append(CircleTarget(player, circles))
circles.append(CircleTarget(player, circles))

# Переменные для защитного круга
hazard_center = player.rect.center
hazard_start = pygame.time.get_ticks()
hazard_is_black = False

# --- Главный игровой цикл ---
running = True
clock = pygame.time.Clock() # Объект для контроля частоты кадров

while running:
    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Закрываем игру при нажатии кнопки "закрыть"
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Выстрел только если игрок жив
            if not game_over and event.button == 1: # Левая кнопка мыши
                bullets.append(Bullet(player.barrel_end_pos, pygame.mouse.get_pos()))

    # --- Обновление состояния игры только если игра не окончена ---
    if not game_over:
        # Движение игрока по нажатию клавиш
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: # Влево
            player.move(-1, 0)
        if keys[pygame.K_d]: # Вправо
            player.move(1, 0)
        if keys[pygame.K_w]: # Вверх
            player.move(0, -1)
        if keys[pygame.K_s]: # Вниз
            player.move(0, 1)

        # Обновление поворота дула игрока
        player.update(pygame.mouse.get_pos())

        # Обновление снарядов
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_offscreen():
                bullets.remove(bullet)

        # Обновление кружков
        for circle in circles:
            circle.update()

        # Обновление защитного круга
        current_time = pygame.time.get_ticks()
        elapsed_hazard = current_time - hazard_start
        if elapsed_hazard >= HAZARD_RED_DURATION + HAZARD_BLACK_DURATION:
            hazard_start = current_time
            hazard_center = player.rect.center
            elapsed_hazard = 0

        hazard_is_black = elapsed_hazard >= HAZARD_RED_DURATION
        if hazard_is_black:
            distance_to_hazard = math.hypot(
                player.rect.centerx - hazard_center[0],
                player.rect.centery - hazard_center[1]
            )
            if distance_to_hazard <= HAZARD_RADIUS + PLAYER_SIZE / 2:
                game_over = True
                player.is_alive = False

        # Проверка столкновений снарядов с кружками
        for bullet in bullets[:]:
            for circle in circles[:]:
                distance = math.sqrt((bullet.pos[0] - circle.pos[0])**2 + (bullet.pos[1] - circle.pos[1])**2)
                if distance < bullet.radius + circle.radius:
                    bullets.remove(bullet)
                    circles.remove(circle)
                    score += 1

                    # Добавляем два новых кружка при сбитии одного, но не более MAX_CIRCLES
                    for _ in range(2):
                        if len(circles) >= MAX_CIRCLES:
                            break
                        new_circle = CircleTarget(player, circles)
                        if score >= 10:
                            new_circle.set_bouncing_direction()
                        circles.append(new_circle)
                    break # Выходим из внутреннего цикла, так как снаряд уже удален

        # Проверка столкновений игрока с кружками
        for circle in circles[:]: # Проверяем каждый кружок
            distance_player_circle = math.sqrt(
                (player.rect.centerx - circle.pos[0])**2 +
                (player.rect.centery - circle.pos[1])**2
            )
            if distance_player_circle < (PLAYER_SIZE / 2) + circle.radius:
                game_over = True # Устанавливаем флаг конца игры
                player.is_alive = False # Игрок "умирает"
                break # Выходим из цикла, игрок уже столкнулся

    # --- Отрисовка ---
    SCREEN.fill(WHITE) # Заполняем весь экран белым цветом

    # Рисуем защитный круг под игровыми объектами
    hazard_color = BLACK if hazard_is_black else RED
    pygame.draw.circle(SCREEN, hazard_color, hazard_center, HAZARD_RADIUS)

    # Отрисовываем игровые объекты поверх круга
    player.draw(SCREEN)
    for bullet in bullets:
        bullet.draw(SCREEN)
    for circle in circles:
        circle.draw(SCREEN)

    # Отображение таймера и счета
    if not game_over: # Таймер идет только пока игрок жив
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    timer_text = font.render(f"Время: {elapsed_time}", True, BLACK)
    score_text = font.render(f"Счет: {score}", True, BLACK)

    SCREEN.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 10))
    SCREEN.blit(score_text, (WIDTH - score_text.get_width() - 10, 50))

    # Сообщение "Игра окончена"
    if game_over:
        game_over_text = game_over_font.render("ИГРА ОКОНЧЕНА!", True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        SCREEN.blit(game_over_text, text_rect)

    # --- Обновление экрана ---
    pygame.display.flip()

    # --- Ограничение FPS ---
    clock.tick(60)

# Завершение работы Pygame
pygame.quit()
