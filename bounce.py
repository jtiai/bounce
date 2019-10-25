import random
import pygame as pg

DEBUG = False

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

pg.init()
clock = pg.time.Clock()
pg.display.set_caption("Bounce")
screen = pg.display.set_mode((500, 500), pg.FULLSCREEN)

pg.mouse.set_visible(False)
pg.event.set_grab(True)


class Bat(pg.sprite.DirtySprite):
    def __init__(self, tag, pos):
        super().__init__()
        self.tag = tag
        self.prev_rect = None
        self.outwards_vector = None
        self.normal = self.outwards_vector

    def set_outwards_vector(self):
        v = pg.math.Vector2(250 - self.rect.centerx, 250 - self.rect.centery)
        v.normalize_ip()
        self.outwards_vector = v
        print(f"{self.tag}: {v}")

    def update(self, *args, **kwargs):
        self.prev_rect = self.rect.copy()

    def get_rel(self):
        return (self.rect.centerx - self.prev_rect.centerx), (self.rect.centery - self.prev_rect.centery)

    def get_collision_angle(self, pos):
        raise NotImplementedError()


class HorizontalBat(Bat):
    def __init__(self, tag, pos):
        super().__init__(tag, pos)
        self.image = pg.Surface((100, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos
        self.prev_rect = self.rect.copy()
        self.set_outwards_vector()
        self.normal = self.outwards_vector  # right hand vector

    def update(self, *args, dx, **kwargs):
        super().update(*args, dx=dx, **kwargs)
        self.rect.centerx += dx
        if self.rect.left < 25:
            self.rect.left = 25
        if self.rect.right > 475:
            self.rect.right = 475

    def get_pos_on_inner_edge(self, delta=0):
        if self.rect.top > 250:
            return self.rect.top - delta
        return self.rect.bottom + delta

    def get_collision_angle(self, pos):
        dist = self.rect.centerx - pos[0]  # Distance of collision
        angle = (40 / 50) * dist
        return angle


class VerticalBat(Bat):
    def __init__(self, tag, pos):
        super().__init__(tag, pos)
        self.image = pg.Surface((20, 100))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos
        self.set_outwards_vector()
        self.normal = self.outwards_vector  # right hand vector

    def update(self, *args, dy, **kwargs):
        super().update(*args, dy=dy, **kwargs)
        self.rect.centery += dy
        if self.rect.top < 25:
            self.rect.top = 25
        if self.rect.bottom > 475:
            self.rect.bottom = 475

    def get_pos_on_inner_edge(self, delta=0):
        if self.rect.left > 250:
            return self.rect.left - delta
        return self.rect.right + delta

    def get_collision_angle(self, pos):
        dist = self.rect.centery - pos[1]  # Distance of collision
        angle = (40 / 50) * dist
        return angle


class Ball(pg.sprite.DirtySprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((23, 23))
        self.rect = pg.draw.circle(self.image, WHITE, (11, 11), 11)
        self.rect.center = pos
        self.follow = None
        self.speed = 3
        self.direction = None
        self.pos = None

    def set_pos(self, pos):
        self.pos = pos

    def update(self, *args, **kwargs):
        if self.follow:
            dx, dy = self.follow.get_rel()
            self.rect.centerx += dx
            self.rect.centery += dy
        else:
            self.pos += self.direction * self.speed
            self.rect.centerx = self.pos.x
            self.rect.centery = self.pos.y


bat_sprites = pg.sprite.RenderUpdates([
    VerticalBat("left", (15, 250)),
    VerticalBat("right", (485, 250)),
    HorizontalBat("top", (250, 15)),
    HorizontalBat("bottom", (250, 485)),

])

ball = Ball((0, 0))

ball_sprites = pg.sprite.RenderUpdates([
    ball,
])

# Get first relative position
pg.mouse.get_rel()

initial_bat = bat_sprites.sprites()[random.randint(0, 3)]
if isinstance(initial_bat, HorizontalBat):
    ball.rect.centery = initial_bat.get_pos_on_inner_edge(11)
    ball.rect.centerx = random.randint(initial_bat.rect.left + ball.rect.width, initial_bat.rect.right - ball.rect.width)
else:
    ball.rect.centerx = initial_bat.get_pos_on_inner_edge(11)
    ball.rect.centery = random.randint(initial_bat.rect.top + ball.rect.height, initial_bat.rect.bottom - ball.rect.height)

done = False
ball.follow = initial_bat
ball.direction = pg.math.Vector2(250 - ball.rect.centerx, 250 - ball.rect.centery)
ball.direction.normalize_ip()
ball.direction.rotate(initial_bat.get_collision_angle(ball.rect.center))

game_area = pg.Rect(11, 11, 500 - 23, 500 - 23)

while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            done = True

        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            if ball.follow:
                v = ball.follow.outwards_vector
                ball.follow = None
                ball.pos = pg.math.Vector2(ball.rect.center)


    screen.fill(BLACK)

    dx, dy = pg.mouse.get_rel()
    bat_sprites.update(dx=dx, dy=dy)
    ball.update()
    if not game_area.contains(ball):
        # Game over
        initial_bat = bat_sprites.sprites()[random.randint(0, 3)]
        if isinstance(initial_bat, HorizontalBat):
            ball.rect.centery = initial_bat.get_pos_on_inner_edge(11)
            ball.rect.centerx = random.randint(initial_bat.rect.left + ball.rect.width,
                                               initial_bat.rect.right - ball.rect.width)
        else:
            ball.rect.centerx = initial_bat.get_pos_on_inner_edge(11)
            ball.rect.centery = random.randint(initial_bat.rect.top + ball.rect.height,
                                               initial_bat.rect.bottom - ball.rect.height)

        ball.follow = initial_bat
        ball.direction = pg.math.Vector2(250 - ball.rect.centerx, 250 - ball.rect.centery)
        ball.direction.normalize_ip()
        ball.direction.rotate(initial_bat.get_collision_angle(ball.rect.center))

    collided_bats = pg.sprite.spritecollide(ball, bat_sprites, False)
    if collided_bats:
        screen.fill(GREEN, (495, 495, 5, 5))
        bat = collided_bats[0]
        angle = bat.get_collision_angle(ball.rect.center)
        ball.direction.reflect_ip(bat.normal)
        ball.direction.rotate_ip(angle)
        if isinstance(bat, HorizontalBat):
            ball.rect.centery = bat.get_pos_on_inner_edge(12)
        else:
            ball.rect.centerx = bat.get_pos_on_inner_edge(12)
        ball.set_pos(ball.rect.center)

    bat_sprites.draw(screen)
    ball_sprites.draw(screen)

    if DEBUG:
        src = ball.rect.center
        dst = pg.math.Vector2(ball.direction)
        dst.scale_to_length(100)
        dst += pg.math.Vector2(src)
        pg.draw.line(screen, GREEN, src, dst.xy)

    clock.tick(60)
    pg.display.flip()
