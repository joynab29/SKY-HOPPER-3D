from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random
import time


# =========================================================
# ---------------- Game State -----------------------------
# =========================================================
GAME_DURATION = 120.0  # 2 minutes
MAX_LIVES = 3
game_won = False
paused = False

game_over = False
lives = MAX_LIVES

start_time = time.time()
elapsed_time = 0.0

# dt / timing
last_frame_time = time.time()
FPS_BASE = 60.0  # used for "frame-like" values such as run ramp


# ---------------- Camera-related ----------------
cam_x = 0
cam_y = 300
cam_z = 100
camera_pos = (cam_x, cam_y, cam_z)
fovY = 90
near = 0.1
far = 1400
CAMERA_FOLLOW_OFFSET_Y = 300

# camera controls
camera_angle = 0.0
camera_radius = 200
min_angle = -70
max_angle = 70


# =========================================================
# ---------------- First Person POV ------------------------
# =========================================================
first_person = False
fp_camera_pos = camera_pos  # updated each frame when FP is active


# =========================================================
# ---------------- COIN + GEM SYSTEM ----------------------
# =========================================================
score = 0

coins = []   # fixed platforms only -> score
gems = []    # moving + blinking platforms -> lives

COIN_SPAWN_CHANCE = 0.70
GEM_SPAWN_CHANCE = 0.85

# Coins: upright, flat filled discs, bobbing vertically, face toward camera
COIN_RADIUS = 18
COIN_THICKNESS = 2.5
COIN_FLOAT_AMPL = 10.0
COIN_FLOAT_SPEED = 2.8
COIN_BASE_Z_OFFSET = 22.0

# Pickup radius
PICKUP_DIST = 35

coin_quadric = None


# =========================================================
# ---------------- ASTEROIDS SYSTEM -----------------------
# =========================================================
asteroids = []
ASTEROID_MAX = 5

ASTEROID_RADIUS_MIN = 12.0
ASTEROID_RADIUS_MAX = 28.0

ASTEROID_SPEED = 520.0  # units/sec, moving from door (far -Y) toward start (+Y)

ASTEROID_SPAWN_MIN = 0.45
ASTEROID_SPAWN_MAX = 1.15

next_asteroid_spawn_time = 0.0

PLAYER_COLLISION_RADIUS = 28.0  # tweak if needed (bigger = easier hit)

asteroid_quadric = None


# ---------------- Player position ----------------
player_x = 0.0
player_y = 430.0
player_z = -190.0  # top of grey platform is -200 + 10

# SAME forward offset (toward green platforms)
PLAYER_OFFSET_Y = -165.0

# start facing toward green platforms (negative Y)
player_dir = 180.0

# angular speed (deg/sec)
turn_speed_deg_per_sec = 160.0

# move speed (slightly reduced)
player_speed = 260.0


# ---------------- Run + Air control tuning ----------------
RUN_MAX_MULT = 2.3
RUN_RAMP_FRAMES = 40
AIR_CONTROL_MULT = 1.6
run_charge = 0.0  # float (frame-units)


# ---------------- Jump & Gravity ----------------
player_vz = 0.0
gravity = -1200.0          # units/sec^2
jump_strength = 620.0      # units/sec
is_on_ground = True

# Double jump
MAX_JUMPS = 2
jumps_left = MAX_JUMPS

# Air momentum
jump_vx = 0.0
jump_vy = 0.0
JUMP_MOMENTUM_FACTOR = 0.75

# respawn (start) position
start_x = 0.0
start_y = 430.0
start_z = -190.0

# last safe checkpoint (updates when LAND)
last_safe_x = start_x
last_safe_y = start_y
last_safe_z = start_z

# Track which platform we are standing on (for moving platforms)
ground_platform = None

# Continuous key holding
keys_down = set()

# To detect "tap" of space
space_was_down = False


# ---------------- Platforms ----------------
platforms = []
first_platform_y = 430
first_platform_half = 230
platform_z = -190
platform_height = 10
platform_width = 180
platform_depth = 180
green_platform_half = platform_depth / 2
num_platforms = 15
initial_gap = 80
platform_gap = 80

max_jump_x = 200
screen_x_min = -350
screen_x_max = 350

# platform motion speed (units/sec)
PLATFORM_SPEED = 90.0


