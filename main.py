import pygame, random, sys, time
from PIL import Image, ImageFilter

pygame.init()
pygame.font.init()
pygame.display.set_mode((1280, 720))
screen = pygame.display.get_surface()
clock = pygame.time.Clock()

def quit():
    pygame.quit()
    sys.exit()

def lerp(a, b, t):
    return a + (b - a) * t

spritesheet = pygame.image.load("images/spritesheet.png").convert_alpha()

def get_sprites():
    sprites = []
    for y in range(0, 32, 8):
        for x in range(0, 32, 8):
            sprite = pygame.Surface((8, 8))
            sprite.blit(spritesheet, (0, 0), (x, y, 8, 8))
            sprite = pygame.transform.scale(sprite, (20, 20))
            sprite.set_colorkey((0, 0, 0))
            sprites.append(sprite)
    return sprites

sprites = get_sprites()

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

        pygame.draw.rect(screen, (255, 20, 240, int(255 * anim_t)), (50, self.y, self.rect_width, 50), 0)
        font = pygame.font.SysFont("SF Pro Display", 25)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_surface.set_alpha(int(255 * anim_t))
        text_rect = text_surface.get_rect(center=(50 + 100, self.y + 25))
        screen.blit(text_surface, text_rect)

class Tilemap:
    def __init__(self, tiles=[], mirror_map=[]):
        self.tiles = tiles
        self.mirror_map = mirror_map

    @staticmethod
    def new(w, h):
        return Tilemap(["0" * w for _ in range(h)], ["0" * w for _ in range(h)])
    
    def clear(self):
        self.tiles = ["0" * len(self.tiles[0]) for _ in range(len(self.tiles))]
        self.mirror_map = ["0" * len(self.tiles[0]) for _ in range(len(self.tiles))]
    
    def set_tile(self, x, y, tile, mirror=0):
        if y < 0 or y >= len(self.tiles) or x < 0 or x >= len(self.tiles[y]):
            return False
        
        row = self.tiles[y]
        mirror_row = self.mirror_map[y]


        for i in range(len(row)):
            if i == x:
                row = row[:i] + str(tile) + row[i+1:]
                mirror_row = mirror_row[:i] + str(mirror) + mirror_row[i+1:]
                break

        self.tiles[y] = row
        self.mirror_map[y] = mirror_row
        return True

    def draw(self, screen):
        tile_size = 20
        color_map = {
            "0": (63, 63, 63),  # empty tile (dark gray)
            "A": sprites[0],    # type A (straight piece horizontal)
            "B": sprites[1],    # type B (corner piece 0)
            "C": sprites[2],    # type C (head piece 0)
            "D": sprites[3],    # type D (tail piece 0)
            "E": sprites[4],    # type E (straight piece vertical)
            "F": sprites[5],    # type F (corner piece 1)
            "G": sprites[6],    # type G (head piece 1)
            "H": sprites[7],    # type H (tail piece 1)
            "I": sprites[8],    # type I (apple)
            "J": sprites[9],    # type J (corner piece 2)
            "K": sprites[12],   # type K (rotten apple)
            "L": sprites[13],   # type L (corner piece 3)
            "M": sprites[10],   # type M (snake head turning horizontal)
            "N": sprites[14],   # type N (snake tail turning vertical)
            "O": sprites[11],   # type O (snake head turning horizontal mirror)
            "P": sprites[15]    # type P (snake body turning vertical mirror)
        }

        mirror_map = {
            "0": "x",
            "1": "x",
            "2": "x",
            "A": "x",
            "B": "x",
            "C": "x",
            "D": "x",
            "E": "y",
            "F": "x",
            "G": "y",
            "H": "y",
            "I": "x",
            "J": "x",
            "K": "x",
            "L": "x",
            "M": "x",
            "N": "y",
            "O": "x",
            "P": "y",
        }

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if self.tiles[y][x] in color_map:
                    if isinstance(color_map[self.tiles[y][x]], pygame.Surface):
                        if (x + y) & 1:
                            pygame.draw.rect(screen, color_map.get("0"), (x*tile_size, y*tile_size, tile_size, tile_size))
                        else:
                            pygame.draw.rect(screen, (60, 60, 60), (x*tile_size, y*tile_size, tile_size, tile_size))
                        if self.mirror_map[y][x] == "0":
                            screen.blit(color_map[self.tiles[y][x]], (x*tile_size, y*tile_size))
                        else:
                            if mirror_map[self.tiles[y][x]] == "x":
                                screen.blit(pygame.transform.flip(color_map[self.tiles[y][x]], True, False), (x*tile_size, y*tile_size))
                            else:
                                screen.blit(pygame.transform.flip(color_map[self.tiles[y][x]], False, True), (x*tile_size, y*tile_size))
                        continue
                color = color_map.get(self.tiles[y][x], (255, 0, 255))
                if (self.tiles[y][x] == "0" and not (x + y) & 1):
                    color = (60, 60, 60)

                pygame.draw.rect(screen, color, (x*tile_size, y*tile_size, tile_size, tile_size))

