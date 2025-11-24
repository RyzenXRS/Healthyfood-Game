import pygame
import random
import cairo    
import io

# --- Inisialisasi Pygame ---
pygame.init()

# --- Konfigurasi Layar ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HEALTHY FOOD: Game Edukasi Drag-and-Drop")

# --- Warna & Font ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRASS_GREEN = (102, 153, 0)
HEALTHY_GREEN = (0, 179, 60)
JUNK_RED = (204, 0, 0)
TEXT_COLOR = (25, 25, 25)

FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 36)

# --- Variabel Game ---
SCORE = 0
LIVES = 3
GAME_OVER = False
DRAGGING_OFFSET = (0, 0) # Digunakan untuk offset mouse saat drag

# Daftar Makanan dan Path Gambarnya
ALL_FOOD_TYPES = [
    # Tipe, Nama, Path Gambar (pastikan file gambar ini ada!)
    ('HEALTHY', 'Apel', 'assest/healthy/apel.png'), 
    ('HEALTHY', 'Pisang', 'assest/healthy/pisang.png'),
    ('HEALTHY', 'Wortel', 'assest/healthy/wortel.png'),
    ('JUNK', 'Burger', 'assest/junk/burger.png'), 
    ('JUNK', 'Soda', 'assest/junk/soda.png'),
    # PERHATIKAN: Nama file Anda di screenshot adalah 'kentang.png'
    ('JUNK', 'Fries', 'assest/junk/kentang.png'),
]

# --- Pycairo Utility: Membuat Teks untuk Wadah (Kualitas Tinggi) ---
def create_cairo_text(text, font_size, color):
    # Membuat Surface Pygame dari Teks Pycairo
    temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
    temp_ctx = cairo.Context(temp_surface)
    temp_ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    temp_ctx.set_font_size(font_size)
    x_bearing, y_bearing, width, height, x_advance, y_advance = temp_ctx.text_extents(text)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width) + 10, int(height) + 10)
    ctx = cairo.Context(surface)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)
    ctx.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
    ctx.move_to(5, height)
    ctx.show_text(text)
    
    buf = io.BytesIO()
    surface.write_to_png(buf)
    buf.seek(0)
    
    pygame_surface = pygame.image.load(buf, "png")
    return pygame_surface

# --- Kelas Sprite ---

class Wadah(pygame.sprite.Sprite):
    # Tambahkan parameter image_path_wadah
    def __init__(self, x, y, tipe_makanan, image_path_wadah): 
        super().__init__()
        self.tipe = tipe_makanan 
        
        # --- Bagian Kunci: Memuat dan Menskala Gambar Wadah ---
        try:
            original_image = pygame.image.load(image_path_wadah).convert_alpha()
            # Skala gambar wadah. Sesuaikan ukuran (200, 250) sesuai aset Anda.
            self.image = pygame.transform.scale(original_image, (200, 250)) 
        except pygame.error:
            print(f"Gambar wadah tidak ditemukan: {image_path_wadah}. Menggunakan placeholder warna.")
            self.image = pygame.Surface([200, 250])
            self.image.fill(JUNK_RED if tipe_makanan == 'JUNK' else HEALTHY_GREEN)
        # ----------------------------------------------------
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Teks Wadah (menggunakan Pycairo, akan digambar di atas gambar wadah)
        text_content = "Makanan Sehat" if tipe_makanan == 'HEALTHY' else "Junk Food"
        text_surface = create_cairo_text(text_content, 30, WHITE)
        
        # Posisikan teks di tengah atas wadah (relatif terhadap gambar wadah)
        text_x = (self.rect.width - text_surface.get_width()) // 2
        text_y = 20
        self.image.blit(text_surface, (text_x, text_y))

class Makanan(pygame.sprite.Sprite):
    def __init__(self, x, y, tipe_makanan, name, image_path):
        super().__init__()
        self.tipe = tipe_makanan
        self.name = name
        self.start_pos = (x, y)
        
        # --- Memuat dan Menskala Gambar ---
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(original_image, (80, 80)) 
        except pygame.error:
            # Placeholder jika gambar tidak ditemukan
            print(f"Gambar tidak ditemukan: {image_path}. Menggunakan placeholder.")
            self.image = pygame.Surface([80, 80])
            self.image.fill(JUNK_RED if tipe_makanan == 'JUNK' else HEALTHY_GREEN)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_dragging = False 

    def update(self):
        # Update posisi hanya jika sedang di-drag
        if self.is_dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.x = mouse_x + DRAGGING_OFFSET[0]
            self.rect.y = mouse_y + DRAGGING_OFFSET[1]
        
    def reset_position(self):
        # Mengembalikan makanan ke posisi awal
        self.rect.x = self.start_pos[0]
        self.rect.y = self.start_pos[1]
        self.is_dragging = False

