import pygame
import random
import os

pygame.init()

# --- KONFIG LAYAR ---
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Healthy vs Unhealthy Food - EduGame")

# --- WARNA & FONT ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
ORANGE = (243, 156, 18)
BG_COLOR = (240, 248, 255)

font_title = pygame.font.SysFont("Arial", 70, bold=True)
font_big = pygame.font.SysFont("Arial", 50, bold=True)
font_medium = pygame.font.SysFont("Arial", 35)
font_small = pygame.font.SysFont("Arial", 25)
font_tiny = pygame.font.SysFont("Arial", 18) # Font untuk fakta

# --- DATA FAKTA MAKANAN ---
# ID 1-8: Healthy, 9-14: Unhealthy
food_facts = {
    1: "Kaya Zat Besi!",      # Bayam
    2: "Sumber Energi!",      # Jagung
    3: "Melancarkan Pencernaan!", # Kol
    4: "Kalsium untuk Tulang!", # Susu
    5: "Banyak Vitamin C!",   # Stroberi
    6: "Protein Tinggi!",     # Daging
    7: "Kaya Kalium!",        # Pisang
    8: "Baik untuk Otak!",    # Udang
    9: "Banyak Lemak Jenuh!", # Burger
    10: "Tinggi Kalori!",     # Pizza
    11: "Daging Olahan!",     # Hotdog
    12: "Terlalu Banyak Gula!", # Soda
    13: "Hanya Karbohidrat!", # Donat
    14: "Digoreng Minyak Banyak!" # Kentang
}