tiles = Tilemap.new(64, 36) 
speed = 0.15

def get_time_data():
    year = time.localtime().tm_year
    month = time.localtime().tm_mon
    day = time.localtime().tm_mday
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    second = time.localtime().tm_sec
    return {
        "year": str(year), 
        "month": ("0" if int(month) < 10 else "") + str(month), 
        "day": ("0" if int(day) < 10 else "") + str(day), 
        "hour": ("0" if int(hour) < 10 else "") + str(hour), 
        "minute": ("0" if int(minute) < 10 else "") + str(minute), 
        "second": ("0" if int(second) < 10 else "") + str(second)
    }

def reset():
    global player_x, player_y, player_vx, player_vy, snake_len, snake_parts, parts_no_head, food_pos

    player_x = 10
    player_y = 10

    player_vx = 0
    player_vy = 0

    snake_len = 10
    snake_parts = []
    parts_no_head = []

    food_pos = (random.randint(0, 63), random.randint(0, 35))

while True:
    reset()
    alive = True
    take_screenshot = False
    while alive:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2: take_screenshot = True
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and diff != (1, 0):
                    player_vx = -1
                    player_vy = 0
                    break
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and diff != (-1, 0):
                    player_vx = 1
                    player_vy = 0
                    break
                elif (event.key == pygame.K_UP or event.key == pygame.K_w) and diff != (0, 1):
                    player_vx = 0
                    player_vy = -1
                    break
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and diff != (0, -1):
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

        if len(parts_no_head) > 0: diff = (round(player_x) - parts_no_head[len(parts_no_head)-1][0], round(player_y) - parts_no_head[len(parts_no_head)-1][1])
        else: diff = (0, 0)

        tiles.clear()

        for i, (sx, sy) in enumerate(snake_parts):
            tile_diff_prev = (0, 0)
            tile_diff_next = (0, 0)
            tile = "A"
            mirror = 0
            if i == 0:
                if len(snake_parts) == 1:
                    tile = "C"
                    if player_vy != 0: tile = "G"
                    mirror = 0 if (player_vx if tile != "G" else player_vy) > 0 else 1
                else:
                    tile_diff = (snake_parts[0][0] - snake_parts[1][0], snake_parts[0][1] - snake_parts[1][1])
                    tile = "D"
                    if tile_diff[1] != 0: tile = "H"
                    mirror = 0 if (tile_diff[0] if tile != "H" else tile_diff[1]) > 0 else 1
            elif i == len(snake_parts) - 1:
                tile_diff = (snake_parts[i][0] - snake_parts[i-1][0], snake_parts[i][1] - snake_parts[i-1][1])
                if player_vx == tile_diff[0] and player_vy == tile_diff[1]:
                    tile = "C"
                    if player_vy != 0: tile = "G"
                    mirror = 0 if (player_vx if tile != "G" else player_vy) > 0 else 1
                else:
                    if len(snake_parts) > 1:
                        if player_vy == -1: 
                            tile = "N"
                            if tile_diff[0] == -1: mirror = 1
                        if player_vy == 1: 
                            tile = "P"
                            #mirror = 1
                        if player_vx == -1:
                            tile = "O"
                            #mirror = 0
                        if player_vx == 1:
                            tile = "M"
                            #mirror = 1

            else:
                tile_diff_prev = (snake_parts[i][0] - snake_parts[i-1][0], snake_parts[i][1] - snake_parts[i-1][1])
                tile_diff_next = (snake_parts[i+1][0] - snake_parts[i][0], snake_parts[i+1][1] - snake_parts[i][1])
                if tile_diff_prev[0] == tile_diff_next[0] and tile_diff_prev[1] == tile_diff_next[1]:
                    tile = "A"
                    if tile_diff_next[1] != 0: tile = "E"
                    mirror = 0 if (tile_diff_next[0] if tile != "E" else tile_diff_next[1]) > 0 else 1
                else:
                    corner_diff = (tile_diff_prev[0] - tile_diff_next[0], tile_diff_prev[1] - tile_diff_next[1])
                    if corner_diff[0] == -1 and corner_diff[1] == -1:
                        tile = "J"
                    if corner_diff[0] == 1 and corner_diff[1] == -1:
                        tile = "L"
                    if corner_diff[0] == -1 and corner_diff[1] == 1:
                        tile = "F"
                    if corner_diff[0] == 1 and corner_diff[1] == 1:
                        tile = "B"
                    


            if not tiles.set_tile(sx, sy, tile, mirror=mirror): alive = False

        tiles.set_tile(food_pos[0], food_pos[1], "I")

        tiles.draw(screen)

        pygame.display.set_caption(f"snaek game :D - length {snake_len} - fps: {clock.get_fps():.2f}")
        pygame.display.flip()

        if take_screenshot:
            td = get_time_data()
            pygame.image.save(screen, f"screenshots/snake_{td['year']}-{td['month']}-{td['day']}_{td['hour']}-{td['minute']}-{td['second']}.png")
            take_screenshot = False

        clock.tick(90)

    menu = True
    dimensions = (screen.get_size()[0] // 2, screen.get_size()[1] // 2)
    background = pygame.image.tostring(pygame.transform.scale(screen, dimensions), "RGB")
    background = Image.frombytes("RGB", dimensions, background).filter(ImageFilter.EDGE_ENHANCE)

    blur_radius = 0
    global anim_t
    anim_t = 0

    buttons = {
        "play_again": Button(500, "play again", on_click=lambda: (
            globals().update({"menu": False})
        )),
        "quit": Button(575, "quit game", on_click=lambda: (
            quit()
        )),
    }

    death_screen = pygame.Surface((1280, 720), pygame.SRCALPHA)
    while menu:
        
        blur_radius += 0.0625 * (10 - blur_radius)
        anim_t += 0.0625 * (1 - anim_t)
        if round(blur_radius) < 10:
            blurred = background.filter(ImageFilter.GaussianBlur(blur_radius))
            blurred = pygame.image.fromstring(blurred.tobytes(), blurred.size, "RGB")
            blurred = pygame.transform.scale(blurred, screen.get_size())
        death_screen.fill((0, 0, 0, 0))
        screen.blit(blurred, (0, 0))
        
        pygame.display.set_caption("snaek game :D - game over")

        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2: take_screenshot = True
                if event.key == pygame.K_LSHIFT: menu = False

        font = pygame.font.Font("fonts/SF-Pro-Display-Bold.otf", int(lerp(100, 150, anim_t)))
        text = font.render(f"gg", True, (255, 255, 255))
        text.set_alpha(int(255 * anim_t))
        death_screen.blit(text, (lerp(death_screen.get_width() // 2, 50, lerp(0.75, 1, anim_t)), death_screen.get_height() // 3 + int(lerp(50, 0, anim_t))))

        font = pygame.font.Font("fonts/SF-Pro-Display-Bold.otf", 50)
        text = font.render(f"final length: {snake_len}", True, (255, 255, 255))
        text.set_alpha(int(255 * anim_t))
        death_screen.blit(text, (lerp(death_screen.get_width() // 2, 50, lerp(0.75, 1, anim_t)), death_screen.get_height() // 3 + 175 + int(lerp(25, 0, anim_t))))

        buttons["play_again"].draw(death_screen)
        buttons["quit"].draw(death_screen)

        screen.blit(death_screen, (0, 0))

        pygame.display.flip()

        if take_screenshot:
            td = get_time_data()
            pygame.image.save(screen, f"screenshots/snake_{td['year']}-{td['month']}-{td['day']}_{td['hour']}-{td['minute']}-{td['second']}.png")
            take_screenshot = False

        clock.tick(120)