# =========================================================
# ---------------- Stars (Night) --------------------------
# =========================================================
STAR_COUNT = 180
stars = []

def generate_stars():
    global stars
    stars.clear()
    for _ in range(STAR_COUNT):
        x = random.uniform(-1800, 1800)
        y = random.uniform(-1800, 1800)
        z = random.uniform(-1300, -900)  # far behind
        size = random.uniform(2.0, 4.5)
        stars.append((x, y, z, size))

generate_stars()


# =========================================================
# ---------------- Helpers -------------------------------
# =========================================================
def clamp01(v):
    return max(0.0, min(1.0, v))

def lerp(a, b, t):
    return a * (1.0 - t) + b * t

def mix_color(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))

def get_time_t():
    return clamp01(elapsed_time / GAME_DURATION)

def get_night_factor():
    t = get_time_t()
    return clamp01((t - 0.6) / 0.4)

def get_fog_factor():
    n = get_night_factor()
    return n * 0.65

# REAL world position used for collision/render
def player_world_pos():
    return player_x, (player_y + PLAYER_OFFSET_Y), player_z


# =========================================================
# ---------------- UI / TEXT ------------------------------
# =========================================================
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# =========================================================
# ---------------- Restart -------------------------------
# =========================================================
def restart_game():
    global game_over, lives, start_time, elapsed_time, last_frame_time
    global player_x, player_y, player_z, player_vz, is_on_ground
    global run_charge, ground_platform, jumps_left
    global jump_vx, jump_vy, space_was_down, keys_down
    global last_safe_x, last_safe_y, last_safe_z
    global player_dir
    global camera_pos, camera_angle, camera_radius
    global score, coins, gems
    global first_person, fp_camera_pos
    global game_won
    global asteroids, next_asteroid_spawn_time

    game_won = False
    game_over = False
    lives = MAX_LIVES

    score = 0
    coins.clear()
    gems.clear()

    asteroids.clear()
    next_asteroid_spawn_time = time.time() + 1.0

    first_person = False
    fp_camera_pos = camera_pos

    start_time = time.time()
    elapsed_time = 0.0
    last_frame_time = time.time()

    player_x, player_y, player_z = start_x, start_y, start_z
    player_vz = 0.0
    is_on_ground = True
    player_dir = 180.0

    run_charge = 0.0
    ground_platform = None
    jumps_left = MAX_JUMPS
    jump_vx = 0.0
    jump_vy = 0.0
    space_was_down = False
    keys_down.clear()

    last_safe_x, last_safe_y, last_safe_z = start_x, start_y, start_z

    camera_angle = 0.0
    camera_radius = 200
    camera_pos = (0, 300, 100)

    generate_platforms()


# =========================================================
# ---------------- Platforms ------------------------------
# =========================================================
def first_platform():
    fog = get_fog_factor()
    fog_color = (0.15, 0.17, 0.22)

    glPushMatrix()
    glTranslatef(0, 430, -200)

    platform_half = 230
    height = 10

    top_col = mix_color((0.522, 0.514, 0.510), fog_color, fog)
    down_col = mix_color((0.380, 0.380, 0.380), fog_color, fog)

    glColor3f(*top_col)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half, height)
    glVertex3f(platform_half, -platform_half, height)
    glVertex3f(platform_half, platform_half, height)
    glVertex3f(-platform_half, platform_half, height)
    glEnd()

    glColor3f(*down_col)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half, height)
    glVertex3f(platform_half, -platform_half, height)
    glVertex3f(platform_half, -platform_half, 0)
    glVertex3f(-platform_half, -platform_half, 0)
    glEnd()

    glPopMatrix()


# =======================
# COIN/GEM SPAWN + UPDATE
# =======================
def spawn_collectibles():
    global coins, gems
    coins.clear()
    gems.clear()

    for p in platforms:
        if p["type"] == "fixed":
            if random.random() > COIN_SPAWN_CHANCE:
                continue
            ox = random.uniform(-p["width"] * 0.25, p["width"] * 0.25)
            oy = random.uniform(-p["depth"] * 0.25, p["depth"] * 0.25)
            coins.append({
                "platform": p,
                "offset_x": ox,
                "offset_y": oy,
                "x": p["x"] + ox,
                "y": p["y"] + oy,
                "z_base": p["z"] + platform_height + COIN_BASE_Z_OFFSET,
                "collected": False
            })

        elif p["type"] in ("moving", "blinking"):
            if random.random() > GEM_SPAWN_CHANCE:
                continue
            ox = random.uniform(-p["width"] * 0.20, p["width"] * 0.20)
            oy = random.uniform(-p["depth"] * 0.20, p["depth"] * 0.20)
            gems.append({
                "platform": p,
                "offset_x": ox,
                "offset_y": oy,
                "x": p["x"] + ox,
                "y": p["y"] + oy,
                "z": p["z"] + platform_height + 18,
                "collected": False
            })