class HUD(pygame.sprite.Sprite):
    """Menangani tampilan Score dan Lives."""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([SCREEN_WIDTH, 50], pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)
        self.update()

    def update(self):
        self.image.fill((0, 0, 0, 0)) # Bersihkan
        
        # Tampilkan Skor
        score_text = FONT_MEDIUM.render(f"Score : {SCORE}", True, TEXT_COLOR)
        self.image.blit(score_text, (20, 10))
        
        # Tampilkan Nyawa
        heart_icon = FONT_MEDIUM.render("❤", True, JUNK_RED) 
        live_x_start = SCREEN_WIDTH - 150
        for i in range(LIVES):
            self.image.blit(heart_icon, (live_x_start + (i * 30), 10))
        
# --- Setup Game ---

# Inisialisasi Group Sprite

# Inisialisasi Group Sprite (tetap sama)
all_sprites = pygame.sprite.Group()
foods = pygame.sprite.Group()
wadahs = pygame.sprite.Group()

# Membuat Wadah
# Ganti parameter 'color' menjadi 'image_path_wadah'
wadah_junk = Wadah(SCREEN_WIDTH * 0.15, 50, 'JUNK', 'assest/wadah_junk.png') 
wadah_healthy = Wadah(SCREEN_WIDTH * 0.65, 50, 'HEALTHY', 'assest/wadah_healthy.png')

all_sprites.add(wadah_junk, wadah_healthy)
wadahs.add(wadah_junk, wadah_healthy)

# ... (sisa Setup Game, tetap sama)
# Setup HUD
hud = HUD()
all_sprites.add(hud)

drag_target = None

# --- Fungsi Bantuan ---

def initialize_foods():
    """Menginisialisasi makanan di posisi acak di bagian bawah layar."""
    global foods, all_sprites
    
    # Hapus semua makanan yang sudah ada
    for food in foods:
        food.kill()
    
    # Posisi awal makanan diatur di bagian bawah
    food_positions = [
        (100, SCREEN_HEIGHT - 150), (250, SCREEN_HEIGHT - 300), 
        (450, SCREEN_HEIGHT - 200), (600, SCREEN_HEIGHT - 100), 
        (750, SCREEN_HEIGHT - 250)
    ]
    
    selected_foods = random.sample(ALL_FOOD_TYPES, min(len(ALL_FOOD_TYPES), len(food_positions)))
    
    for i, (tipe, name, path) in enumerate(selected_foods):
        x, y = food_positions[i]
        food = Makanan(x, y, tipe, name, path) 
        foods.add(food)
        all_sprites.add(food)

def check_drop(food, wadah_group):
    """Cek apakah makanan dijatuhkan di wadah yang benar."""
    global SCORE, LIVES
    
    hit_wadahs = pygame.sprite.spritecollide(food, wadah_group, False)
    
    if hit_wadahs:
        target_wadah = hit_wadahs[0] 
        
        if food.tipe == target_wadah.tipe:
            # Jawaban Benar
            SCORE += 10
            food.kill() # Hapus makanan
            return True
        else:
            # Jawaban Salah
            LIVES -= 1
            food.kill() # Hapus makanan
            return True
            
    # Jika dijatuhkan di luar wadah, kembalikan ke game loop untuk dikembalikan/dihapus
    return False

# Panggil fungsi inisialisasi awal
initialize_foods()

# --- Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 1. Penanganan Mouse Down (Mulai Drag)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not drag_target:
                for food in foods:
                    if food.rect.collidepoint(event.pos):
                        drag_target = food
                        drag_target.is_dragging = True
                        
                        # Tidak perlu deklarasi global di sini karena kita berada
                        # pada tingkat modul; langsung set offset untuk drag yang mulus
                        mouse_x, mouse_y = event.pos
                        DRAGGING_OFFSET = (food.rect.x - mouse_x, food.rect.y - mouse_y)
                        break
        
        # 2. Penanganan Mouse Up (Akhiri Drag)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drag_target:
                drag_target.is_dragging = False
                
                # Cek Penempatan
                correctly_placed = check_drop(drag_target, wadahs)
                
                if not correctly_placed:
                    # Dijatuhkan di luar wadah
                    # Kembalikan ke posisi awal (simulasi saja, atau buat item hilang dan kurangi nyawa)
                    drag_target.reset_position() 
                
                drag_target = None
                
    if not GAME_OVER:
        # --- Logika Game ---
        
        # 1. Update semua sprite (hanya yang sedang di-drag yang bergerak)
        all_sprites.update()
        
        # 2. Cek Level Selesai
        if not foods:
            # Inisialisasi ulang makanan untuk level baru
            initialize_foods()
            
        # 3. Cek Game Over
        if LIVES <= 0:
            GAME_OVER = True
            
        # 4. Update HUD
        hud.update()
            
        # --- Rendering (Menggambar) ---
        screen.fill(GRASS_GREEN)
        
        # Gambar semua sprite
        all_sprites.draw(screen)

    else:
        # --- Tampilan Game Over ---
        screen.fill(BLACK)
        game_over_text = FONT_LARGE.render("GAME OVER", True, JUNK_RED)
        score_final_text = FONT_MEDIUM.render(f"Skor Akhir: {SCORE}", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(score_final_text, (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2))

    # Perbarui seluruh layar
    pygame.display.flip() 
    
    # Batasi FPS
    clock.tick(60)

pygame.quit()