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

game_over = False
lives = MAX_LIVES

start_time = time.time()
elapsed_time = 0.0

# dt / timing
last_frame_time = time.time()
FPS_BASE = 60.0  # used for "frame-like" values such as run ramp


# ---------------- Camera-related jinish ----------------
cam_x = 0
cam_y = 300
cam_z = 100
camera_pos = (cam_x, cam_y, cam_z)
fovY = 90
near = 0.1
far = 1400

# camera controls
camera_angle = 0.0
camera_radius = 200
min_angle = -70
max_angle = 70


# ---------------- Player position (center of grey start platform) ----------------
player_x = 0.0
player_y = 430.0
player_z = -190.0  # top of grey platform is -200 + 10

# ✅ FIX (3): start facing toward green platforms (downwards in Y)
# Our forward vector is (-sin(dir), cos(dir)), so 180° makes forward_y = -1 (toward negative Y).
player_dir = 180.0

# angular speed (deg/sec)
turn_speed_deg_per_sec = 160.0

# ✅ FIX (1): decrease speed a little (was 320)
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


def restart_game():
    """Full restart: resets timer, lives, player, platforms, movement states, AND camera."""
    global game_over, lives, start_time, elapsed_time, last_frame_time
    global player_x, player_y, player_z, player_vz, is_on_ground
    global run_charge, ground_platform, jumps_left
    global jump_vx, jump_vy, space_was_down, keys_down
    global last_safe_x, last_safe_y, last_safe_z
    global player_dir
    global camera_pos, camera_angle, camera_radius

    game_over = False
    lives = MAX_LIVES

    start_time = time.time()
    elapsed_time = 0.0
    last_frame_time = time.time()

    # reset player
    player_x, player_y, player_z = start_x, start_y, start_z
    player_vz = 0.0
    is_on_ground = True

    # ✅ FIX (3): reset facing toward platforms
    player_dir = 180.0

    # reset movement state
    run_charge = 0.0
    ground_platform = None
    jumps_left = MAX_JUMPS
    jump_vx = 0.0
    jump_vy = 0.0
    space_was_down = False
    keys_down.clear()

    # reset checkpoint
    last_safe_x, last_safe_y, last_safe_z = start_x, start_y, start_z

    # ✅ FIX (2): reset camera too
    camera_angle = 0.0
    camera_radius = 200
    camera_pos = (0, 300, 100)

    generate_platforms()


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


def first_platform():
    glPushMatrix()
    glTranslatef(0, 430, -200)

    platform_half = 230
    height = 10

    glColor3f(0.522, 0.514, 0.510)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half, height)
    glVertex3f(platform_half, -platform_half, height)
    glVertex3f(platform_half, platform_half, height)
    glVertex3f(-platform_half, platform_half, height)
    glEnd()

    glColor3f(0.380, 0.380, 0.380)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half, height)
    glVertex3f(platform_half, -platform_half, height)
    glVertex3f(platform_half, -platform_half, 0)
    glVertex3f(-platform_half, -platform_half, 0)
    glEnd()

    glPopMatrix()