def update_collectibles():
    for c in coins:
        if c["collected"]:
            continue
        p = c["platform"]
        c["x"] = p["x"] + c["offset_x"]
        c["y"] = p["y"] + c["offset_y"]
        c["z_base"] = p["z"] + platform_height + COIN_BASE_Z_OFFSET

    for g in gems:
        if g["collected"]:
            continue
        p = g["platform"]
        g["x"] = p["x"] + g["offset_x"]
        g["y"] = p["y"] + g["offset_y"]
        g["z"] = p["z"] + platform_height + 18


def generate_platforms():
    global platforms
    platforms.clear()

    prev_x = 0
    current_y = (first_platform_y - first_platform_half - initial_gap - green_platform_half)
    prev_type = None

    for _ in range(num_platforms):
        dx = random.uniform(-max_jump_x, max_jump_x)
        x = max(screen_x_min, min(screen_x_max, prev_x + dx))

        r = random.random()

        # prevent consecutive blinking platforms
        if prev_type == "blinking":
            p_type = "fixed" if r < 0.6 else "moving"
        else:
            if r < 0.7:
                p_type = "fixed"
            elif r < 0.85:
                p_type = "moving"
            else:
                p_type = "blinking"

        platform = {
            "x": x,
            "y": current_y,
            "z": platform_z,
            "width": platform_width,
            "depth": platform_depth,
            "type": p_type,
            "visible": True,
            "direction": 1,
            "last_toggle": time.time(),
            "dx": 0.0
        }

        platforms.append(platform)
        prev_x = x
        current_y -= (platform_depth + platform_gap)
        prev_type = p_type

    spawn_collectibles()


def draw_platform(p):
    if p["type"] == "blinking" and not p["visible"]:
        return

    fog = get_fog_factor()
    fog_color = (0.15, 0.17, 0.22)

    top_base = (0.290, 0.627, 0.275)
    side_base = (0.627, 0.451, 0.275)

    top_col = mix_color(top_base, fog_color, fog)
    side_col = mix_color(side_base, fog_color, fog)

    glPushMatrix()
    glTranslatef(p["x"], p["y"], p["z"])
    w = p["width"] / 2
    d = p["depth"] / 2
    h = platform_height

    glColor3f(*top_col)
    glBegin(GL_QUADS)
    glVertex3f(-w, -d, h)
    glVertex3f(w, -d, h)
    glVertex3f(w, d, h)
    glVertex3f(-w, d, h)
    glEnd()

    glColor3f(*side_col)
    glBegin(GL_QUADS)
    glVertex3f(-w, d, h)
    glVertex3f(w, d, h)
    glVertex3f(w, d, 0)
    glVertex3f(-w, d, 0)

    glVertex3f(w, -d, h)
    glVertex3f(w, d, h)
    glVertex3f(w, d, 0)
    glVertex3f(w, -d, 0)
    glEnd()

    glPopMatrix()


def draw_all_platforms():
    for p in platforms:
        draw_platform(p)


def update_platforms(dt):
    if game_over:
        return

    now = time.time()

    for p in platforms:
        p["dx"] = 0.0

        if p["type"] == "moving":
            old_x = p["x"]
            p["x"] += p["direction"] * PLATFORM_SPEED * dt
            if p["x"] > screen_x_max or p["x"] < screen_x_min:
                p["direction"] *= -1
            p["dx"] = p["x"] - old_x

        if p["type"] == "blinking":
            if now - p["last_toggle"] >= 1.0:
                p["visible"] = not p["visible"]
                p["last_toggle"] = now


def check_platform_collision(px, py, pz):
    # grey first platform
    if abs(px) <= 230 and abs(py - 430) <= 230:
        if pz <= -190:
            return -190, None

    for p in platforms:
        if p["type"] == "blinking" and not p["visible"]:
            continue
        if abs(px - p["x"]) <= p["width"] / 2 and abs(py - p["y"]) <= p["depth"] / 2:
            if pz <= p["z"]:
                return p["z"], p

    return None, None


