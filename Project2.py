from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random
import time


# =========================================================
# ---------------- NEW FEATURES (Game State) --------------
# =========================================================
GAME_DURATION = 120.0  # 2 minutes in seconds
MAX_LIVES = 3

game_over = False
lives = MAX_LIVES

start_time = time.time()
elapsed_time = 0.0  # seconds since start


def restart_game():
    """
    Full restart: resets timer, lives, player, platforms, movement states.
    """
    global game_over, lives, start_time, elapsed_time
    global player_x, player_y, player_z, player_vz, is_on_ground
    global run_charge, ground_platform, jumps_left
    global jump_vx, jump_vy, space_was_down, keys_down
    global last_safe_x, last_safe_y, last_safe_z

    game_over = False
    lives = MAX_LIVES

    start_time = time.time()
    elapsed_time = 0.0

    # reset player
    player_x = start_x
    player_y = start_y
    player_z = start_z
    player_vz = 0.0
    is_on_ground = True

    # reset movement state
    run_charge = 0
    ground_platform = None
    jumps_left = MAX_JUMPS
    jump_vx = 0.0
    jump_vy = 0.0
    space_was_down = False
    keys_down.clear()

    # reset respawn checkpoint
    last_safe_x = start_x
    last_safe_y = start_y
    last_safe_z = start_z

    # regenerate platforms
    generate_platforms()


# ---------------- Camera-related jinish ----------------
cam_x = 0
cam_y = 300
cam_z = 100
camera_pos = (cam_x, cam_y, cam_z)
fovY = 90
near = 0.1
far = 1400


# ---------------- Player position (center of grey start platform) ----------------
player_x = 0
player_y = 430
player_z = -190  # top of grey platform is -200 + 10

# movement speed (base)
player_speed = 12

# ---------------- Run + Air control tuning ----------------
RUN_MAX_MULT = 2.3          # max running multiplier when holding W
RUN_RAMP_FRAMES = 40        # frames to reach max run speed
AIR_CONTROL_MULT = 1.6      # extra control while in air (still allows steering)

run_charge = 0

# ---------------- Jump & Gravity ----------------
player_vz = 0.0
gravity = -2.0
jump_strength = 28.0
is_on_ground = True

# ✅ Double jump
MAX_JUMPS = 2
jumps_left = MAX_JUMPS

# ✅ Air momentum (this is the key to reaching platforms)
jump_vx = 0.0
jump_vy = 0.0
JUMP_MOMENTUM_FACTOR = 0.75  # how much stored momentum applies per frame in air

# respawn (start) position
start_x = 0
start_y = 430
start_z = -190

# ✅ NEW: last safe checkpoint (updates when you LAND on a platform)
last_safe_x = start_x
last_safe_y = start_y
last_safe_z = start_z

# Track which platform we are standing on (for moving platforms)
ground_platform = None

# Continuous key holding
keys_down = set()

# To detect "tap" of space (so holding space doesn't spam jumps)
space_was_down = False


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


# ----------------- MARIO PLAYER -----------------
def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
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

    # Head
    glColor3f(0.95, 0.70, 0.50)
    glPushMatrix()
    glTranslatef(0, 0, 195)
    glScalef(120, 80, 90)
    glutSolidCube(1)
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


# ---------------- Generate random platforms ----------------
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


def update_platforms():
    # ✅ NEW: freeze platforms on game over
    if game_over:
        return

    current_time = time.time()

    for p in platforms:
        p["dx"] = 0.0

        if p["type"] == "moving":
            old_x = p["x"]
            p["x"] += p["direction"] * 0.9
            if p["x"] > screen_x_max or p["x"] < screen_x_min:
                p["direction"] *= -1
            p["dx"] = p["x"] - old_x

        if p["type"] == "blinking":
            if current_time - p["last_toggle"] >= 1.0:
                p["visible"] = not p["visible"]
                p["last_toggle"] = current_time


def check_platform_collision(px, py, pz):
    # Grey first platform
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


def normalize(vx, vy):
    length = math.sqrt(vx * vx + vy * vy)
    if length == 0:
        return 0.0, 0.0
    return vx / length, vy / length


def get_camera_vectors():
    camx, camy, _ = camera_pos
    target_x = 0
    target_y = camy - 300  # matches setupCamera()

    fx = target_x - camx
    fy = target_y - camy
    fx, fy = normalize(fx, fy)

    rx = fy
    ry = -fx
    return fx, fy, rx, ry


def keyboardDown(key, x, y):
    global game_over

    # ✅ NEW: Restart on game over
    if game_over:
        if key == b'r' or key == b'R':
            restart_game()
        return  # block all other keys

    keys_down.add(key)


def keyboardUp(key, x, y):
    if game_over:
        return
    if key in keys_down:
        keys_down.remove(key)


# ---------------- camera-functions ----------------
camera_angle = 0.0
camera_radius = 200
min_angle = -70
max_angle = 70


