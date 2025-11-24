
import pygame

import pygame
import pygame.freetype
import random
import sys
import os

pygame.init()
pygame.freetype.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
FPS = 60

COLOR_SKY_TOP = (0, 0, 150)
COLOR_SKY_BOTTOM = (135, 206, 250)
COLOR_BALL = (255, 69, 0)
COLOR_PIPE = (0, 200, 0)
COLOR_PIPE_LIP = (0, 150, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_SHADOW = (0, 0, 0)
COLOR_PARTICLE = (255, 140, 0)
COLOR_CLOUD = (255, 255, 255)
COLOR_BIRD = (255, 255, 0)
COLOR_BUTTON_BG = (30, 30, 30)
COLOR_BUTTON_BORDER = (200, 200, 200)
COLOR_BUTTON_HOVER = (255, 255, 0)

def load_freetype_font(name, size):
    font = pygame.freetype.SysFont(name, size)
    font.origin = True
    font.pad = True
    return font

FONT_TITLE = load_freetype_font('Impact', 64)
FONT_MSG = load_freetype_font('Arial Black', 28)
FONT_SCORE = load_freetype_font('Arial Black', 56)
FONT_COUNTDOWN = load_freetype_font('Impact', 80)
FONT_DIFFICULTY = load_freetype_font('Arial Black', 28)

GRAVITY = 0.25
JUMP_STRENGTH = -6
PIPE_WIDTH = 60
PIPE_LIP_HEIGHT = 10
PIPE_LIP_WIDTH = PIPE_WIDTH + 20

DIFFICULTIES = {
    'Easy': {'speed': 1.5, 'gap': 220},
    'Medium': {'speed': 2.5, 'gap': 180},
    'Hard': {'speed': 3.5, 'gap': 120}
}

HIGH_SCORE_FILE = "high_score.txt"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Ball - Perfect UI/UX Edition")
clock = pygame.time.Clock()

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(score))
    except:
        pass