def draw_door_on_platform(p):
    glPushMatrix()
    glTranslatef(p["x"], p["y"], p["z"] + platform_height)

    door_width = 40
    door_height = 70
    door_depth = 5
    w = door_width / 2

    glColor3f(0.55, 0.27, 0.07)
    glBegin(GL_QUADS)
    glVertex3f(-w, 0, 0)
    glVertex3f(w, 0, 0)
    glVertex3f(w, 0, door_height)
    glVertex3f(-w, 0, door_height)
    glEnd()

    glColor3f(0.45, 0.20, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(w, 0, 0)
    glVertex3f(w + door_depth, 0, 0)
    glVertex3f(w + door_depth, 0, door_height)
    glVertex3f(w, 0, door_height)
    glEnd()

    glColor3f(1.0, 0.85, 0.0)
    glPointSize(6)
    glBegin(GL_POINTS)
    glVertex3f(w - 5, 0, door_height / 2)
    glEnd()

    glPopMatrix()


# =========================================================
# ---------------- Collectibles Render + Pickup ------------
# =========================================================
def draw_coin(c):
    global coin_quadric
    if coin_quadric is None:
        coin_quadric = gluNewQuadric()
        gluQuadricNormals(coin_quadric, GLU_SMOOTH)

    # bobbing
    t = time.time() * COIN_FLOAT_SPEED
    bob = math.sin(t + (c["x"] * 0.01) + (c["y"] * 0.01)) * COIN_FLOAT_AMPL
    z = c["z_base"] + bob

    # billboard towards active camera (FP or TP)
    camx, camy, _ = (fp_camera_pos if first_person else camera_pos)
    vx = camx - c["x"]
    vy = camy - c["y"]
    angle_z = math.degrees(math.atan2(vx, vy))

    glPushMatrix()
    glTranslatef(c["x"], c["y"], z)

    # make disk upright (XY -> XZ)
    glRotatef(90, 1, 0, 0)
    # rotate so coin face points camera
    glRotatef(angle_z, 0, 0, 1)

    glColor3f(0.95, 0.80, 0.10)
    gluDisk(coin_quadric, 0.0, COIN_RADIUS, 48, 1)  # filled front
    gluCylinder(coin_quadric, COIN_RADIUS, COIN_RADIUS, COIN_THICKNESS, 48, 1)
    glTranslatef(0, 0, COIN_THICKNESS)
    gluDisk(coin_quadric, 0.0, COIN_RADIUS, 48, 1)  # filled back

    glPopMatrix()


gem_quadric = None
def draw_gem(g):
    # low-poly crystal using fewer slices/stacks (no spin)
    global gem_quadric
    if gem_quadric is None:
        gem_quadric = gluNewQuadric()
        gluQuadricNormals(gem_quadric, GLU_SMOOTH)

    glPushMatrix()
    glTranslatef(g["x"], g["y"], g["z"])

    glColor3f(0.20, 0.90, 1.00)

    radius = 10.0
    height = 28.0
    tip_h = 12.0

    slices = 10
    stacks = 2

    # main body cylinder
    gluCylinder(gem_quadric, radius, radius, height, slices, stacks)

    # top cone
    glPushMatrix()
    glTranslatef(0, 0, height)
    gluCylinder(gem_quadric, radius, 0.0, tip_h, slices, stacks)
    glPopMatrix()

    # bottom cone
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluCylinder(gem_quadric, radius, 0.0, tip_h * 0.75, slices, stacks)
    glPopMatrix()

    glPopMatrix()


def draw_collectibles():
    for c in coins:
        if not c["collected"]:
            draw_coin(c)

    for g in gems:
        if g["collected"]:
            continue
        p = g["platform"]
        if p["type"] == "blinking" and not p["visible"]:
            continue
        draw_gem(g)


def check_collectibles_pickup():
    global score, lives

    px, py, pz = player_world_pos()

    # coins -> score
    for c in coins:
        if c["collected"]:
            continue
        dx = px - c["x"]
        dy = py - c["y"]
        if (dx * dx + dy * dy) <= (PICKUP_DIST * PICKUP_DIST) and abs(pz - c["z_base"]) < 150:
            c["collected"] = True
            score += 1

    # gems -> lives (capped)
    for g in gems:
        if g["collected"]:
            continue
        p = g["platform"]
        if p["type"] == "blinking" and not p["visible"]:
            continue
        dx = px - g["x"]
        dy = py - g["y"]
        if (dx * dx + dy * dy) <= (PICKUP_DIST * PICKUP_DIST) and abs(pz - g["z"]) < 110:
            g["collected"] = True
            lives = min(MAX_LIVES, lives + 1)


# =========================================================
# ---------------- Asteroids (Spawn/Update/Draw/Hit) -------
# =========================================================
def door_spawn_position():
    """
    Spawn line is at the door platform location.
    Returns (x_center, y_line, z_base)
    """
    if not platforms:
        return 0.0, -1200.0, -170.0
    p = platforms[-1]
    return p["x"], p["y"], p["z"] + platform_height + 30.0


def maybe_spawn_asteroid():
    global next_asteroid_spawn_time

    if game_over or game_won:
        return

    if len(asteroids) >= ASTEROID_MAX:
        return

    now = time.time()
    if now < next_asteroid_spawn_time:
        return

    sx, sy, sz = door_spawn_position()

    # width = whole screen (playable width)
    x = random.uniform(screen_x_min, screen_x_max)

    # slight random height spread (still coming “straight” in Y)
    z = sz + random.uniform(-40.0, 60.0)

    r = random.uniform(ASTEROID_RADIUS_MIN, ASTEROID_RADIUS_MAX)

    asteroids.append({"x": x, "y": sy, "z": z, "r": r, "dead": False})

    next_asteroid_spawn_time = now + random.uniform(ASTEROID_SPAWN_MIN, ASTEROID_SPAWN_MAX)


def update_asteroids(dt):
    """
    Move asteroids from door (far negative Y) toward start platform (+Y).
    If they pass the start platform area without hitting, remove them (player survives).
    """
    if game_over or game_won:
        return

    # spawn new ones
    maybe_spawn_asteroid()

    # move
    for a in asteroids:
        if a.get("dead", False):
            continue
        a["y"] += ASTEROID_SPEED * dt  # toward +Y

    # remove asteroids that passed the start platform area
    # (grey platform center y=430; we remove once it passes a bit beyond)
    PASS_Y = 650.0
    asteroids[:] = [a for a in asteroids if (not a.get("dead", False)) and (a["y"] <= PASS_Y)]


def check_asteroid_collisions():
    global lives, game_over

    if game_over or game_won:
        return

    px, py, pz = player_world_pos()

    for a in asteroids:
        if a.get("dead", False):
            continue

        dx = px - a["x"]
        dy = py - a["y"]
        dz = pz - a["z"]

        hit_dist = a["r"] + PLAYER_COLLISION_RADIUS
        if (dx*dx + dy*dy + dz*dz) <= (hit_dist * hit_dist):
            lives -= 1
            a["dead"] = True  # prevent multiple hits same asteroid

            if lives <= 0:
                game_over = True
            return

    # clean dead ones
    asteroids[:] = [a for a in asteroids if not a.get("dead", False)]


def draw_asteroids():
    global asteroid_quadric
    if asteroid_quadric is None:
        asteroid_quadric = gluNewQuadric()
        gluQuadricNormals(asteroid_quadric, GLU_SMOOTH)

    for a in asteroids:
        glPushMatrix()
        glTranslatef(a["x"], a["y"], a["z"])
        glColor3f(0.18, 0.18, 0.18)
        gluSphere(asteroid_quadric, a["r"], 14, 14)
        glPopMatrix()


# =========================================================
# ---------------- Player (Mario) -------------------------
# =========================================================
def draw_player():
    fog = get_fog_factor()
    fog_color = (0.15, 0.17, 0.22)

    def C(c):
        return mix_color(c, fog_color, fog)

    px, py, pz = player_world_pos()

    glPushMatrix()
    glTranslatef(px, py, pz + 1.0)
    glRotatef(player_dir, 0, 0, 1)
    glScalef(0.35, 0.35, 0.35)

    glColor3f(*C((0.25, 0.12, 0.05)))
    glPushMatrix()
    glTranslatef(-45, 0, 10)
    glScalef(70, 40, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(45, 0, 10)
    glScalef(70, 40, 20)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.20, 0.55, 0.95)))
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glScalef(140, 60, 60)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.90, 0.15, 0.12)))
    glPushMatrix()
    glTranslatef(0, 0, 110)
    glScalef(140, 70, 90)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.20, 0.55, 0.95)))
    glPushMatrix()
    glTranslatef(0, 0, 125)
    glScalef(180, 80, 70)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.20, 0.55, 0.95)))
    glPushMatrix()
    glTranslatef(-120, 0, 120)
    glScalef(80, 40, 40)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(120, 0, 120)
    glScalef(80, 40, 40)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.95, 0.70, 0.50)))
    glPushMatrix()
    glTranslatef(-150, 0, 105)
    glScalef(40, 35, 25)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(150, 0, 105)
    glScalef(40, 35, 25)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((1.0, 0.95, 0.2)))
    glPushMatrix()
    glTranslatef(-40, 36, 120)
    glScalef(25, 5, 25)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40, 36, 120)
    glScalef(25, 5, 25)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.95, 0.70, 0.50)))
    glPushMatrix()
    glTranslatef(0, 0, 195)
    glScalef(120, 80, 90)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.95, 0.70, 0.50)))
    glPushMatrix()
    glTranslatef(60, 0, 195)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 25, 16, 4)
    glPopMatrix()

    glColor3f(*C((0.20, 0.10, 0.05)))
    glPushMatrix()
    glTranslatef(-35, 35, 215)
    glScalef(70, 30, 25)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.15, 0.08, 0.03)))
    glPushMatrix()
    glTranslatef(35, 30, 175)
    glScalef(60, 8, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(40, 40, 205)
    glColor3f(*C((1, 1, 1)))
    gluSphere(gluNewQuadric(), 18, 16, 16)
    glTranslatef(8, 8, 0)
    glColor3f(*C((0.1, 0.1, 0.1)))
    gluSphere(gluNewQuadric(), 8, 16, 16)
    glPopMatrix()

    glColor3f(*C((0.20, 0.55, 0.95)))
    glPushMatrix()
    glTranslatef(0, 0, 245)
    glScalef(160, 110, 20)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, 270)
    glScalef(120, 80, 50)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


