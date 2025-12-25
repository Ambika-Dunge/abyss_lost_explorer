import pygame
import sys
import random
import os
from player import Player
from collectible import Collectible
from enemy import Enemy

# Initialize
pygame.init()
pygame.mixer.init()

# Get Fullscreen Dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_desktop_sizes()[0]
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Abyss: The Lost Explorer")

# Debug
print("📂 Current Working Directory:", os.getcwd())
if os.path.exists("assets"):
    print("📁 Assets Folder Files:", os.listdir("assets"))
else:
    print("🚫 Assets Folder Not Found")


try:
    pygame.mixer.music.load("assets/background music.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print("🚫 Error loading music:", e)

# Load Sound Effects
oxygen_pickup_sound = pygame.mixer.Sound("assets/oxygen_pickup.mp3")
death_sound = pygame.mixer.Sound("assets/death_sound.mp3")
win_sound = pygame.mixer.Sound("assets/win_sound.mp3")

# Constants
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)

# Load background
background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Clock and Font
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

# Player and Groups
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites = pygame.sprite.Group(player)

oxygen = 100
oxygen_decrease_rate = 0.05

def draw_oxygen_bar(surface, x, y, value, max_value):
    BAR_WIDTH = 200
    BAR_HEIGHT = 20
    fill = (value / max_value) * BAR_WIDTH
    pygame.draw.rect(surface, CYAN, (x, y, fill, BAR_HEIGHT))
    pygame.draw.rect(surface, WHITE, (x, y, BAR_WIDTH, BAR_HEIGHT), 2)

# Collectibles and Enemies
collectibles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 3000)

for _ in range(5):
    collectibles.add(Collectible("assets/oxygen_boost.png", SCREEN_WIDTH, SCREEN_HEIGHT))

for _ in range(3):
    enemies.add(Enemy("assets/enemy.png", SCREEN_WIDTH, SCREEN_HEIGHT))

# Game State
game_over = False
show_menu = False

# Button Class
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, self.hover_color if is_hover else self.color, self.rect, border_radius=10)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()

# Button Actions
def restart_game():
    global oxygen, game_over, show_menu, all_sprites
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    oxygen = 100
    all_sprites = pygame.sprite.Group(player)
    collectibles.empty()
    enemies.empty()
    for _ in range(5):
        collectibles.add(Collectible("assets/oxygen_boost.png", SCREEN_WIDTH, SCREEN_HEIGHT))
    for _ in range(3):
        enemies.add(Enemy("assets/enemy.png", SCREEN_WIDTH, SCREEN_HEIGHT))
    game_over = False
    show_menu = False

def resume_game():
    global game_over, show_menu
    game_over = False
    show_menu = False

def stop_game():
    pygame.quit()
    sys.exit()

# Buttons
buttons = [
    Button("Restart", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30, 200, 50, CYAN, (0, 200, 200), restart_game),
    Button("Resume", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 50, CYAN, (0, 200, 200), resume_game),
    Button("Stop",   SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 50, CYAN, (0, 200, 200), stop_game),
]

def draw_game_over_message():
    msg = font.render("You are dead! Press Enter for menu.", True, WHITE)
    screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

def draw_menu():
    pygame.draw.rect(screen, (30, 30, 30), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 250), border_radius=12)
    pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 250), 3, border_radius=12)
    title = font.render("Game Menu", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
    for button in buttons:
        button.draw(screen)

# Game Loop
running = True
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if show_menu:
            for button in buttons:
                button.check_click(event)

        if event.type == SPAWN_EVENT and not game_over and not show_menu:
            collectibles.add(Collectible("assets/oxygen_boost.png", SCREEN_WIDTH, SCREEN_HEIGHT))

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_RETURN:
                show_menu = True

    keys = pygame.key.get_pressed()
    if not game_over and not show_menu:
        player.update(keys)
        enemies.update()
        oxygen -= oxygen_decrease_rate
        if oxygen <= 0:
            death_sound.play()
            game_over = True

        collected = pygame.sprite.spritecollide(player, collectibles, True)
        for c in collected:
            oxygen = min(oxygen + 20, 100)
            oxygen_pickup_sound.play()

        if pygame.sprite.spritecollide(player, enemies, False):
            death_sound.play()
            game_over = True

    if not show_menu:
        all_sprites.draw(screen)
        collectibles.draw(screen)
        enemies.draw(screen)
        draw_oxygen_bar(screen, 10, 10, oxygen, 100)

    if game_over:
        draw_game_over_message()

    if show_menu:
        draw_menu()

    pygame.display.flip()

pygame.quit()
sys.exit()
