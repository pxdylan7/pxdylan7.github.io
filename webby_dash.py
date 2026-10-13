import pygame

pygame.init()

WIDTH = 800
HEIGHT = 450
FPS = 60
TILE = 40
GROUND_Y = HEIGHT - 80

PLAYER_X = 160
SPEED = 6
GRAVITY = 1
JUMP_STRENGTH = -15

START_DISTANCE = 600

# "#" is a block you can land on, "^" is a spike, "." is empty air.
# The bottom row sits on the ground; each row above it is one tile higher.
LEVEL = [
    "..............................................##...............................................................................................^.................................................................",
    "............................................####..........^................########..................................#.......#...............####...........................##...................................",
    "..........^.......^^......^^^.....^.^.....######.......##########.......##^^^^^^^^##........^^.....^.^....^^^....#^^.#.^^#^^.#.^^#.........######.........^^^.....^.^.....####.....^.......^^^...................",
]

LEVEL_END = START_DISTANCE + len(LEVEL[0]) * TILE

SKY_TOP = (255, 190, 115)
SKY_BOTTOM = (220, 108, 92)
SUN = (255, 226, 152)
FAR_HILLS = (186, 118, 102)
NEAR_HILLS = (130, 96, 76)
GROUND = (92, 70, 56)
GROUND_MARK = (114, 88, 68)
BLOCK = (100, 68, 110)
BLOCK_EDGE = (68, 46, 78)
SPIKE = (150, 66, 58)
SPIKE_EDGE = (98, 40, 36)
PLAYER = (255, 206, 92)
PLAYER_EDGE = (190, 108, 50)
TEXT = (255, 246, 230)
BUTTON = (176, 84, 62)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Webby Dash")
clock = pygame.time.Clock()
big_font = pygame.font.SysFont(None, 72)
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)


def make_background():
    background = pygame.Surface((WIDTH, HEIGHT))

    for y in range(HEIGHT):
        blend = y / HEIGHT
        red = SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * blend
        green = SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * blend
        blue = SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * blend
        pygame.draw.line(background, (red, green, blue), (0, y), (WIDTH, y))

    pygame.draw.circle(background, SUN, (WIDTH - 200, GROUND_Y - 110), 60)
    pygame.draw.ellipse(background, FAR_HILLS, (-150, GROUND_Y - 170, 500, 340))
    pygame.draw.ellipse(background, FAR_HILLS, (300, GROUND_Y - 140, 600, 300))
    pygame.draw.ellipse(background, NEAR_HILLS, (-80, GROUND_Y - 100, 420, 220))
    pygame.draw.ellipse(background, NEAR_HILLS, (420, GROUND_Y - 90, 480, 200))
    return background


def build_level():
    obstacles = []
    for row_number, row in enumerate(LEVEL):
        tiles_above_ground = len(LEVEL) - row_number
        y = GROUND_Y - tiles_above_ground * TILE
        for column, symbol in enumerate(row):
            x = START_DISTANCE + column * TILE
            if symbol == "#":
                obstacles.append({"kind": "block", "rect": pygame.Rect(x, y, TILE, TILE)})
            elif symbol == "^":
                obstacles.append({"kind": "spike", "rect": pygame.Rect(x, y, TILE, TILE)})
    return obstacles


def spike_hitbox(rect):
    return pygame.Rect(rect.x + 12, rect.y + 16, rect.width - 24, rect.height - 16)


def draw_block(rect):
    pygame.draw.rect(screen, BLOCK, rect)
    pygame.draw.rect(screen, BLOCK_EDGE, rect, 3)


def draw_spike(rect):
    points = [(rect.left, rect.bottom), (rect.centerx, rect.top), (rect.right, rect.bottom)]
    pygame.draw.polygon(screen, SPIKE, points)
    pygame.draw.polygon(screen, SPIKE_EDGE, points, 3)


