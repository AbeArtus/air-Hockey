import pygame
import random
import sys
import asyncio
import math

# Initialize Pygame
pygame.init()
# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)

gamestate = 0


def minmax(x, minx, maxx):
    return min(max(x, minx), maxx)


accel = 0.9  # Acceleration rate
max_speed = 12  # Maximum speed
decel_rate = 0.94  # Deceleration rate


def paddle2_controls(keys, paddle):
    # Check individual keys for moement
    move_up = keys[pygame.K_UP]
    move_down = keys[pygame.K_DOWN]
    move_left = keys[pygame.K_LEFT]
    move_right = keys[pygame.K_RIGHT]

    # Apply acceleration based on pressed keys
    if move_up:
        paddle.Yvel -= accel
    if move_down:
        paddle.Yvel += accel
    if move_left:
        paddle.Xvel -= accel * 1.1
    if move_right:
        paddle.Xvel += accel * 1.1

    # Decelerate when no movement keys are pressed
    if not (move_up or move_down or move_left or move_right):
        paddle.Xvel *= decel_rate
        paddle.Yvel *= decel_rate

    # Limit maximum speed
    paddle.Xvel = min(max_speed, max(-max_speed, paddle.Xvel))
    paddle.Yvel = min(max_speed, max(-max_speed, paddle.Yvel))

    # Update paddle position
    paddle.rect.x += int(paddle.Xvel)
    paddle.rect.y += int(paddle.Yvel)


def paddle1_controls(keys, paddle):
    # Check individual keys for movement
    move_up = keys[pygame.K_w]
    move_down = keys[pygame.K_s]
    move_left = keys[pygame.K_a]
    move_right = keys[pygame.K_d]

    # Apply acceleration based on pressed keys
    if move_up:
        paddle.Yvel -= accel
    if move_down:
        paddle.Yvel += accel
    if move_left:
        paddle.Xvel -= accel * 1.1
    if move_right:
        paddle.Xvel += accel * 1.1
    # Decelerate when no movement keys are pressed
    if not (move_up or move_down or move_left or move_right):
        paddle.Xvel *= decel_rate
        paddle.Yvel *= decel_rate

    # Limit maximum speed
    paddle.Xvel = min(max_speed, max(-max_speed, paddle.Xvel)) 
    paddle.Yvel = min(max_speed, max(-max_speed, paddle.Yvel))

    # Update paddle position
    paddle.rect.x += int(paddle.Xvel)
    paddle.rect.y += int(paddle.Yvel)


# Define the paddles
class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, radius):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.radius = radius
        self.Xvel = 0
        self.Yvel = 0