# =========================================================
# ---------------- Sky + Stars ----------------------------
# =========================================================
def draw_sky_gradient():
    t = get_time_t()

    r_bottom = 0.7 * (1 - t) + 0.02 * t
    g_bottom = 0.9 * (1 - t) + 0.03 * t
    b_bottom = 1.0 * (1 - t) + 0.20 * t

    r_top = 0.2 * (1 - t) + 0.01 * t
    g_top = 0.5 * (1 - t) + 0.02 * t
    b_top = 0.9 * (1 - t) + 0.12 * t

    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(r_bottom, g_bottom, b_bottom)
    glVertex3f(-2000, -2000, -1200)
    glVertex3f(2000, -2000, -1200)

    glColor3f(r_top, g_top, b_top)
    glVertex3f(2000, 2000, -1200)
    glVertex3f(-2000, 2000, -1200)
    glEnd()

    glPopMatrix()


def draw_stars():
    night = get_night_factor()
    if night <= 0.01:
        return

    brightness = 0.25 + 0.75 * night

    for (x, y, z, size) in stars:
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(brightness, brightness, brightness)
        gluSphere(gluNewQuadric(), size, 8, 8)
        glPopMatrix()


# =========================================================
# ---------------- Camera / Input -------------------------
# =========================================================
def specialKeyListener(key, x, y):
    global camera_angle, camera_pos
    if game_over:
        return

    # lock 3rd-person controls in first-person
    if first_person:
        return

    cx, cy, cz = camera_pos

    if key == GLUT_KEY_LEFT:
        camera_angle -= 2
        camera_angle = max(min_angle, camera_angle)

    if key == GLUT_KEY_RIGHT:
        camera_angle += 2
        camera_angle = min(max_angle, camera_angle)

    if key == GLUT_KEY_UP:
        cy -= 5
    if key == GLUT_KEY_DOWN:
        cy += 5

    r = math.radians(camera_angle)
    cx = camera_radius * math.sin(r)
    camera_pos = (cx, cy, cz)