def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)

    # rotate to face direction
    glRotatef(player_dir, 0, 0, 1)

    # scale
    glScalef(0.35, 0.35, 0.35)

    # Shoes
    glColor3f(0.25, 0.12, 0.05)
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

    # Legs
    glColor3f(0.20, 0.55, 0.95)
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glScalef(140, 60, 60)
    glutSolidCube(1)
    glPopMatrix()

    # Torso
    glColor3f(0.90, 0.15, 0.12)
    glPushMatrix()
    glTranslatef(0, 0, 110)
    glScalef(140, 70, 90)
    glutSolidCube(1)
    glPopMatrix()

    # Jacket
    glColor3f(0.20, 0.55, 0.95)
    glPushMatrix()
    glTranslatef(0, 0, 125)
    glScalef(180, 80, 70)
    glutSolidCube(1)
    glPopMatrix()

    # Arms
    glColor3f(0.20, 0.55, 0.95)
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

    # Hands
    glColor3f(0.95, 0.70, 0.50)
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

    # Buttons
    glColor3f(1.0, 0.95, 0.2)
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

    # Head
    glColor3f(0.95, 0.70, 0.50)
    glPushMatrix()
    glTranslatef(0, 0, 195)
    glScalef(120, 80, 90)
    glutSolidCube(1)
    glPopMatrix()

    # Nose
    glColor3f(0.95, 0.70, 0.50)
    glPushMatrix()
    glTranslatef(60, 0, 195)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 10, 25, 16, 4)
    glPopMatrix()

    # Hair
    glColor3f(0.20, 0.10, 0.05)
    glPushMatrix()
    glTranslatef(-35, 35, 215)
    glScalef(70, 30, 25)
    glutSolidCube(1)
    glPopMatrix()

    # Mustache
    glColor3f(0.15, 0.08, 0.03)
    glPushMatrix()
    glTranslatef(35, 30, 175)
    glScalef(60, 8, 20)
    glutSolidCube(1)
    glPopMatrix()

    # Eye
    glPushMatrix()
    glTranslatef(40, 40, 205)
    glColor3f(1, 1, 1)
    gluSphere(gluNewQuadric(), 18, 16, 16)
    glTranslatef(8, 8, 0)
    glColor3f(0.1, 0.1, 0.1)
    gluSphere(gluNewQuadric(), 8, 16, 16)
    glPopMatrix()

    # Hat
    glColor3f(0.20, 0.55, 0.95)
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


def generate_platforms():
    global platforms
    platforms.clear()

    prev_x = 0
    current_y = (first_platform_y - first_platform_half - initial_gap - green_platform_half)

    for _ in range(num_platforms):
        dx = random.uniform(-max_jump_x, max_jump_x)
        x = max(screen_x_min, min(screen_x_max, prev_x + dx))

        r = random.random()
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


def draw_platform(p):
    if p["type"] == "blinking" and not p["visible"]:
        return

    glPushMatrix()
    glTranslatef(p["x"], p["y"], p["z"])
    w = p["width"] / 2
    d = p["depth"] / 2
    h = platform_height

    glColor3f(0.290, 0.627, 0.275)
    glBegin(GL_QUADS)
    glVertex3f(-w, -d, h)
    glVertex3f(w, -d, h)
    glVertex3f(w, d, h)
    glVertex3f(-w, d, h)
    glEnd()

    glColor3f(0.627, 0.451, 0.275)
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


def specialKeyListener(key, x, y):
    global camera_angle, camera_pos
    if game_over:
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
    pass


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, near, far)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, y - 300, -200, 0, 0, 1)


def draw_sky_gradient():
    t = min(elapsed_time / GAME_DURATION, 1.0)

    r_bottom = 0.7 * (1 - t) + 0.02 * t
    g_bottom = 0.9 * (1 - t) + 0.03 * t
    b_bottom = 1.0 * (1 - t) + 0.20 * t

    r_top = 0.2 * (1 - t) + 0.01 * t
    g_top = 0.5 * (1 - t) + 0.02 * t
    b_top = 0.9 * (1 - t) + 0.12 * t

    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    glColor3f(r_bottom, g_bottom, b_bottom)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)

    glColor3f(r_top, g_top, b_top)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)


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