class box(pygame.sprite.Sprite):
    def __init__(self, color, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.width = width
        self.height = height
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_centerX(self):
        return self.rect.x + self.width // 2

    def get_centerY(self):
        return self.rect.y + self.height // 2


# Define the ball
class Ball(pygame.sprite.Sprite):
    def __init__(self, color, radius):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.velocity = [0, 0]
        self.rect = self.image.get_rect()
        self.radius = radius

    def get_centerX(self):
        return self.rect.x + self.radius

    def get_centerY(self):
        return self.rect.y + self.radius


def update(ball, paddle_sprites, box_sprites):
    # Ball and screen edge collision
    deceleration = 0.995
    if ball.rect.top <= 0 or ball.rect.bottom >= screen_height:
        ball.velocity[1] = -ball.velocity[1]

    # Ball and paddle collision
    for paddle in paddle_sprites:
        if pygame.sprite.collide_circle(ball, paddle):
            # Calculate the angle between the ball and paddle
            dx = ball.rect.centerx - paddle.rect.centerx
            dy = ball.rect.centery - paddle.rect.centery
            angle = math.atan2(dy, dx)

            # Calculate the magnitude of the combined velocity
            magnitude = math.sqrt(ball.velocity[0] ** 2 + ball.velocity[1] ** 2 + paddle.Xvel**2 + paddle.Yvel**2)

            # Set the new velocity based on angle and magnitude
            ball.velocity[0] = magnitude * math.cos(angle)
            ball.velocity[1] = magnitude * math.sin(angle)
            break  # Exit the loop after handling collision with one paddle

    # Ball and box collision
    if pygame.sprite.spritecollide(ball, box_sprites, False):
        ballrad = ball.radius 
        for box in pygame.sprite.spritecollide(ball, box_sprites, False):
            dy = ball.get_centerY() - box.get_centerY()
            dx = ball.get_centerX() - box.get_centerX()
        if ball.get_centerX() < screen_width // 2:
            if (dy <= ballrad + box.height // 2 or dy <= -(ballrad + box.height // 2)) and dx >= (box.width//2 + ball.radius) -1 :
                ball.velocity[0] = -ball.velocity[0]
            else:
                ball.velocity[1] = -ball.velocity[1]
        else:
            if (dy <= ballrad + box.height // 2 or dy <= -(ballrad + box.height // 2)) and dx <= -(box.width//2 + ball.radius) + 1 :
                ball.velocity[0] = -ball.velocity[0]
            else:
                ball.velocity[1] = -ball.velocity[1]

    ball.velocity[0] = minmax(ball.velocity[0], -10, 10) * deceleration
    ball.velocity[1] = minmax(ball.velocity[1], -10, 10) * deceleration

    ball.rect.x += ball.velocity[0]
    ball.rect.y += ball.velocity[1]

    if ball.get_centerY() < 200 or ball.get_centerY() >= screen_height - 200:
        ball.rect.x = minmax(ball.rect.x, 49, screen_width - 49 - ball.radius * 2)


# Create paddles
paddle1 = Paddle(DARK_RED, 30)
paddle1.rect.x = 50
paddle1.rect.y = screen_height // 2 - paddle1.radius
paddle2 = Paddle(DARK_RED, 30)
paddle2.rect.x = screen_width - 50 - paddle2.radius*2
paddle2.rect.y = screen_height // 2 - paddle2.radius

# Create the ball
ball = Ball(RED, 24)
ball.rect.x = screen_width // 2 - ball.radius
ball.rect.y = screen_height // 2 - ball.radius

# Create boxes for the goal
box1 = box(BLACK, 50, 200, 0, 0)  # Top-left corner
box2 = box(BLACK, 50, 200, screen_width - 50, 0)  # Top-right corner
box3 = box(BLACK, 50, 200, 0, screen_height - 200)  # Bottom-left corner
box4 = box(BLACK, 50, 200, screen_width - 50, screen_height - 200)  # Bottom-right corner

# Create paddle sprite groups
paddle_sprites = pygame.sprite.Group()
paddle_sprites.add(paddle1, paddle2)
# Create ball spritegamegroups
ball_sprite = pygame.sprite.Group()
ball_sprite.add(ball)
# Create the box group
box_sprites = pygame.sprite.Group()
box_sprites.add(box1, box2, box3, box4)


font = pygame.font.Font(None, 36)


async def main():
    # Main loop
    running = True
    clock = pygame.time.Clock()

    # Set initial game state
    paused = False

    # Player Score
    p1_score = 0
    p2_score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        paddle1_controls(keys, paddle1)
        paddle2_controls(keys, paddle2)

        # Limit paddle movement within the screen boundaries
        paddle1.rect.y = max(min(paddle1.rect.y, screen_height - paddle1.rect.height), 0)
        paddle2.rect.y = max(min(paddle2.rect.y, screen_height - paddle2.rect.height), 0)
        paddle1.rect.x = max(min(paddle1.rect.x, screen_width // 2 - paddle1.radius * 2), 50)
        paddle2.rect.x = max(min(paddle2.rect.x, screen_width - 50 - paddle2.radius * 2), screen_width // 2)
        ball.rect.y = minmax(ball.rect.y, 0, screen_height - ball.radius * 2)

        # Handle scoring, and reset
        if ball.rect.x + ball.radius * 2 <= 0:
            p2_score += 1
            paddle1.rect.x = 1 / 4 * screen_width - paddle1.radius
            paddle1.rect.y = 1 / 2 * screen_height - paddle1.radius
            paddle2.rect.x = 3 / 4 * screen_width - paddle1.radius
            paddle2.rect.y = 1 / 2 * screen_height - paddle2.radius
            ball.rect.y = 1 / 2 * screen_height - ball.radius
            ball.rect.x = 1 / 2 * screen_width - ball.radius * 4
            ball.velocity = [0, 0]
        elif ball.rect.x > screen_width + ball.radius * 2:
            p1_score += 1
            paddle1.rect.x = 1 / 4 * screen_width - paddle1.radius
            paddle1.rect.y = (1 / 2 * screen_height) - paddle1.radius
            paddle2.rect.x = 3 / 4 * screen_width - paddle1.radius
            paddle2.rect.y = 1 / 2 * screen_height - paddle1.radius
            ball.rect.y = (1 / 2 * screen_height) - ball.radius
            ball.rect.x = 1 / 2 * screen_width + ball.radius * 2
            ball.velocity = [0, 0]

        update(ball, paddle_sprites, box_sprites)

        # Draw
        screen.fill(WHITE)
        box_sprites.draw(screen)
        ball_sprite.draw(screen)
        paddle_sprites.draw(screen)

        # render the score text
        score_text = font.render(f"{p1_score} : {p2_score}", True, BLACK)
        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 10))

        # Flip the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


asyncio.run(main())