def mouseListener(button, state, x, y):
    global first_person
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person


def setupCamera():
    global fp_camera_pos

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, near, far)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        px, py, pz = player_world_pos()

        ang = math.radians(player_dir)
        forward_x = -math.sin(ang)
        forward_y = math.cos(ang)

        head_height = 85.0
        eye_x = px + forward_x * 12.0
        eye_y = py + forward_y * 12.0
        eye_z = pz + head_height

        look_dist = 220.0
        look_x = eye_x + forward_x * look_dist
        look_y = eye_y + forward_y * look_dist
        look_z = eye_z - 60.0

        fp_camera_pos = (eye_x, eye_y, eye_z)

        gluLookAt(
            eye_x, eye_y, eye_z,
            look_x, look_y, look_z,
            0, 0, 1
        )
    else:
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, y - 300, -200, 0, 0, 1)


def keyboardDown(key, x, y):
    global game_over
    if game_over:
        if key == b'r' or key == b'R':
            restart_game()
        return
    keys_down.add(key)


def keyboardUp(key, x, y):
    if game_over:
        return
    if key in keys_down:
        keys_down.remove(key)


def draw_pause_icon():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 1.0, 0.0)

    if not paused:
        glBegin(GL_QUADS)
        glVertex2f(938, 655); glVertex2f(944, 655); glVertex2f(944, 685); glVertex2f(938, 685)
        glVertex2f(956, 655); glVertex2f(962, 655); glVertex2f(962, 685); glVertex2f(956, 685)
        glEnd()
    else:
        glBegin(GL_TRIANGLES)
        glVertex2f(942, 655); glVertex2f(942, 685); glVertex2f(970, 670)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# =========================================================
