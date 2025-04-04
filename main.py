import pygame, random, sys
from PIL import Image, ImageFilter

pygame.init()
pygame.font.init()
pygame.display.set_mode((1280, 720))
screen = pygame.display.get_surface()
clock = pygame.time.Clock()

def quit():
    pygame.quit()
    sys.exit()

class Button: 
    def __init__(self, y, text: str, on_click=None):
        self.y = y
        self.text = text.upper()
        self.rect_width = 1
        self.on_click = on_click

    def hovering(self):
        if True:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (mouse_x >= 50 and mouse_x <= 250) and (mouse_y >= self.y and mouse_y <= self.y + 50):
                return True
        return False

    def draw(self, screen):
        if self.hovering():
            self.rect_width += 0.125 * (300 - self.rect_width)
            mouse_down = pygame.mouse.get_pressed()
            if mouse_down[0]: self.on_click() if self.on_click else None
        else:
            self.rect_width += 0.125 * (1 - self.rect_width)

        pygame.draw.rect(screen, (255, 20, 240), (50, self.y, self.rect_width, 50), 0)
        font = pygame.font.SysFont("SF Pro Display", 25)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(50 + 100, self.y + 25))
        screen.blit(text_surface, text_rect)

class Tilemap:
    def __init__(self, tiles=[]):
        self.tiles = tiles

    @staticmethod
    def new(w, h):
        return Tilemap(["0" * w for _ in range(h)])
    
    def clear(self):
        self.tiles = ["0" * len(self.tiles[0]) for _ in range(len(self.tiles))]
    
    def set_tile(self, x, y, tile):
        if y < 0 or y >= len(self.tiles) or x < 0 or x >= len(self.tiles[y]):
            return False
        
        row = self.tiles[y]

        for i in range(len(row)):
            if i == x:
                row = row[:i] + str(tile) + row[i+1:]
                break

        self.tiles[y] = row
        return True

    def draw(self, screen):
        tile_size = 20
        color_map = {
            "0": (63, 63, 63),  # empty tile (dark gray)
            "1": (0, 255, 0),   # type 1 (snake)
            "2": (255, 0, 0)    # type 2 (food)
        }

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                color = color_map.get(self.tiles[y][x], (255, 0, 255))
                if (self.tiles[y][x] == "0" and not (x + y) & 1):
                    color = (60, 60, 60)

                pygame.draw.rect(screen, color, (x*tile_size, y*tile_size, tile_size, tile_size))

tiles = Tilemap.new(64, 36) 
speed = 0.15

def reset():
    global player_x, player_y, player_vx, player_vy, snake_len, snake_parts, parts_no_head, food_pos

    player_x = 10
    player_y = 10

    player_vx = 0
    player_vy = 0

    snake_len = 40
    snake_parts = []
    parts_no_head = []

    food_pos = (random.randint(0, 63), random.randint(0, 35))

def blur(surface: pygame.Surface, radius):
    scaled_surface = pygame.transform.smoothscale(surface, (surface.get_width() // radius, surface.get_height() // radius))
    scaled_surface = pygame.transform.smoothscale(scaled_surface, (surface.get_width(), surface.get_height()))
    return scaled_surface

while True:
    reset()
    alive = True
    while alive:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and player_vx != 1:
                    player_vx = -1
                    player_vy = 0
                    break
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and player_vx != -1:
                    player_vx = 1
                    player_vy = 0
                    break
                elif (event.key == pygame.K_UP or event.key == pygame.K_w) and player_vy != 1:
                    player_vx = 0
                    player_vy = -1
                    break
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and player_vy != -1:
                    player_vx = 0
                    player_vy = 1
                    break

        player_x += player_vx * speed
        player_y += player_vy * speed

        if round(player_x) == food_pos[0] and round(player_y) == food_pos[1]:
            snake_len += 1
            food_pos = (random.randint(0, 63), random.randint(0, 35))

        if (round(player_x), round(player_y)) in parts_no_head: alive = False

        if not (round(player_x), round(player_y)) in snake_parts:
            snake_parts.append((round(player_x), round(player_y)))

        if len(snake_parts) > snake_len + 1: snake_parts.pop(0)

        parts_no_head = snake_parts.copy()
        parts_no_head.pop()

        tiles.clear()

        for (sx, sy) in snake_parts: 
            if not tiles.set_tile(sx, sy, 1): alive = False

        tiles.set_tile(food_pos[0], food_pos[1], 2)

        tiles.draw(screen)

        pygame.display.set_caption(f"snaek game :D - length {snake_len} - fps: {clock.get_fps():.2f}")
        pygame.display.flip()
        clock.tick(120)

    menu = True
    background = pygame.image.tostring(screen, "RGBA")
    background = Image.frombytes("RGBA", screen.get_size(), background)

    blur_radius = 0

    buttons = {
        "play_again": Button(500, "play again", on_click=lambda: (
            globals().update({"menu": False})
        )),
        "quit": Button(575, "quit game", on_click=lambda: (
            quit()
        )),
    }

    while menu:
        blur_radius += 0.125 * (20 - blur_radius)
        if round(blur_radius) < 20:
            blurred = background.filter(ImageFilter.GaussianBlur(blur_radius))
            blurred = pygame.image.fromstring(blurred.tobytes(), blurred.size, "RGBA")
            blurred = pygame.transform.scale(blurred, screen.get_size())
        screen.blit(blurred, (0, 0))
        pygame.display.set_caption("snaek game :D - game over")

        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT: menu = False

        font = pygame.font.SysFont("SF Pro Display", 150)
        text = font.render(f"gg", True, (255, 255, 255))
        screen.blit(text, (50, screen.get_height() // 3))

        font = pygame.font.SysFont("SF Pro Display", 50)
        text = font.render(f"final length: {snake_len}", True, (255, 255, 255))
        screen.blit(text, (50, screen.get_height() // 3 + 175))

        buttons["play_again"].draw(screen)
        buttons["quit"].draw(screen)

        pygame.display.flip()
        clock.tick(120)