def specialKeyListener(key, x, y):
    global camera_angle, camera_pos

    # ✅ NEW: freeze camera on game over
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


# ✅ NEW SKY: day -> night based on timer
def draw_sky_gradient():
    # progress 0..1
    t = min(elapsed_time / GAME_DURATION, 1.0)

    # light sky -> dark navy
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
    # bottom
    glColor3f(r_bottom, g_bottom, b_bottom)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)

    # top
    glColor3f(r_top, g_top, b_top)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)


def idle():
    global player_x, player_y, player_z, player_vz, is_on_ground
    global run_charge, ground_platform, jumps_left
    global jump_vx, jump_vy, space_was_down
    global lives, game_over, elapsed_time, start_time
    global last_safe_x, last_safe_y, last_safe_z

    # ✅ NEW: Freeze everything on game over
    if game_over:
        glutPostRedisplay()
        return

    # ✅ NEW: Timer update
    elapsed_time = time.time() - start_time
    if elapsed_time >= GAME_DURATION:
        elapsed_time = GAME_DURATION
        game_over = True
        glutPostRedisplay()
        return

    update_platforms()

    fx, fy, rx, ry = get_camera_vectors()

    # -------- RUN LOGIC (hold W to run) --------
    if b'w' in keys_down or b'W' in keys_down:
        run_charge = min(RUN_RAMP_FRAMES, run_charge + 1)
    else:
        run_charge = max(0, run_charge - 2)

    run_t = run_charge / float(RUN_RAMP_FRAMES) if RUN_RAMP_FRAMES > 0 else 1.0
    run_mult = 1.0 + (RUN_MAX_MULT - 1.0) * run_t

    # -------- Movement direction --------
    forward = 0
    right = 0

    if b'w' in keys_down or b'W' in keys_down:
        forward += 1
    if b's' in keys_down or b'S' in keys_down:
        forward -= 1
    if b'd' in keys_down or b'D' in keys_down:
        right += 1
    if b'a' in keys_down or b'A' in keys_down:
        right -= 1

    mag = math.sqrt(forward * forward + right * right)
    if mag > 0:
        forward /= mag
        right /= mag

    # Base move speed for THIS frame
    speed = player_speed * run_mult

    # In-air steering still allowed (but not the main distance)
    steer_speed = speed * (AIR_CONTROL_MULT if not is_on_ground else 1.0)

    # Apply steering (works on ground + in air)
    player_x += (fx * forward + rx * right) * steer_speed
    player_y += (fy * forward + ry * right) * steer_speed

    # -------- SPACE press detection (rising edge) --------
    space_is_down = (b' ' in keys_down)

    # -------- DOUBLE JUMP with stored momentum --------
    if space_is_down and not space_was_down and jumps_left > 0:
        player_vz = jump_strength
        is_on_ground = False
        jumps_left -= 1

        jump_vx = (fx * forward + rx * right) * speed
        jump_vy = (fy * forward + ry * right) * speed

        if abs(jump_vx) < 0.0001 and abs(jump_vy) < 0.0001:
            pass

    space_was_down = space_is_down

    # -------- Apply stored momentum while airborne --------
    if not is_on_ground:
        player_x += jump_vx * JUMP_MOMENTUM_FACTOR
        player_y += jump_vy * JUMP_MOMENTUM_FACTOR

    # -------- Gravity --------
    player_vz += gravity
    player_z += player_vz

    # -------- Collision --------
    top_z, plat = check_platform_collision(player_x, player_y, player_z)
    if top_z is not None:
        player_z = top_z
        player_vz = 0.0
        is_on_ground = True
        ground_platform = plat

        # ✅ NEW: update last safe checkpoint when landed
        last_safe_x = player_x
        last_safe_y = player_y
        last_safe_z = player_z

        jumps_left = MAX_JUMPS
        jump_vx = 0.0
        jump_vy = 0.0
    else:
        is_on_ground = False
        ground_platform = None

    # -------- Move with moving platform --------
    if is_on_ground and ground_platform is not None and ground_platform["type"] == "moving":
        player_x += ground_platform["dx"]
        # also update checkpoint with carry, so respawn matches platform movement
        last_safe_x += ground_platform["dx"]

    # -------- Respawn if fell --------
    if player_z < -600:
        lives -= 1
        if lives <= 0:
            game_over = True
        else:
            # respawn at last safe platform (checkpoint)
            player_x = last_safe_x
            player_y = last_safe_y
            player_z = last_safe_z
            player_vz = 0.0
            is_on_ground = True
            ground_platform = None
            run_charge = 0
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

    # ✅ NEW UI: Lives + Timer
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
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"SkyHopper 3D")
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glEnable(GL_DEPTH_TEST)

    generate_platforms()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardDown)
    glutKeyboardUpFunc(keyboardUp)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()