# ---------------- Main Update Loop -----------------------
# =========================================================
def idle():
    global player_x, player_y, player_z, player_vz, is_on_ground
    global run_charge, ground_platform, jumps_left
    global jump_vx, jump_vy, space_was_down
    global lives, game_over, elapsed_time, start_time
    global last_safe_x, last_safe_y, last_safe_z
    global last_frame_time
    global camera_pos
    global game_won

    if game_over:
        glutPostRedisplay()
        return

    now = time.time()
    dt = now - last_frame_time
    last_frame_time = now
    dt = max(0.0, min(dt, 0.05))

    # ---------------- TIMER ----------------
    elapsed_time = now - start_time
    if elapsed_time >= GAME_DURATION:
        elapsed_time = GAME_DURATION
        game_over = True
        glutPostRedisplay()
        return

    # ---------------- PLATFORMS & COLLECTIBLES ----------------
    update_platforms(dt)
    update_collectibles()

    # ---------------- ASTEROIDS ----------------
    update_asteroids(dt)

    # ---------------- DIRECTION VECTORS ----------------
    ang = math.radians(player_dir)
    forward_x = -math.sin(ang)
    forward_y =  math.cos(ang)
    right_x   =  math.cos(ang)
    right_y   =  math.sin(ang)

    # ---------------- RUN LOGIC ----------------
    w_down = (b'w' in keys_down or b'W' in keys_down)
    s_down = (b's' in keys_down or b'S' in keys_down)

    if w_down:
        run_charge = min(RUN_RAMP_FRAMES, run_charge + dt * FPS_BASE)
    else:
        run_charge = max(0.0, run_charge - dt * FPS_BASE * 2.0)

    run_t = run_charge / float(RUN_RAMP_FRAMES)
    run_mult = 1.0 + (RUN_MAX_MULT - 1.0) * run_t

    base_speed = player_speed * run_mult
    steer_speed = base_speed * (AIR_CONTROL_MULT if not is_on_ground else 1.0)

    # ---------------- INPUT ----------------
    move_f = 0.0
    move_s = 0.0

    if w_down: move_f += 1.0
    if s_down: move_f -= 1.0
    if b'a' in keys_down or b'A' in keys_down: move_s -= 1.0
    if b'd' in keys_down or b'D' in keys_down: move_s += 1.0

    # ---------------- APPLY MOVEMENT ----------------
    player_x += (forward_x * move_f + right_x * move_s) * steer_speed * dt
    player_y += (forward_y * move_f + right_y * move_s) * steer_speed * dt

    # ---------------- JUMP ----------------
    space_is_down = (b' ' in keys_down)
    if space_is_down and not space_was_down and jumps_left > 0:
        player_vz = jump_strength
        is_on_ground = False
        jumps_left -= 1
        jump_vx = forward_x * base_speed * move_f
        jump_vy = forward_y * base_speed * move_f

    space_was_down = space_is_down

    # ---------------- AIR MOMENTUM ----------------
    if not is_on_ground:
        player_x += jump_vx * JUMP_MOMENTUM_FACTOR * dt
        player_y += jump_vy * JUMP_MOMENTUM_FACTOR * dt

    # ---------------- GRAVITY ----------------
    player_vz += gravity * dt
    player_z += player_vz * dt

    # ---------------- COLLISION (platform) ----------------
    px, py, pz = player_world_pos()
    top_z, plat = check_platform_collision(px, py, pz)

    if top_z is not None:
        player_z = top_z
        player_vz = 0.0
        is_on_ground = True
        ground_platform = plat
        last_safe_x, last_safe_y, last_safe_z = player_x, player_y, player_z
        jumps_left = MAX_JUMPS
        jump_vx = jump_vy = 0.0
    else:
        is_on_ground = False
        ground_platform = None

    # ---------------- MOVE WITH PLATFORM ----------------
    if is_on_ground and ground_platform and ground_platform["type"] == "moving":
        player_x += ground_platform["dx"]
        last_safe_x += ground_platform["dx"]

    # ---------------- COLLECTIBLES ----------------
    check_collectibles_pickup()

    # ---------------- ASTEROID COLLISION ----------------
    check_asteroid_collisions()

    # ---------------- DOOR WIN CONDITION ----------------
    if platforms:
        final_platform = platforms[-1]
        door_x = final_platform["x"]
        door_y = final_platform["y"]
        door_z = final_platform["z"] + platform_height

        if abs(px - door_x) < 40 and abs(py - door_y) < 40 and abs(pz - door_z) < 70:
            game_over = True
            game_won = True
            glutPostRedisplay()
            return

    # ---------------- FALL / RESPAWN ----------------
    if player_z < -600:
        lives -= 1
        if lives <= 0:
            game_over = True
        else:
            player_x, player_y, player_z = last_safe_x, last_safe_y, last_safe_z
            player_vz = 0.0
            is_on_ground = True
            run_charge = 0.0
            jumps_left = MAX_JUMPS
            jump_vx = jump_vy = 0.0
            space_was_down = False

    # ---------------- WORLD BOUNDS ----------------
    player_x = max(-600, min(600, player_x))
    player_y = max(-5000, min(900, player_y))

    # ---------------- CAMERA FOLLOW ----------------
    if not first_person:
        cx, cy, cz = camera_pos
        world_py = player_y + PLAYER_OFFSET_Y
        target_cy = world_py + CAMERA_FOLLOW_OFFSET_Y

        follow_speed = 6.0
        cy += (target_cy - cy) * follow_speed * dt
        camera_pos = (cx, cy, cz)

    glutPostRedisplay()


