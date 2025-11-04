# Toon Dash: simple football endless runner built with PyGame
# You play as a Toon dodging red cards and hitting trophies for points

import pygame, random, sys
pygame.init()

# Window setup and game clock
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Toon Dash")
clock = pygame.time.Clock()

# Basic colours for pitch, text + game elements
GREEN1 = (15, 110, 15)
GREEN2 = (25, 140, 25)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (210, 40, 40)
GOLD   = (255, 215, 60)

# Fonts for menus, HUD + banners
font    = pygame.font.SysFont("arial", 26, True)
bigfont = pygame.font.SysFont("arial", 50, True)
midfont = pygame.font.SysFont("arial", 32, True)

# Main game state and stats
# 'state' just switches between title, play & game over
state = "title"     # title -> play -> gameover
score = 0
best_score = 0
lives = 3
speed = 5
paused = False
toon_mode = False
shake_timer = 0
invincible_timer = 0
streak = 0

# Player is just rectangle, same with hazards & collectibles
# Lists keep track of everything on screen
player = pygame.Rect(80, HEIGHT // 2 - 20, 40, 40)
hazards = []
collectibles = []
particles = []
stars = []

# Simple frame counters to trigger spawns & banner text
spawn_timer = 0
collect_timer = 0
star_timer = 0
banner_timer = 0
banner_text = ""

# Draws the football pitch pattern with stripes and lines
def draw_pitch():
    stripe = 40
    for y in range(0, HEIGHT, stripe * 2):
        pygame.draw.rect(screen, GREEN1, (0, y, WIDTH, stripe))
        pygame.draw.rect(screen, GREEN2, (0, y + stripe, WIDTH, stripe))
    for y in range(60, HEIGHT, 60):
        pygame.draw.line(screen, (255, 255, 255), (0, y), (WIDTH, y), 1)

# Resets everything when starting or restarting a game
def reset_run():
    global score, lives, speed, toon_mode, streak
    global hazards, collectibles, particles, stars
    global invincible_timer, shake_timer, banner_timer, banner_text
    score = 0
    lives = 3
    speed = 5
    toon_mode = False
    streak = 0
    hazards.clear()
    collectibles.clear()
    particles.clear()
    stars.clear()
    invincible_timer = 0
    shake_timer = 0
    banner_timer = 0
    banner_text = ""
    player.x = 80
    player.y = HEIGHT // 2 - 20

# Makes small bursts of dots when collecting or getting hit
def make_particles(x, y, colour):
    for _ in range(10):
        particles.append([x, y, random.randint(-3, 3), random.randint(-3, 3), random.randint(10, 30), colour])

# Spawns a red hazard somewhere on the right side
def spawn_hazard():
    if random.random() < 0.25:
        w = random.randint(60, 110)
        h = random.randint(18, 26)
    else:
        w = h = random.randint(25, 40)
    hazards.append(pygame.Rect(WIDTH, random.randint(40, HEIGHT - 40), w, h))

# Spawns a gold trophy somewhere random
def spawn_collectible():
    s = 26
    collectibles.append(pygame.Rect(WIDTH, random.randint(40, HEIGHT - 40), s, s))

# Spawns tiny white dots in the background for motion
def spawn_star():
    stars.append([WIDTH, random.randint(0, HEIGHT), random.randint(2, 5)])

# Quick text banners “Speed Up!” or “Streak +1!”
def set_banner(text, frames=120):
    global banner_text, banner_timer
    banner_text = text
    banner_timer = frames

# Runs when you get hit by a red hazard
# Takes a life, flashes white, shakes screen, ends game if out of lives
def hit_player():
    global lives, invincible_timer, shake_timer, streak, state, best_score
    if invincible_timer > 0:
        return
    lives -= 1
    streak = 0
    invincible_timer = 90
    shake_timer = 12
    make_particles(player.centerx, player.centery, RED)
    if lives <= 0:
        if score > best_score:
            best_score = score
        state = "gameover"

# Runs when you get trophy
# Adds points, speed & shows banners based on streaks
def collect_item():
    global score, speed, streak
    score += 1
    streak += 1
    make_particles(player.centerx, player.centery, GOLD)
    if score % 5 == 0:
        speed += 1
        set_banner(f"Speed Up! {speed}")
    if streak % 5 == 0 and streak > 0:
        score += 1
        set_banner(f"Streak +1! ({streak})")
    if score % 10 == 0 and score > 0:
        set_banner(f"Milestone: {score}!")

# Turns on Toon Mode after 15 points, gives extra life & changes visuals
def maybe_unlock_toon_mode():
    global toon_mode, lives, speed
    if (not toon_mode) and score >= 15:
        toon_mode = True
        lives += 1
        speed += 2
        set_banner("TOON MODE UNLOCKED! +1 Life")

# Title screen with controls and best score
def draw_title():
    screen.fill(GREEN2)
    draw_pitch()
    t = bigfont.render("TOON DASH", True, WHITE)
    s = midfont.render("Press SPACE to Start", True, GOLD)
    h = font.render("↑ ↓ move • Dodge red • Collect gold • P = Pause", True, WHITE)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 30))
    if best_score > 0:
        b = font.render(f"Best Score: {best_score}", True, WHITE)
        screen.blit(b, (WIDTH // 2 - b.get_width() // 2, HEIGHT // 2 + 70))

# Game over screen shows final + best score
def draw_gameover():
    screen.fill(GREEN2)
    draw_pitch()
    a = bigfont.render("GAME OVER", True, RED)
    s1 = midfont.render(f"Score: {score}", True, WHITE)
    s2 = midfont.render(f"Best: {best_score}", True, GOLD)
    tip = font.render("Press SPACE to Restart", True, WHITE)
    screen.blit(a, (WIDTH // 2 - a.get_width() // 2, HEIGHT // 2 - 110))
    screen.blit(s1, (WIDTH // 2 - s1.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(s2, (WIDTH // 2 - s2.get_width() // 2, HEIGHT // 2 + 5))
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 + 60))

# Main game loop, repeats 60 times per second
while True:
    clock.tick(60)

    #  Check key presses and quit events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if state == "title" and e.key == pygame.K_SPACE:
                reset_run()
                state = "play"
            elif state == "gameover" and e.key == pygame.K_SPACE:
                reset_run()
                state = "play"
            elif state == "play" and e.key == pygame.K_p:
                paused = not paused

    # If on title or game over screen, just draw those and skip gameplay
    if state == "title":
        draw_title()
        pygame.display.flip()
        continue
    if state == "gameover":
        draw_gameover()
        pygame.display.flip()
        continue

    # Clear screen and redraw the pitch every frame
    screen.fill(GREEN1)
    draw_pitch()

    # Player movement – up/down arrows, stays inside the window
    if not paused:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.y -= 6
        if keys[pygame.K_DOWN]:
            player.y += 6
        player.clamp_ip(screen.get_rect())

    # Stars
    if not paused:
        star_timer += 1
        if star_timer > 15:
            spawn_star()
            star_timer = 0
    for s in stars[:]:
        s[0] -= s[2]
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), 1)
        if s[0] < 0:
            stars.remove(s)

    # Spawn hazards and collectibles based on timers
    if not paused:
        spawn_timer += 1
        collect_timer += 1
        if spawn_timer > 55:
            spawn_hazard()
            spawn_timer = 0
        if collect_timer > 120:
            spawn_collectible()
            collect_timer = 0

    # Move red cards left, remove old ones & check for collision
    for h in hazards[:]:
        if not paused:
            h.x -= speed
        if h.right < 0:
            hazards.remove(h)
        elif player.colliderect(h) and invincible_timer == 0:
            hazards.remove(h)
            hit_player()

    # Move gold trophies and check when player collects them
    for c in collectibles[:]:
        if not paused:
            c.x -= speed
        if c.right < 0:
            collectibles.remove(c)
        elif player.colliderect(c):
            collectibles.remove(c)
            collect_item()
            maybe_unlock_toon_mode()

    # Toon Mode visual
    if toon_mode:
        for i in range(0, WIDTH, 80):
            pygame.draw.rect(screen, WHITE, (i, 0, 40, HEIGHT))
            pygame.draw.rect(screen, BLACK, (i + 40, 0, 40, HEIGHT))

    # Particles
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1
        pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), 3)
        if p[4] <= 0:
            particles.remove(p)

    # Count down timers for invincibility, screen shake and banners
    if invincible_timer > 0:
        invincible_timer -= 1
    if shake_timer > 0:
        shake_timer -= 1
    if banner_timer > 0:
        banner_timer -= 1

    # Adds small shake to screen when hit
    ox = random.randint(-2, 2) if shake_timer > 0 else 0
    oy = random.randint(-2, 2) if shake_timer > 0 else 0

    # Draw player (flashes when invincible)
    if invincible_timer % 6 < 3:
        pygame.draw.rect(screen, WHITE, (player.x + ox, player.y + oy, player.w, player.h))
        pygame.draw.rect(screen, BLACK, (player.x + ox, player.y + oy, player.w // 2, player.h))

    # Draw red cards and gold trophies
    for h in hazards:
        pygame.draw.rect(screen, RED, (h.x + ox, h.y + oy, h.w, h.h))
        pygame.draw.line(screen, BLACK, (h.x + ox, h.y + oy), (h.right + ox, h.bottom + oy), 2)
    for c in collectibles:
        pygame.draw.rect(screen, GOLD, (c.x + ox, c.y + oy, c.w, c.h))
        pygame.draw.line(screen, BLACK, (c.x + ox, c.bottom + oy), (c.right + ox, c.y + oy), 2)

    # HUD, draw score, lives and speed text on top
    hud = font.render(f"Score: {score}   Lives: {lives}   Speed: {speed}", True, WHITE)
    screen.blit(hud, (20, 10))
    if toon_mode:
        tm = font.render("TOON MODE!", True, GOLD)
        screen.blit(tm, (WIDTH // 2 - tm.get_width() // 2, 10))
    if paused:
        pz = bigfont.render("PAUSED", True, GOLD)
        screen.blit(pz, (WIDTH // 2 - pz.get_width() // 2, HEIGHT // 2 - 40))

    # Show any active banner message on screen
    if banner_timer > 0 and banner_text:
        b = midfont.render(banner_text, True, WHITE)
        bg = pygame.Surface((b.get_width() + 24, b.get_height() + 10))
        bg.set_alpha(170)
        bg.fill(BLACK)
        screen.blit(bg, (WIDTH // 2 - bg.get_width() // 2, 60))
        screen.blit(b, (WIDTH // 2 - b.get_width() // 2, 65))

    # Game over
    if state == "play" and lives <= 0:
        state = "gameover"

    pygame.display.flip()