def draw_gradient():
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(COLOR_SKY_TOP[0] + (COLOR_SKY_BOTTOM[0] - COLOR_SKY_TOP[0]) * ratio)
        g = int(COLOR_SKY_TOP[1] + (COLOR_SKY_BOTTOM[1] - COLOR_SKY_TOP[1]) * ratio)
        b = int(COLOR_SKY_TOP[2] + (COLOR_SKY_BOTTOM[2] - COLOR_SKY_TOP[2]) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_text(text, font, color, x, y, center=True):
    text_rect = font.get_rect(text)
    if center:
        pos = (x - text_rect.width // 2, y + text_rect.height // 2)
    else:
        pos = (x, y + text_rect.height)
    font.render_to(screen, (pos[0] + 2, pos[1] + 2), text, COLOR_SHADOW)
    font.render_to(screen, pos, text, color)

class Button:
    def __init__(self, text, x, y, width, height, font, base_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(surface, COLOR_BUTTON_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 3, border_radius=8)
        text_rect = self.font.get_rect(self.text)
        text_pos = (self.rect.centerx - text_rect.width // 2, self.rect.centery + text_rect.height // 2)
        self.font.render_to(surface, text_pos, self.text, color)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.hovered and mouse_pressed[0]

def draw_heart(surface, x, y, size=20, color=(255, 0, 0)):
    points = [
        (x - size // 2, y + size // 4),
        (x, y + size),
        (x + size // 2, y + size // 4)
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.circle(surface, color, (x - size // 4, y + size // 4), size // 4)
    pygame.draw.circle(surface, color, (x + size // 4, y + size // 4), size // 4)
    pygame.draw.polygon(surface, COLOR_SHADOW, points, 2)

def draw_lives(surface, lives):
    for i in range(lives):
        x = 20 + i * 35
        y = 20
        draw_heart(surface, x, y, size=20)

def draw_countdown(surface, count, font, center_x, center_y):
    scale = 1 + 0.3 * (1 - (pygame.time.get_ticks() % 1000) / 1000)
    color_val = 200 + 55 * ((pygame.time.get_ticks() % 1000) / 1000)
    color = (min(255, color_val),) * 3
    text_surface, rect = font.render(str(count), color)
    scaled_surface = pygame.transform.smoothscale(text_surface, (int(rect.width * scale), int(rect.height * scale)))
    rect = scaled_surface.get_rect(center=(center_x, center_y))
    surface.blit(scaled_surface, rect)

def draw_score_panel(surface, score, font, center_x, top_y):
    text = str(int(score))
    text_rect = font.get_rect(text)
    padding = 15
    panel_width = text_rect.width + padding * 2
    panel_height = text_rect.height + padding * 2
    panel_rect = pygame.Rect(center_x - panel_width // 2, top_y, panel_width, panel_height)
    shadow_rect = panel_rect.move(3, 3)
    shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=10)
    surface.blit(shadow_surf, shadow_rect.topleft)
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (50, 50, 50, 180), panel_surf.get_rect(), border_radius=10)
    surface.blit(panel_surf, panel_rect.topleft)
    font.render_to(surface, (panel_rect.left + padding, panel_rect.top + padding + text_rect.height), text, COLOR_TEXT)

def update_cursor(buttons, mouse_pos):
    hovered = any(button.rect.collidepoint(mouse_pos) for button in buttons)
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hovered else pygame.SYSTEM_CURSOR_ARROW)

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.size = random.randint(4, 7)
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_PARTICLE, (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=pos)
        self.vel = [random.uniform(-2, 2), random.uniform(-2, 0)]
        self.gravity = 0.1
        self.lifetime = 30

    def update(self):
        self.vel[1] += self.gravity
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.lifetime -= 1
        alpha = max(0, int(255 * (self.lifetime / 30)))
        self.image.set_alpha(alpha)
        if self.lifetime <= 0:
            self.kill()

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 40
        self.image_orig = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image_orig, COLOR_BALL, (self.size//2, self.size//2), self.size//2)
        pygame.draw.circle(self.image_orig, (255, 255, 255), (self.size//3, self.size//3), self.size//8)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(center=(50, SCREEN_HEIGHT//2))
        self.vel_y = 0
        self.angle = 0
        self.particles = pygame.sprite.Group()
        self.shield_time = 0

    def jump(self):
        self.vel_y = JUMP_STRENGTH
        self.angle = -20
        for _ in range(5):
            self.particles.add(Particle(self.rect.midbottom))

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
        self.angle = min(self.angle + 2, 90)
        old_center = self.rect.center
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect(center=old_center)
        if self.shield_time > 0:
            self.shield_time -= 1
        self.particles.update()

    def draw(self, surface):
        if self.shield_time > 0:
            alpha = 100 + int(50 * (pygame.time.get_ticks() % 500) / 500)
            shield_color = (0, 191, 255, alpha)
            shield_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, shield_color, shield_surf.get_rect().center, self.rect.width//2 + 5)
            surface.blit(shield_surf, shield_surf.get_rect(center=self.rect.center))
        surface.blit(self.image, self.rect)
        self.particles.draw(surface)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, height, is_top):
        super().__init__()
        self.image = pygame.Surface((PIPE_LIP_WIDTH, height), pygame.SRCALPHA)
        body_rect = pygame.Rect(10, 0, PIPE_WIDTH, height)
        self.image.fill(COLOR_PIPE, body_rect)
        lip_rect = pygame.Rect(0, 0, PIPE_LIP_WIDTH, PIPE_LIP_HEIGHT)
        if not is_top:
            self.image.fill(COLOR_PIPE_LIP, lip_rect)
        else:
            lip_rect.y = height - PIPE_LIP_HEIGHT
            self.image.fill(COLOR_PIPE_LIP, lip_rect)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = 0 if is_top else SCREEN_HEIGHT - height
        self.passed = False

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(30, 50)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (200, 0, 0), (0, 0, size, size), border_radius=5)
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, size, size), 3, border_radius=5)
        self.rect = self.image.get_rect(
            x=SCREEN_WIDTH + random.randint(50, 150),
            y=random.randint(50, SCREEN_HEIGHT - 100)
        )
        self.speed = random.uniform(2, 4)

    def update(self, game_speed):
        self.rect.x -= self.speed + game_speed
        if self.rect.right < 0:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        w = random.randint(50, 100)
        h = random.randint(20, 40)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_CLOUD, (10, 10), 10)
        pygame.draw.circle(self.image, COLOR_CLOUD, (40, 15), 15)
        pygame.draw.circle(self.image, COLOR_CLOUD, (70, 10), 10)
        self.rect = self.image.get_rect(x=SCREEN_WIDTH + random.randint(0, 200), y=random.randint(50, 150))
        self.speed = random.uniform(0.5, 1.0)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH + random.randint(100, 300)
            self.rect.y = random.randint(50, 150)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_BIRD, [(0, 10), (20, 5), (20, 15)])
        self.rect = self.image.get_rect(x=SCREEN_WIDTH + random.randint(0, 400), y=random.randint(10, 100))
        self.speed = random.uniform(1.0, 2.0)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH + random.randint(200, 400)
            self.rect.y = random.randint(10, 100)

class FlappyBallGame:
    def __init__(self):
        self.ball = Ball()
        self.pipes = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.birds = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.score = 0.0
        self.high_score = load_high_score()
        self.lives = 3
        self.difficulty = 'Medium'
        self.game_speed = DIFFICULTIES[self.difficulty]['speed']
        self.pipe_gap = DIFFICULTIES[self.difficulty]['gap']
        self.state = 'intro'
        self.countdown_start = 0

        for _ in range(5):
            self.clouds.add(Cloud())
        for _ in range(3):
            self.birds.add(Bird())

        self.buttons = []
        btn_width, btn_height = 140, 40
        start_y = SCREEN_HEIGHT//2 - 45
        for i, diff in enumerate(DIFFICULTIES.keys()):
            btn = Button(diff, SCREEN_WIDTH//2 - btn_width//2, start_y + i*60, btn_width, btn_height,
                         FONT_DIFFICULTY, COLOR_BUTTON_BORDER, COLOR_BUTTON_HOVER)
            self.buttons.append(btn)

        self.enemy_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.enemy_spawn_event, 0)

    def reset(self):
        self.ball = Ball()
        self.pipes.empty()
        self.enemies.empty()
        self.score = 0.0
        self.lives = 3
        self.game_speed = DIFFICULTIES[self.difficulty]['speed']
        self.pipe_gap = DIFFICULTIES[self.difficulty]['gap']
        self.spawn_pipes()
        self.state = 'countdown'
        self.countdown_start = pygame.time.get_ticks()
        pygame.time.set_timer(self.enemy_spawn_event, max(800, int(3000 / self.game_speed)))

    def spawn_pipes(self):
        if len(self.pipes) >= 4:
            return
        min_height = 80
        max_height = SCREEN_HEIGHT - self.pipe_gap - min_height
        top_height = random.randint(min_height, max_height)
        top_pipe = Pipe(top_height, True)
        bottom_pipe = Pipe(SCREEN_HEIGHT - top_height - self.pipe_gap, False)
        if len(self.pipes) > 0:
            last_pipe_x = self.pipes.sprites()[-1].rect.x
            top_pipe.rect.x = last_pipe_x + 200 + random.randint(0, 100)
            bottom_pipe.rect.x = top_pipe.rect.x
        self.pipes.add(top_pipe, bottom_pipe)

    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == 'intro':
                    self.state = 'difficulty'
                elif self.state == 'playing':
                    self.ball.jump()
                elif self.state == 'game_over':
                    self.state = 'intro'
                    pygame.time.set_timer(self.enemy_spawn_event, 0)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == 'difficulty':
                for btn in self.buttons:
                    if btn.is_clicked(mouse_pos, mouse_pressed):
                        self.difficulty = btn.text
                        self.reset()
                        break
        if event.type == self.enemy_spawn_event and self.state == 'playing':
            if self.difficulty != 'Easy' or random.random() < 0.7:
                self.enemies 
                self.enemies.add(Enemy())
        return True

    def update(self):
        if self.state == 'countdown':
            elapsed = (pygame.time.get_ticks() - self.countdown_start) // 1000
            if elapsed >= 3:
                self.state = 'playing'

        if self.state in ('playing', 'countdown'):
            self.ball.update()
            self.clouds.update()
            self.birds.update()

        if self.state == 'playing':
            self.pipes.update(self.game_speed)
            self.enemies.update(self.game_speed)

            if len(self.pipes) == 0 or (len(self.pipes) > 0 and self.pipes.sprites()[-1].rect.x < SCREEN_WIDTH - 250):
                self.spawn_pipes()

            for pipe in self.pipes:
                is_top_pipe = pipe.rect.y < SCREEN_HEIGHT / 2
                if is_top_pipe and not pipe.passed and pipe.rect.right < self.ball.rect.left:
                    pipe.passed = True
                    self.score += 1.0
                    if self.score > self.high_score:
                        self.high_score = int(self.score)
                        save_high_score(self.high_score)

            if pygame.sprite.spritecollideany(self.ball, self.pipes) and self.ball.shield_time <= 0:
                self.lives -= 1
                self.ball.shield_time = FPS * 2
                if self.lives <= 0:
                    self.state = 'game_over'

            enemy_hit = pygame.sprite.spritecollideany(self.ball, self.enemies)
            if enemy_hit and self.ball.shield_time <= 0:
                self.lives -= 1
                self.ball.shield_time = FPS * 2
                enemy_hit.kill()
                if self.lives <= 0:
                    self.state = 'game_over'

            if self.ball.rect.top <= 0 or self.ball.rect.bottom >= SCREEN_HEIGHT:
                if self.ball.shield_time <= 0:
                    self.lives -= 1
                    self.ball.shield_time = FPS * 2
                    if self.lives <= 0:
                        self.state = 'game_over'

    def draw(self):
        draw_gradient()
        self.clouds.draw(screen)
        self.birds.draw(screen)

        if self.state in ('playing', 'game_over', 'countdown'):
            self.pipes.draw(screen)
            self.enemies.draw(screen)
            self.ball.draw(screen)
            draw_score_panel(screen, int(self.score), FONT_SCORE, SCREEN_WIDTH // 2, 10)
            draw_lives(screen, self.lives)

        if self.state == 'intro':
            draw_text("Flappy Ball", FONT_TITLE, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80)
            draw_text(f"High Score: {self.high_score}", FONT_MSG, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            draw_text("Press SPACE to Select Difficulty", FONT_MSG, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60)

        elif self.state == 'difficulty':
            draw_text("Select Difficulty", FONT_TITLE, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)
            for btn in self.buttons:
                btn.draw(screen)

        elif self.state == 'countdown':
            elapsed = (pygame.time.get_ticks() - self.countdown_start) // 1000
            if elapsed < 3:
                draw_countdown(screen, 3 - elapsed, FONT_COUNTDOWN, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        elif self.state == 'game_over':
            draw_text("GAME OVER", FONT_TITLE, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80)
            draw_text(f"Final Score: {int(self.score)}", FONT_MSG, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            draw_text("Press SPACE to try again", FONT_MSG, COLOR_TEXT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60)

def main():
    game = FlappyBallGame()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            running = game.handle_events(event)
            if not running:
                break

        if not running:
            break

        if game.state == 'difficulty':
            for btn in game.buttons:
                btn.update(mouse_pos)
            update_cursor(game.buttons, mouse_pos)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()