# --- SISTEM HIGH SCORE ---
def get_high_score(mode):
    filename = f"highscore_{mode.lower()}.txt"
    if not os.path.exists(filename): return 0
    try:
        with open(filename, "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(mode, new_score):
    current = get_high_score(mode)
    if new_score > current:
        filename = f"highscore_{mode.lower()}.txt"
        with open(filename, "w") as f:
            f.write(str(new_score))
        return new_score 
    return current

# --- Assets Things ---
def load_image(name, size=None, silent=False):
    path = os.path.join("assets", name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except FileNotFoundError:
        if not silent:
            print(f"Warning: Gambar {name} tidak ditemukan.")
        return None

bg_start_img = load_image("bg_start.png", (WIDTH, HEIGHT))
bg_menu_img = load_image("bg_menu.png", (WIDTH, HEIGHT))
paperbag_img = load_image("15.png", (220, 300))
paperbag = paperbag_img if paperbag_img else pygame.Surface((220, 300))
if not paperbag_img: paperbag.fill((139, 69, 19))

foods_img = {}
for i in range(1, 15):
    img = load_image(f"{i}.png", (100, 100))
    if img is None:
        surf = pygame.Surface((100, 100))
        surf.fill(RED if i > 8 else GREEN)
        txt = font_small.render(str(i), True, WHITE)
        surf.blit(txt, (40, 30))
        foods_img[i] = surf
    else:
        foods_img[i] = img

heart_full_img = load_image("heart_full.png", (40, 40), silent=True)
heart_empty_img = load_image("heart_empty.png", (40, 40), silent=True)

if heart_full_img is None:
    heart_full_img = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(heart_full_img, RED, (12, 12), 12)
    pygame.draw.circle(heart_full_img, RED, (28, 12), 12)
    pygame.draw.polygon(heart_full_img, RED, [(0, 15), (20, 38), (40, 15)])

if heart_empty_img is None:
    heart_empty_img = pygame.Surface((40, 40), pygame.SRCALPHA)
    GRAY = (200, 200, 200)
    pygame.draw.circle(heart_empty_img, GRAY, (12, 12), 12)
    pygame.draw.circle(heart_empty_img, GRAY, (28, 12), 12)
    pygame.draw.polygon(heart_empty_img, GRAY, [(0, 15), (20, 38), (40, 15)])

# --- CLASS OBJEK ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
        self.life = 255 

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 5 
        self.size -= 0.1 

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

class FloatingText:
    def __init__(self, text, x, y, color=BLACK):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 60 
        self.y_offset = 0

    def update(self):
        self.life -= 1
        self.y_offset -= 1 

    def draw(self, surface):
        if self.life > 0:
            txt_surf = font_small.render(self.text, True, self.color)
            txt_bg = font_small.render(self.text, True, WHITE)
            
            draw_pos = (self.x - txt_surf.get_width()//2, self.y + self.y_offset)
            
            surface.blit(txt_bg, (draw_pos[0]-1, draw_pos[1]))
            surface.blit(txt_bg, (draw_pos[0]+1, draw_pos[1]))
            surface.blit(txt_bg, (draw_pos[0], draw_pos[1]-1))
            surface.blit(txt_bg, (draw_pos[0], draw_pos[1]+1))
            surface.blit(txt_surf, draw_pos)

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

    def update_drag(self, pos):
        self.rect.center = (pos[0] + self.offset_x, pos[1] + self.offset_y)

class Button:
    def __init__(self, text, x, y, w, h, color, action_code, style="visible"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action_code = action_code
        self.style = style 
        self.hovered = False

    def draw(self, surface):
        if self.style == "invisible":
            pass
        else:
            current_col = (min(self.color[0]+30, 255), min(self.color[1]+30, 255), min(self.color[2]+30, 255)) if self.hovered else self.color
            shadow_rect = pygame.Rect(self.rect.x, self.rect.y + 5, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), shadow_rect, border_radius=15)
            pygame.draw.rect(surface, current_col, self.rect, border_radius=15)
            pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=15)
            
            if self.text:
                txt_surf = font_medium.render(self.text, True, WHITE)
                surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.centery - txt_surf.get_height()//2))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# --- Variabel Global---
current_state = "START"
game_mode = None 
score = 0
current_high_score = 0 
lives = 3
level = 1
time_left = 30
foods = []          
dragged_food = None 
quiz_food = None    
quiz_answered = False
feedback_text = ""
feedback_timer = 0
is_high_score_beaten = False

# List untuk efek
particles = []
floating_texts = []

# --- Logika Game ---
def create_particles(x, y, color):
    for _ in range(15): # Buat 15 partikel
        particles.append(Particle(x, y, color))

def show_fact(food_id, x, y):
    fact = food_facts.get(food_id, "Makanan!")
    col = GREEN if food_id <= 8 else RED
    floating_texts.append(FloatingText(fact, x, y, col))

def reset_game(mode):
    global score, lives, level, foods, dragged_food, quiz_food, game_mode, feedback_text, time_left, is_high_score_beaten, current_high_score, particles, floating_texts
    score = 0
    lives = 3
    level = 1
    time_left = 30 
    foods = []
    dragged_food = None
    feedback_text = ""
    is_high_score_beaten = False
    game_mode = mode
    particles = []
    floating_texts = []
    
    current_high_score = get_high_score(mode)
    
    if mode == "DRAG":
        spawn_drag_level()
    elif mode == "QUIZ":
        spawn_quiz_question()

def spawn_drag_level():
    global foods
    foods = []
    total = 6 + level * 2
    for _ in range(total):
        fid = random.randint(1, 14) 
        x = random.randint(100, WIDTH-100)
        y = random.randint(100, HEIGHT-100)
        foods.append(Food(fid, x, y))

def spawn_quiz_question():
    global quiz_food, quiz_answered
    fid = random.randint(1, 14)
    quiz_food = Food(fid, WIDTH//2, HEIGHT//2 - 50)
    quiz_food.image = pygame.transform.scale(foods_img[fid], (200, 200))
    quiz_food.rect = quiz_food.image.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    quiz_answered = False

def draw_hearts(surface):
    for i in range(3):
        x = WIDTH - 150 + i * 45
        y = 20
        if i < lives:
            surface.blit(heart_full_img, (x, y))
        else:
            surface.blit(heart_empty_img, (x, y))

def draw_timer(surface):
    color = BLACK
    if time_left < 10: color = RED 
    timer_text = font_medium.render(f"Waktu: {int(time_left)}s", True, color)
    surface.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, 20))

# --- SETUP TOMBOL ---
btn_start_invisible = Button("", 360, 450, 280, 100, BLACK, "GOTO_MENU", style="invisible")
btn_menu_pilah = Button("", 150, 180, 250, 250, GREEN, "START_DRAG", style="invisible")
btn_menu_tebak = Button("", 600, 180, 250, 250, ORANGE, "START_QUIZ", style="invisible")
btn_back = Button("KEMBALI", 20, 20, 160, 50, ORANGE, "BACK_HOME")
btn_quiz_healthy = Button("HEALTHY", WIDTH//2 - 220, 450, 200, 80, GREEN, "ANS_HEALTHY")
btn_quiz_unhealthy = Button("UNHEALTHY", WIDTH//2 + 20, 450, 200, 80, RED, "ANS_UNHEALTHY")


# --- MAIN LOOP ---
clock = pygame.time.Clock()
running = True

while running:
    dt_ms = clock.tick(60) 
    dt_seconds = dt_ms / 1000.0 
    
    pos = pygame.mouse.get_pos()

    # --- UPDATE EFFECTS ---
    for p in particles[:]:
        p.update()
        if p.life <= 0 or p.size <= 0: particles.remove(p)
        
    for ft in floating_texts[:]:
        ft.update()
        if ft.life <= 0: floating_texts.remove(ft)

    # --- UPDATE TIMER & HIGHSCORE ---
    if current_state in ["GAME_DRAG", "GAME_QUIZ"]:
        time_left -= dt_seconds
        if score > current_high_score:
            current_high_score = score
            is_high_score_beaten = True

        if time_left <= 0:
            time_left = 0
            lives = 0 
            current_state = "GAME_OVER"
            save_high_score(game_mode, score)

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                if current_state != "START" and btn_back.is_clicked(pos):
                    if score > 0: save_high_score(game_mode, score)
                    current_state = "START"

                # 1. STATE START
                if current_state == "START":
                    if btn_start_invisible.is_clicked(pos):
                        current_state = "MENU"

                # 2. STATE MENU
                elif current_state == "MENU":
                    if btn_menu_pilah.is_clicked(pos):
                        current_state = "GAME_DRAG"
                        reset_game("DRAG")
                    elif btn_menu_tebak.is_clicked(pos):
                        current_state = "GAME_QUIZ"
                        reset_game("QUIZ")

                # 3. STATE GAME QUIZ
                elif current_state == "GAME_QUIZ" and not feedback_text:
                    correct = False
                    answered = False
                    
                    if btn_quiz_healthy.is_clicked(pos):
                        answered = True
                        if quiz_food.id <= 8: correct = True 
                    elif btn_quiz_unhealthy.is_clicked(pos):
                        answered = True
                        if quiz_food.id >= 9: correct = True 

                    if answered:
                        if correct:
                            score += 10
                            time_left += 3
                            feedback_text = "BENAR! +3 Detik"
                            create_particles(pos[0], pos[1], GREEN)
                            show_fact(quiz_food.id, WIDTH//2, HEIGHT//2 + 20)
                        else:
                            lives -= 1
                            time_left -= 5 
                            if time_left < 0: time_left = 0
                            feedback_text = "SALAH! -5 Detik"
                        
                        feedback_timer = 60 
                        if lives <= 0: 
                            current_state = "GAME_OVER"
                            save_high_score(game_mode, score)

                # 4. STATE GAME OVER
                elif current_state == "GAME_OVER":
                    current_state = "MENU"

                # 5. STATE GAME DRAG
                elif current_state == "GAME_DRAG":
                    for food in reversed(foods):
                        if food.rect.collidepoint(pos):
                            food.dragging = True
                            food.offset_x = food.rect.centerx - pos[0]
                            food.offset_y = food.rect.centery - pos[1]
                            dragged_food = food
                            foods.remove(food)
                            foods.append(food) 
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            if current_state == "GAME_DRAG" and dragged_food:
                center = dragged_food.rect.center
                dropped = False
                unhealthy_rect = pygame.Rect(100, 200, 220, 300)
                healthy_rect = pygame.Rect(WIDTH-320, 200, 220, 300)

                is_correct = False
                if unhealthy_rect.collidepoint(center):
                    dropped = True
                    if dragged_food.id >= 9: is_correct = True
                elif healthy_rect.collidepoint(center):
                    dropped = True
                    if dragged_food.id <= 8: is_correct = True
                
                if dropped:
                    if is_correct:
                        score += 10
                        time_left += 3 
                        # EFEK VISUAL: Partikel Hijau & Fakta
                        create_particles(center[0], center[1], GREEN)
                        show_fact(dragged_food.id, center[0], center[1])
                    else:
                        lives -= 1
                        time_left -= 5 
                        if time_left < 0: time_left = 0
                        # EFEK VISUAL: Partikel Merah (Salah)
                        create_particles(center[0], center[1], RED)

                    foods.remove(dragged_food)
                    if len(foods) == 0:
                        level += 1
                        spawn_drag_level()
                    
                    if lives <= 0: 
                        current_state = "GAME_OVER"
                        save_high_score(game_mode, score)
                else:
                    dragged_food.dragging = False 
                dragged_food = None

    # --- UPDATE LOGIC ---
    if current_state == "GAME_DRAG" and dragged_food:
        dragged_food.update_drag(pos)

    if current_state == "GAME_QUIZ" and feedback_text:
        feedback_timer -= 1
        if feedback_timer <= 0:
            feedback_text = ""
            spawn_quiz_question()

    # Hover Check
    if current_state == "START": btn_start_invisible.check_hover(pos)
    elif current_state == "MENU": 
        btn_menu_pilah.check_hover(pos)
        btn_menu_tebak.check_hover(pos)
    elif current_state == "GAME_QUIZ":
        btn_quiz_healthy.check_hover(pos)
        btn_quiz_unhealthy.check_hover(pos)
    btn_back.check_hover(pos)
    screen.fill(BG_COLOR)

    # 1. Halaman Start
    if current_state == "START":
        if bg_start_img: screen.blit(bg_start_img, (0, 0))
        else: screen.fill(BG_COLOR)
        btn_start_invisible.draw(screen)

    # 2. Hal Menu
    elif current_state == "MENU":
        if bg_menu_img: screen.blit(bg_menu_img, (0, 0))
        else: screen.fill(BG_COLOR)
        
        hs_drag = get_high_score("DRAG")
        hs_quiz = get_high_score("QUIZ")
        
        score_info = font_small.render(f"High Scores -> Pilah: {hs_drag} | Tebak: {hs_quiz}", True, BLACK)
        bg_info = pygame.Surface((score_info.get_width()+20, score_info.get_height()+10))
        bg_info.set_alpha(180)
        bg_info.fill(WHITE)
        screen.blit(bg_info, (WIDTH//2 - bg_info.get_width()//2, 10))
        screen.blit(score_info, (WIDTH//2 - score_info.get_width()//2, 15))

        btn_menu_pilah.draw(screen)
        btn_menu_tebak.draw(screen)
        btn_back.draw(screen)

    # 3. Game Pilah (Drag)
    elif current_state == "GAME_DRAG":
        screen.blit(paperbag, (100, 200))
        screen.blit(paperbag, (WIDTH-320, 200))
        lbl_unhealthy = font_medium.render("UNHEALTHY", True, BLACK)
        lbl_healthy = font_medium.render("HEALTHY", True, BLACK)
        screen.blit(lbl_unhealthy, (210 - lbl_unhealthy.get_width()//2, 150))
        screen.blit(lbl_healthy, (WIDTH-210 - lbl_healthy.get_width()//2, 150))

        for food in foods:
            food.draw(screen)
        
        info_score = font_small.render(f"Score: {score} | Level: {level}", True, BLACK)
        screen.blit(info_score, (200, 20))
        info_best = font_small.render(f"Best: {current_high_score}", True, GREEN) 
        screen.blit(info_best, (200, 50))
        
        draw_hearts(screen)
        draw_timer(screen)
        btn_back.draw(screen)

    # 4. Game Quiz (Tebak)  
    elif current_state == "GAME_QUIZ":
        title = font_medium.render("Termasuk jenis apakah makanan ini?", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        if quiz_food: quiz_food.draw(screen)
        btn_quiz_healthy.draw(screen)
        btn_quiz_unhealthy.draw(screen)
        
        if feedback_text:
            col = GREEN if "BENAR" in feedback_text else RED
            fb_surf = font_big.render(feedback_text, True, col)
            screen.blit(fb_surf, (WIDTH//2 - fb_surf.get_width()//2, HEIGHT//2 + 80))

        info_score = font_small.render(f"Score: {score}", True, BLACK)
        screen.blit(info_score, (200, 20))
        info_best = font_small.render(f"Best: {current_high_score}", True, GREEN)
        screen.blit(info_best, (200, 50))

        draw_hearts(screen)
        draw_timer(screen)
        btn_back.draw(screen)

    # 5. Jika Game Over
    elif current_state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        if is_high_score_beaten:
            txt_go = font_title.render("NEW HIGH SCORE!", True, ORANGE)
        else:
            txt_go = font_title.render("GAME OVER", True, RED)
            
        txt_score = font_medium.render(f"Final Score: {score}", True, WHITE)
        final_best = get_high_score(game_mode)
        txt_best = font_small.render(f"Best Record: {final_best}", True, GREEN)
        
        txt_hint = font_small.render("Klik di mana saja untuk kembali", True, WHITE)
        
        screen.blit(txt_go, (WIDTH//2 - txt_go.get_width()//2, HEIGHT//2 - 80))
        screen.blit(txt_score, (WIDTH//2 - txt_score.get_width()//2, HEIGHT//2))
        screen.blit(txt_best, (WIDTH//2 - txt_best.get_width()//2, HEIGHT//2 + 50))
        screen.blit(txt_hint, (WIDTH//2 - txt_hint.get_width()//2, HEIGHT//2 + 100))

    for p in particles:
        p.draw(screen)
    for ft in floating_texts:
        ft.draw(screen)

    pygame.display.flip()

pygame.quit()