def idle():
    global player_x, player_y, player_z, player_vz, is_on_ground
    global run_charge, ground_platform, jumps_left
    global jump_vx, jump_vy, space_was_down
    global lives, game_over, elapsed_time, start_time
    global last_safe_x, last_safe_y, last_safe_z
    global last_frame_time
    global player_dir

    if game_over:
        glutPostRedisplay()
        return

    now = time.time()
    dt = now - last_frame_time
    last_frame_time = now
    dt = max(0.0, min(dt, 0.05))

    elapsed_time = now - start_time
    if elapsed_time >= GAME_DURATION:
        elapsed_time = GAME_DURATION
        game_over = True
        glutPostRedisplay()
        return

    update_platforms(dt)

    # angular movement
    if b'a' in keys_down or b'A' in keys_down:
        player_dir = (player_dir + turn_speed_deg_per_sec * dt) % 360.0
    if b'd' in keys_down or b'D' in keys_down:
        player_dir = (player_dir - turn_speed_deg_per_sec * dt) % 360.0

    # forward vector
    ang = math.radians(player_dir)
    forward_x = -math.sin(ang)
    forward_y = math.cos(ang)

    # run
    w_down = (b'w' in keys_down or b'W' in keys_down)
    s_down = (b's' in keys_down or b'S' in keys_down)

    if w_down:
        run_charge = min(RUN_RAMP_FRAMES, run_charge + dt * FPS_BASE)
    else:
        run_charge = max(0.0, run_charge - dt * FPS_BASE * 2.0)

    run_t = run_charge / float(RUN_RAMP_FRAMES) if RUN_RAMP_FRAMES > 0 else 1.0
    run_mult = 1.0 + (RUN_MAX_MULT - 1.0) * run_t

    base_speed = player_speed * run_mult
    steer_speed = base_speed * (AIR_CONTROL_MULT if not is_on_ground else 1.0)

    # W/S movement
    move_dir = 0.0
    if w_down:
        move_dir += 1.0
    if s_down:
        move_dir -= 1.0

    player_x += forward_x * steer_speed * move_dir * dt
    player_y += forward_y * steer_speed * move_dir * dt

    # jump edge detect
    space_is_down = (b' ' in keys_down)
    if space_is_down and not space_was_down and jumps_left > 0:
        player_vz = jump_strength
        is_on_ground = False
        jumps_left -= 1

        jump_vx = forward_x * base_speed * move_dir
        jump_vy = forward_y * base_speed * move_dir

        if abs(move_dir) < 0.0001:
            pass

    space_was_down = space_is_down

    # apply air momentum
    if not is_on_ground:
        player_x += jump_vx * JUMP_MOMENTUM_FACTOR * dt
        player_y += jump_vy * JUMP_MOMENTUM_FACTOR * dt

    # gravity
    player_vz += gravity * dt
    player_z += player_vz * dt

    # collision
    top_z, plat = check_platform_collision(player_x, player_y, player_z)
    if top_z is not None:
        player_z = top_z
        player_vz = 0.0
        is_on_ground = True
        ground_platform = plat

        last_safe_x = player_x
        last_safe_y = player_y
        last_safe_z = player_z

        jumps_left = MAX_JUMPS
        jump_vx = 0.0
        jump_vy = 0.0
    else:
        is_on_ground = False
        ground_platform = None

    # move with moving platform
    if is_on_ground and ground_platform is not None and ground_platform["type"] == "moving":
        player_x += ground_platform["dx"]
        last_safe_x += ground_platform["dx"]

    # falling -> lose life -> respawn
    if player_z < -600:
        lives -= 1
        if lives <= 0:
            game_over = True
        else:
            player_x = last_safe_x
            player_y = last_safe_y
            player_z = last_safe_z
            player_vz = 0.0
            is_on_ground = True
            ground_platform = None
            run_charge = 0.0
            jumps_left = MAX_JUMPS
            jump_vx = 0.0
            jump_vy = 0.0
            space_was_down = False

    # bounds
    player_x = max(-600, min(600, player_x))
    player_y = max(-5000, min(900, player_y))

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    draw_sky_gradient()

    setupCamera()
    first_platform()
    draw_all_platforms()
    draw_player()

    # UI
    draw_text(10, 770, f"Lives: {lives}")
    time_left = max(0, int(GAME_DURATION - elapsed_time))
    mm = time_left // 60
    ss = time_left % 60
    draw_text(10, 740, f"Time Left: {mm:02d}:{ss:02d}")

    if game_over:
        draw_text(420, 420, "GAME OVER")
        draw_text(300, 380, "Press 'R' to Restart")

    glutSwapBuffers()


def main():
    global last_frame_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"SkyHopper 3D")
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glEnable(GL_DEPTH_TEST)

    generate_platforms()
    last_frame_time = time.time()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardDown)
    glutKeyboardUpFunc(keyboardUp)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()








