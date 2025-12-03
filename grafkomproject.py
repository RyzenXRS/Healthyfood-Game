import pygame
import random
import os

pygame.init()

# Setting layar
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pilah Makanan Sehat & Junk Food")

# Warna & Font
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BG_COLOR = (180, 230, 255)

font_big = pygame.font.SysFont("Arial", 60, bold=True)
font_medium = pygame.font.SysFont("Arial", 40)
font_small = pygame.font.SysFont("Arial", 30)

# Load gambar
def load_image(name, size=None):
    path = os.path.join(name)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

paperbag = load_image("15.png", (250, 350))
foods_img = {}
for i in range(1, 15):
    foods_img[i] = load_image(f"{i}.png", (100, 100))

# Hati (jika tidak ada gambar, buat manual)
try:
    heart_full = load_image("heart_full.png", (50, 50))
    heart_empty = load_image("heart_empty.png", (50, 50))
except:
    heart_full = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(heart_full, RED, (18,20), 15)
    pygame.draw.circle(heart_full, RED, (32,20), 15)
    pygame.draw.polygon(heart_full, RED, [(10,25), (25,45), (40,25)])
    
    heart_empty = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(heart_empty, (100,100,100), (18,20), 15, 4)
    pygame.draw.circle(heart_empty, (100,100,100), (32,20), 15, 4)
    pygame.draw.polygon(heart_empty, (100,100,100), [(10,25), (25,45), (40,25)], 4)

# Kelas Makanan
class Food:
    def __init__(self, id, x, y):
        self.id = id
        self.image = foods_img[id]
        self.rect = self.image.get_rect(center=(x, y))
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def start_drag(self, pos):
        self.dragging = True
        self.offset_x = self.rect.centerx - pos[0]
        self.offset_y = self.rect.centery - pos[1]

    def update_drag(self, pos):
        self.rect.center = (pos[0] + self.offset_x, pos[1] + self.offset_y)

    def stop_drag(self):
        self.dragging = False

# Kelas efek skor
class ScoreEffect:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 60  # 1 detik

    def update(self):
        self.y -= 2
        self.life -= 1

    def draw(self, surface):
        txt = font_medium.render(self.text, True, self.color)
        surface.blit(txt, (self.x - txt.get_width()//2, self.y))

# Variabel game
clock = pygame.time.Clock()
score = 0
lives = 3
level = 1
foods = []
dragged_food = None
game_over = False
score_effects = []

# Area paperbag
junk_bag_rect = pygame.Rect(100, 200, 250, 350)
healthy_bag_rect = pygame.Rect(WIDTH-350, 200, 250, 350)

def spawn_level():
    global foods
    foods = []
    total = 8 + level * 2  # makin tinggi level, makin banyak
    for _ in range(total):
        if random.randint(0, 1):
            fid = random.randint(1, 8)   # sehat
        else:
            fid = random.randint(9, 14)  # junk
        x = random.randint(200, WIDTH-200)
        y = random.randint(100, HEIGHT-200)
        foods.append(Food(fid, x, y))

def draw_ui():
    screen.fill(BG_COLOR)
    
    # Paperbag
    screen.blit(paperbag, (100, 200))
    screen.blit(paperbag, (WIDTH-350, 200))
    
    # Label
    junk_label = font_medium.render("JUNK FOOD", True, BLACK)
    healthy_label = font_medium.render("HEALTHY FOOD", True, BLACK)
    screen.blit(junk_label, (225 - junk_label.get_width()//2, 150))
    screen.blit(healthy_label, (WIDTH-225 - healthy_label.get_width()//2, 150))
    
    # Score & Level
    score_text = font_small.render(f"Score: {score}", True, BLACK)
    level_text = font_small.render(f"Level: {level}", True, BLACK)
    screen.blit(score_text, (20, 20))
    screen.blit(level_text, (20, 70))
    
    # Hati
    for i in range(3):
        img = heart_full if i < lives else heart_empty
        screen.blit(img, (WIDTH - 200 + i*60, 20))

# Mulai level pertama
spawn_level()

# Main Loop
running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                continue
            pos = pygame.mouse.get_pos()
            for food in reversed(foods):
                if food.rect.collidepoint(pos):
                    food.start_drag(pos)
                    dragged_food = food
                    foods.remove(food)
                    foods.append(food)  # pindah ke atas
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragged_food and not game_over:
                pos = pygame.mouse.get_pos()
                dropped = False
                center = dragged_food.rect.center

                # Cek masuk paperbag
                if junk_bag_rect.collidepoint(center):
                    if dragged_food.id >= 9:
                        score += 10
                        score_effects.append(ScoreEffect(center[0], center[1], "+10", GREEN))
                    else:
                        lives -= 1
                        score_effects.append(ScoreEffect(center[0], center[1], "-1 NYAWA", RED))
                    dropped = True

                elif healthy_bag_rect.collidepoint(center):
                    if dragged_food.id <= 8:
                        score += 10
                        score_effects.append(ScoreEffect(center[0], center[1], "+10", GREEN))
                    else:
                        lives -= 1
                        score_effects.append(ScoreEffect(center[0], center[1], "-1 NYAWA", RED))
                    dropped = True

                # Jika masuk paperbag → hilang selamanya
                if dropped:
                    foods.remove(dragged_food)
                else:
                    dragged_food.stop_drag()

                dragged_food = None

                # Cek kalah
                if lives <= 0:
                    game_over = True

                # Cek semua makanan sudah masuk paperbag → next level
                if len(foods) == 0:
                    level += 1
                    spawn_level()

        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                score = 0
                lives = 3
                level = 1
                game_over = False
                spawn_level()

    # Update drag
    if dragged_food and dragged_food.dragging:
        dragged_food.update_drag(pygame.mouse.get_pos())

    # Update efek skor
    for effect in score_effects[:]:
        effect.update()
        if effect.life <= 0:
            score_effects.remove(effect)

    # Gambar
    draw_ui()

    # Gambar makanan
    for food in foods:
        food.draw(screen)

    # Gambar efek skor
    for effect in score_effects:
        effect.draw(screen)

    # Game Over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        go_text = font_big.render("GAME OVER", True, RED)
        restart_text = font_medium.render("Tekan R untuk Mulai Lagi", True, WHITE)
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 80))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

pygame.quit()