def draw_player(player_y, angle):
    square = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    square.fill(PLAYER)
    pygame.draw.rect(square, PLAYER_EDGE, (0, 0, TILE, TILE), 4)
    pygame.draw.rect(square, PLAYER_EDGE, (12, 12, 16, 16))

    rotated = pygame.transform.rotate(square, angle)
    center = (PLAYER_X + TILE // 2, int(player_y) + TILE // 2)
    screen.blit(rotated, rotated.get_rect(center=center))


def draw_ground(camera_x):
    pygame.draw.rect(screen, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.line(screen, TEXT, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

    first_mark = -(camera_x % 80)
    for x in range(first_mark, WIDTH, 80):
        pygame.draw.rect(screen, GROUND_MARK, (x, GROUND_Y + 30, 40, 6))


def draw_progress_bar(progress):
    outline = pygame.Rect(WIDTH // 2 - 150, 20, 300, 14)
    filled = pygame.Rect(outline.x, outline.y, outline.width * progress // 100, outline.height)
    pygame.draw.rect(screen, PLAYER, filled)
    pygame.draw.rect(screen, TEXT, outline, 2)


def draw_text(text, text_font, center_y):
    image = text_font.render(text, True, TEXT)
    rect = image.get_rect(center=(WIDTH // 2, center_y))
    screen.blit(image, rect)


background = make_background()
obstacles = build_level()
play_button = pygame.Rect(0, 0, 160, 60)
play_button.center = (WIDTH // 2, HEIGHT // 2 + 10)

state = "menu"
player_y = GROUND_Y - TILE
velocity = 0
angle = 0
on_ground = True
camera_x = 0
progress = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state != "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and play_button.collidepoint(event.pos):
                player_y = GROUND_Y - TILE
                velocity = 0
                angle = 0
                on_ground = True
                camera_x = 0
                progress = 0
                state = "playing"

    if state == "playing":
        camera_x = camera_x + SPEED

        keys = pygame.key.get_pressed()
        wants_to_jump = keys[pygame.K_SPACE] or keys[pygame.K_UP] or pygame.mouse.get_pressed()[0]
        if on_ground and wants_to_jump:
            velocity = JUMP_STRENGTH

        previous_bottom = player_y + TILE
        velocity = velocity + GRAVITY
        player_y = player_y + velocity
        on_ground = False

        if player_y + TILE >= GROUND_Y:
            player_y = GROUND_Y - TILE
            velocity = 0
            on_ground = True

        player_rect = pygame.Rect(PLAYER_X, int(player_y), TILE, TILE)

        for obstacle in obstacles:
            rect = obstacle["rect"].move(-camera_x, 0)

            if obstacle["kind"] == "spike":
                if player_rect.colliderect(spike_hitbox(rect)):
                    state = "crashed"

            elif player_rect.colliderect(rect):
                landed_on_top = velocity >= 0 and previous_bottom <= rect.top + 10
                if landed_on_top:
                    player_y = rect.top - TILE
                    velocity = 0
                    on_ground = True
                    player_rect.y = int(player_y)
                else:
                    state = "crashed"

        if on_ground:
            angle = round(angle / 90) * 90
        else:
            angle = angle - 7

        progress = min(100, 100 * camera_x // LEVEL_END)
        if camera_x >= LEVEL_END:
            state = "won"

    screen.blit(background, (0, 0))

    for obstacle in obstacles:
        rect = obstacle["rect"].move(-camera_x, 0)
        if -TILE < rect.x < WIDTH:
            if obstacle["kind"] == "block":
                draw_block(rect)
            else:
                draw_spike(rect)

    draw_ground(camera_x)
    draw_player(player_y, angle)

    if state == "playing":
        draw_progress_bar(progress)
    else:
        if state == "menu":
            draw_text("Webby Dash", big_font, HEIGHT // 2 - 100)
            draw_text("Hold space or click to jump", small_font, HEIGHT // 2 - 50)
            button_label = "Play"
        elif state == "crashed":
            draw_text("Crashed!", big_font, HEIGHT // 2 - 100)
            draw_text(str(progress) + "% complete", font, HEIGHT // 2 - 50)
            button_label = "Replay"
        else:
            draw_text("Level Complete!", big_font, HEIGHT // 2 - 100)
            button_label = "Replay"

        pygame.draw.rect(screen, BUTTON, play_button, border_radius=12)
        draw_text(button_label, font, play_button.centery)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