# =========================================================
# ---------------- Rendering ------------------------------
# =========================================================
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_sky_gradient()
    draw_stars()

    first_platform()
    draw_all_platforms()
    if platforms:
        draw_door_on_platform(platforms[-1])

    draw_collectibles()
    draw_asteroids()

    # hide mario in first-person (prevents "inside mario" view)
    if not first_person:
        draw_player()

    draw_text(10, 770, f"Lives: {lives}")
    time_left = max(0, int(GAME_DURATION - elapsed_time))
    mm = time_left // 60
    ss = time_left % 60
    draw_text(10, 740, f"Time Left: {mm:02d}:{ss:02d}")
    draw_text(10, 710, f"Score: {score}")
    draw_text(10, 680, f"POV: {'FIRST' if first_person else 'THIRD'}")

    if game_over:
        if game_won:
            draw_text(420, 420, "YOU WIN!")
            draw_text(260, 380, "Congratulations! Press 'R' to Play Again")
        else:
            draw_text(420, 420, "GAME OVER")
            draw_text(300, 380, "Press 'R' to Restart")

    draw_pause_icon()
    glutSwapBuffers()


def main():
    global last_frame_time, next_asteroid_spawn_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"SkyHopper 3D")
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glEnable(GL_DEPTH_TEST)

    generate_platforms()
    last_frame_time = time.time()
    next_asteroid_spawn_time = time.time() + 1.0

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardDown)
    glutKeyboardUpFunc(keyboardUp)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
