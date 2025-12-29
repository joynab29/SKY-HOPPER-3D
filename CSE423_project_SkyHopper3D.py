from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random
import time


#game-states
duration=120.0
jibon=3
jitse=False
pausedd=False

jibon_shesh=False

lives=jibon
start_time=time.time()
elapsed_time=0.0
#pause
pause_start_time=0.0
paused_time_total=0.0
#timer(dt)
last_time=time.time()
fps_screen=60.0




#Camera related jinishpati
cam_x= 0
cam_y= 300
cam_z= 100
camera_pos= (cam_x, cam_y, cam_z)
fovY= 90
near= 0.1
far= 1400
camera_follow_y= 300
camera_angle= 0.0
camera_radius=200
min_angle= -70
max_angle= 70
first_person= False #1st pov
fp_camera_pos= camera_pos


#khazana
score= 0
coins=[]
gems=[]

coin_spawning=0.70
gem_Spawn= 0.85
radiusCOIN = 18
MOTA_coin = 2.5
ampl_Coin= 10.0
coin_Speed= 2.8
coin_z= 22.0
collect_Area= 35
coin_quadric=None


asteroids=[] #asteroid
max_aster= 5
min_aster_radius=12.0
max_aster_Radius= 28.0

aster_Speed= 520.0
min_spawn_aster= 0.45
max_spawn_aster= 1.15
next_asteroid_spawn_time= 0.0
aster_Hit_radius= 28.0
asteroid_quadric= None


#Player position
player_x= 0.0
player_y= 430.0
player_z= -190.0
player_y_offset= -165.0
player_dir= 180.0
turn_speed_deg_per_sec= 160.0
player_speed= 260.0

run_max= 2.3
run_frames= 40
air_control= 1.6
run_charge= 0.0
#jumping
player_vz= 0.0
gravity= -1200.0
jump_strength= 620.0
is_on_ground= True
jump_vx=0.0
jump_vy=0.0
momentum_factor_JUMP = 0.75
max_jump= 2
jumps_left=max_jump

startX= 0.0
startY= 430.0
startZ= -190.0



last_safe_x= startX
last_safe_y= startY
last_safe_z=startZ
ground_platform= None
keys_down= set()
space_was_down=False


# Platforms (shobuj)
platforms= []
first_platform_y= 430
first_platform_half= 230
platform_z= -190
platform_height= 10
platform_width= 180
platform_depth= 180
green_platform_half= platform_depth/2
num_platforms= 15
first_gap= 80
platform_gap= 80
max_jump_x= 200
screen_x_min= -350
screen_x_max= 350

platform_er_speed= 90.0


#Akashetey lokkho tara
star_count=180
stars=[]
def generate_stars():
    global stars
    stars.clear()
    for i in range(star_count):
        x= random.uniform(-1800, 1800)
        z=random.uniform(-1300,-900)
        y= random.uniform(-1800,1800)
        size= random.uniform(2.0,4.5)
        stars.append((x,y,z,size))
generate_stars()


#helper-functions
def clamp01(v):
    return max(0.0, min(1.0,v))

def lerp(a,b,t):
    return a* (1.0 - t) + b * t
def mix_color(c1, c2, t):
    return (lerp(c1[0], c2[0],t), lerp(c1[1],c2[1],t), lerp(c1[2],c2[2],t))


def get_time_t():
    return clamp01(elapsed_time / duration)


def get_night_factor():
    t= get_time_t()
    return clamp01((t- 0.6)/ 0.4)


def get_fog_factor():
    n = get_night_factor()
    return n* 0.65
def mario_position():
    return player_x,(player_y+player_y_offset), player_z


#draw-text
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


#pause-play
def toggle_pause():
    global pausedd,pause_start_time,paused_time_total
    global last_time,keys_down,space_was_down
    global next_asteroid_spawn_time

    if jibon_shesh:
        return

    now=time.time()
    if pausedd==False:
        pausedd= True
        pause_start_time=now
        keys_down.clear()
        space_was_down=False
        last_time= now
    else:
        pausedd= False
        paused_dur= now - pause_start_time
        if paused_dur<0:
            paused_dur=0.0
        paused_time_total+=paused_dur
        next_asteroid_spawn_time+= paused_dur
        last_time= now

#Game restart
def restart_game():
    global jibon_shesh,lives, start_time, elapsed_time, last_time
    global player_x,player_y, player_z, player_vz, is_on_ground
    global run_charge,ground_platform, jumps_left
    global jump_vx, jump_vy,space_was_down,keys_down
    global last_safe_x, last_safe_y,last_safe_z
    global player_dir
    global camera_pos,camera_angle,camera_radius
    global score, coins,gems
    global first_person,fp_camera_pos
    global jitse
    global asteroids,next_asteroid_spawn_time
    global pausedd,pause_start_time,paused_time_total
    

    jitse=False
    jibon_shesh= False
    lives= jibon
    score= 0
    coins.clear()
    gems.clear()
    asteroids.clear()
    next_asteroid_spawn_time=time.time()+ 1.0
    first_person=False
    fp_camera_pos=camera_pos
    pausedd = False
    pause_start_time = 0.0
    paused_time_total = 0.0
    start_time = time.time()
    elapsed_time = 0.0
    last_time = time.time()

    player_x,player_y,player_z =startX,startY,startZ
    player_vz= 0.0
    jumps_left= max_jump
    jump_vx= 0.0
    jump_vy= 0.0
    is_on_ground= True
    player_dir= 180.0
    run_charge= 0.0
    ground_platform= None
    space_was_dow = False
    keys_down.clear()

    last_safe_x, last_safe_y, last_safe_z = startX, startY, startZ
    camera_angle= 0.0
    camera_radius= 200
    camera_pos= (0, 300, 100)
    generate_platforms()

#first_fixed platform
def first_platform():
    fog=get_fog_factor()
    fog_color=(0.15, 0.17, 0.22)

    glPushMatrix()
    glTranslatef(0,430, -200)
    platform_half=230
    height=10

    top_col= mix_color((0.522, 0.514, 0.510), fog_color, fog)
    down_col= mix_color((0.380, 0.380, 0.380), fog_color, fog)

    glColor3f(*top_col)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half,height)
    glVertex3f(platform_half,-platform_half, height)
    glVertex3f(platform_half,platform_half,height)
    glVertex3f(-platform_half,platform_half, height)
    glEnd()

    glColor3f(*down_col)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half,height)
    glVertex3f(platform_half,-platform_half,height)
    glVertex3f(platform_half, -platform_half, 0)
    glVertex3f(-platform_half,-platform_half,0)
    glEnd()
    glPopMatrix()


def khazana_spawn_korbe():
    global coins,gems
    coins.clear()
    gems.clear()

    for p in platforms:
        if p["type"]=="fixed":
            if random.random()> coin_spawning:
                continue
            ox=random.uniform(-p["width"]* 0.25, p["width"] * 0.25)
            oy=random.uniform(-p["depth"]* 0.25, p["depth"] * 0.25)
            coins.append({
                "platform": p,
                "offset_x": ox,
                "offset_y": oy,
                "x": p["x"]+ ox,
                "y": p["y"]+ oy,
                "z_base": p["z"]+ platform_height+ coin_z,
                "collected": False
            })

        elif p["type"] in ("moving", "blinking"):
            if random.random()> gem_Spawn:
                continue
            ox= random.uniform(-p["width"] * 0.20, p["width"] * 0.20)
            oy= random.uniform(-p["depth"] * 0.20, p["depth"] * 0.20)
            gems.append({
                "platform": p,
                "offset_x": ox,
                "offset_y": oy,
                "x": p["x"] + ox,
                "y": p["y"] + oy,
                "z": p["z"] + platform_height + 18,
                "collected": False
            })


def khazana_update():
    for c in coins:
        if c["collected"]:
            continue
        p= c["platform"]
        c["x"]= p["x"]+ c["offset_x"]
        c["y"]= p["y"]+ c["offset_y"]
        c["z_base"]= p["z"]+ platform_height + coin_z

    for g in gems:
        if g["collected"]:
            continue
        p= g["platform"]
        g["x"]= p["x"]+ g["offset_x"]
        g["y"]= p["y"]+ g["offset_y"]
        g["z"]= p["z"]+platform_height+ 18


def generate_platforms():
    global platforms
    platforms.clear()

    prev_x= 0
    current_y= (first_platform_y - first_platform_half - first_gap - green_platform_half)
    prev_type= None

    for i in range(num_platforms):
        dx = random.uniform(-max_jump_x, max_jump_x)
        x = max(screen_x_min,min(screen_x_max, prev_x + dx))
        r = random.random()
        if prev_type== "blinking":
            p_type= "fixed" if r< 0.6 else "moving"
        else:
            if r< 0.7:
                p_type="fixed"
            elif r< 0.85:
                p_type="moving"
            else:
                p_type="blinking"

        platform= {
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
        prev_x= x
        current_y-=(platform_depth+ platform_gap)
        prev_type=p_type
    khazana_spawn_korbe()


def draw_platform(p):
    if p["type"]=="blinking" and not p["visible"]:
        return
    fog=get_fog_factor()
    fog_color= (0.15,0.17,0.22)
    top_base=(0.290,0.627, 0.275)
    side_base= (0.627, 0.451,0.275)
    top_col= mix_color(top_base,fog_color,fog)
    side_col= mix_color(side_base,fog_color, fog)

    glPushMatrix()
    glTranslatef(p["x"],p["y"],p["z"])
    w=p["width"]/ 2
    d=p["depth"]/ 2
    h=platform_height

    glColor3f(*top_col)
    glBegin(GL_QUADS)
    glVertex3f(-w,-d,h)
    glVertex3f(w,-d,h)
    glVertex3f(w,d, h)
    glVertex3f(-w,d,h)
    glEnd()
    glColor3f(*side_col)
    glBegin(GL_QUADS)
    glVertex3f(-w,d, h)
    glVertex3f(w, d,h)
    glVertex3f(w,d,0)
    glVertex3f(-w,d,0)

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
    if jibon_shesh:
        return

    now=time.time()
    for p in platforms:
        p["dx"] = 0.0
        if p["type"]== "blinking":
            if now- p["last_toggle"]>= 1.0:
                p["visible"]=not p["visible"]
                p["last_toggle"]=now
                
                
                
        if p["type"]== "moving":
            old_x=p["x"]
            p["x"]+= p["direction"]* platform_er_speed* dt
            if p["x"]> screen_x_max or p["x"]<screen_x_min:
                p["direction"] *=-1
                
                
            p["dx"]= p["x"]- old_x

        

def check_platform_collision(px, py, pz):
    if abs(px)<= 230 and abs(py- 430)<= 230:
        if pz <= -190:
            return -190, None

    for p in platforms:
        if p["type"]== "blinking" and not p["visible"]:
            continue
        if abs(px- p["x"])<= p["width"]/ 2 and abs(py - p["y"])<= p["depth"]/ 2:
            if pz<=p["z"]:
                return p["z"],p

    return None,None


def draw_door_on_platform(p):
    glPushMatrix()
    glTranslatef(p["x"], p["y"], p["z"]+ platform_height)
    door_height=75
    door_depth=5
    door_width=45
    
    w= door_width/ 2
    glColor3f(0.55,0.27,0.07) #color of door
    glBegin(GL_QUADS)
    glVertex3f(-w,0, 0)
    glVertex3f(w,0, 0)
    glVertex3f(w,0,door_height)
    glVertex3f(-w, 0,door_height)
    glEnd()

    glColor3f(0.45,0.20,0.05)
    glBegin(GL_QUADS)
    glVertex3f(w, 0, 0)
    glVertex3f(w+ door_depth,0, 0)
    glVertex3f(w+ door_depth,0,door_height)
    glVertex3f(w,0,door_height)
    glEnd()
    glColor3f(1.0, 0.85, 0.0)
    glPointSize(6)
    glBegin(GL_POINTS)
    glVertex3f(w-5,0, door_height/2)
    glEnd()
    glPopMatrix()


def draw_coin(c):
    global coin_quadric
    if coin_quadric is None:
        coin_quadric = gluNewQuadric()
        gluQuadricNormals(coin_quadric, GLU_SMOOTH)

    t=elapsed_time* coin_Speed  # freezes when paused
    bob= math.sin(t + (c["x"] * 0.01) + (c["y"] * 0.01)) * ampl_Coin
    z =c["z_base"] + bob

    camx, camy, _ = (fp_camera_pos if first_person else camera_pos)
    vx= camx - c["x"]
    vy= camy - c["y"]
    angle_z = math.degrees(math.atan2(vx, vy))

    glPushMatrix()
    glTranslatef(c["x"], c["y"], z)
    glRotatef(90, 1, 0, 0)
    glRotatef(angle_z, 0, 0, 1)

    glColor3f(0.95, 0.80, 0.10)
    gluDisk(coin_quadric, 0.0, radiusCOIN, 48, 1)
    gluCylinder(coin_quadric, radiusCOIN, radiusCOIN, MOTA_coin, 48, 1)
    glTranslatef(0, 0, MOTA_coin)
    gluDisk(coin_quadric, 0.0, radiusCOIN, 48, 1)

    glPopMatrix()


gem_quadric = None
def draw_gem(g):
    global gem_quadric
    if gem_quadric is None:
        gem_quadric= gluNewQuadric()
        gluQuadricNormals(gem_quadric, GLU_SMOOTH)

    glPushMatrix()
    glTranslatef(g["x"], g["y"], g["z"])
    glColor3f(0.20, 0.90, 1.00)

    radius = 10.0
    height = 28.0
    tip_h = 12.0
    slices = 10
    stacks = 2

    gluCylinder(gem_quadric, radius, radius, height, slices, stacks)

    glPushMatrix()
    glTranslatef(0, 0, height)
    gluCylinder(gem_quadric, radius, 0.0, tip_h, slices, stacks)
    glPopMatrix()

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

    px, py, pz= mario_position()

    for c in coins:
        if c["collected"]:
            continue
        dx = px - c["x"]
        dy = py - c["y"]
        if (dx * dx + dy * dy) <= (collect_Area * collect_Area) and abs(pz - c["z_base"]) < 150:
            c["collected"] = True
            score += 1
           

    for g in gems:
        if g["collected"]:
            continue
        p = g["platform"]
        if p["type"] == "blinking" and not p["visible"]:
            continue
        dx = px - g["x"]
        dy = py - g["y"]
        if (dx * dx + dy * dy) <= (collect_Area * collect_Area) and abs(pz - g["z"]) < 110:
            g["collected"] = True
            lives = min(jibon, lives + 1)



def door_spawn_position():
    if not platforms:
        return 0.0, -1200.0, -170.0
    p = platforms[-1]
    return p["x"], p["y"], p["z"] + platform_height + 30.0


def maybe_spawn_asteroid():
    global next_asteroid_spawn_time

    if jibon_shesh or jitse:
        return
    if len(asteroids) >= max_aster:
        return

    now= time.time()
    if now<next_asteroid_spawn_time:
        return

    sx, sy, sz = door_spawn_position()
    x = random.uniform(screen_x_min, screen_x_max)
    z = sz + random.uniform(-40.0, 60.0)
    r = random.uniform(min_aster_radius, max_aster_Radius)
    asteroids.append({"x": x, "y": sy, "z": z, "r": r, "dead": False})
    next_asteroid_spawn_time = now + random.uniform(min_spawn_aster, max_spawn_aster)


def update_asteroids(dt):
    if jibon_shesh or jitse:
        return

    maybe_spawn_asteroid()
    for a in asteroids:
        if a.get("dead",False):
            continue
        a["y"] += aster_Speed * dt

    PASS_Y= 650.0
    asteroids[:]= [a for a in asteroids if (not a.get("dead", False)) and (a["y"] <= PASS_Y)]


def check_asteroid_collisions():
    global lives, jibon_shesh

    if jibon_shesh or jitse:
        return

    px, py, pz= mario_position()
    for a in asteroids:
        if a.get("dead", False):
            continue

        dx=px -a["x"]
        dy= py -a["y"]
        dz =pz- a["z"]

        hit_dist = a["r"]+aster_Hit_radius
        if (dx*dx+ dy*dy + dz*dz)<= (hit_dist*hit_dist):
            lives-= 1
            a["dead"]= True
            if lives <= 0:
                jibon_shesh = True
            return

    asteroids[:]=[a for a in asteroids if not a.get("dead", False)]


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


#Player drawing
def draw_player():
    fog=get_fog_factor()
    fog_color= (0.15, 0.17, 0.22)
    def C(c):
        return mix_color(c, fog_color, fog)

    px,py,pz =mario_position()
    glPushMatrix()
    glTranslatef(px,py,pz+ 1.0)
    glRotatef(player_dir,0,0,1)
    glScalef(0.35,0.35,0.35)

    glColor3f(*C((0.25,0.12,0.05)))
    glPushMatrix()
    glTranslatef(-45,0, 10)
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
    glTranslatef(0,0,45)
    glScalef(140,60,60)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.90,0.15, 0.12)))
    glPushMatrix()
    glTranslatef(0,0,110)
    glScalef(140,70,90)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.20,0.55,0.95)))
    glPushMatrix()
    glTranslatef(0,0,125)
    glScalef(180,80,70)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.20,0.55,0.95)))
    glPushMatrix()
    glTranslatef(-120,0,120)
    glScalef(80,40,40)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(120,0, 120)
    glScalef(80, 40,40)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.95,0.70,0.50)))
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

    glColor3f(*C((0.20,0.10, 0.05)))
    glPushMatrix()
    glTranslatef(-35,35,215)
    glScalef(70, 30, 25)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(*C((0.15,0.08, 0.03)))
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
    if jibon_shesh or pausedd:
        return
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
    if pausedd:
        return
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
        px, py, pz = mario_position()

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
    global jibon_shesh

    if key == b'p' or key == b'P':
        toggle_pause()
        return

    if jibon_shesh:
        if key == b'r' or key == b'R':
            restart_game()
        return

    if pausedd:
        return

    keys_down.add(key)


def keyboardUp(key, x, y):
    if jibon_shesh:
        return
    if pausedd:
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

    if not pausedd:
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
    global lives, jibon_shesh, elapsed_time, start_time
    global last_safe_x, last_safe_y, last_safe_z
    global last_time
    global camera_pos
    global jitse
    global paused_time_total

    if jibon_shesh:
        glutPostRedisplay()
        return

    now = time.time()

    if pausedd:
        last_time = now
        glutPostRedisplay()
        return

    dt = now - last_time
    last_time = now
    dt = max(0.0, min(dt, 0.05))

    elapsed_time = now - start_time - paused_time_total
    if elapsed_time < 0:
        elapsed_time = 0.0

    if elapsed_time >= duration:
        elapsed_time = duration
        jibon_shesh = True
        glutPostRedisplay()
        return

    update_platforms(dt)
    khazana_update()
    update_asteroids(dt)

    ang = math.radians(player_dir)
    forward_x = -math.sin(ang)
    forward_y =  math.cos(ang)
    right_x   =  math.cos(ang)
    right_y   =  math.sin(ang)

    w_down = (b'w' in keys_down or b'W' in keys_down)
    s_down = (b's' in keys_down or b'S' in keys_down)

    if w_down:
        run_charge = min(run_frames, run_charge + dt * fps_screen)
    else:
        run_charge = max(0.0, run_charge - dt * fps_screen * 2.0)

    run_t = run_charge / float(run_frames)
    run_mult = 1.0 + (run_max - 1.0) * run_t

    base_speed = player_speed * run_mult
    steer_speed = base_speed * (air_control if not is_on_ground else 1.0)

    move_f = 0.0
    move_s = 0.0

    if w_down: move_f += 1.0
    if s_down: move_f -= 1.0
    if b'a' in keys_down or b'A' in keys_down: move_s -= 1.0
    if b'd' in keys_down or b'D' in keys_down: move_s += 1.0

    player_x += (forward_x * move_f + right_x * move_s) * steer_speed * dt
    player_y += (forward_y * move_f + right_y * move_s) * steer_speed * dt

    space_is_down = (b' ' in keys_down)
    if space_is_down and not space_was_down and jumps_left > 0:
        player_vz = jump_strength
        is_on_ground = False
        jumps_left -= 1
        jump_vx = forward_x * base_speed * move_f
        jump_vy = forward_y * base_speed * move_f

    space_was_down = space_is_down

    if not is_on_ground:
        player_x += jump_vx * momentum_factor_JUMP * dt
        player_y += jump_vy * momentum_factor_JUMP * dt

    player_vz += gravity * dt
    player_z += player_vz * dt

    px, py, pz = mario_position()
    top_z, plat = check_platform_collision(px, py, pz)

    if top_z is not None:
        player_z = top_z
        player_vz = 0.0
        is_on_ground = True
        ground_platform = plat
        last_safe_x, last_safe_y, last_safe_z = player_x, player_y, player_z
        jumps_left = max_jump
        jump_vx = jump_vy = 0.0
    else:
        is_on_ground = False
        ground_platform = None

    if is_on_ground and ground_platform and ground_platform["type"] == "moving":
        player_x += ground_platform["dx"]
        last_safe_x += ground_platform["dx"]

    check_collectibles_pickup()
    check_asteroid_collisions()

    if platforms:
        final_platform = platforms[-1]
        door_x = final_platform["x"]
        door_y = final_platform["y"]
        door_z = final_platform["z"] + platform_height

        if abs(px - door_x) < 40 and abs(py - door_y) < 40 and abs(pz - door_z) < 70:
            jibon_shesh = True
            jitse = True
            glutPostRedisplay()
            return

    if player_z < -600:
        lives -= 1
        if lives <= 0:
            jibon_shesh = True
        else:
            player_x, player_y, player_z = last_safe_x, last_safe_y, last_safe_z
            player_vz = 0.0
            is_on_ground = True
            run_charge = 0.0
            jumps_left = max_jump
            jump_vx = jump_vy = 0.0
            space_was_down = False

    player_x = max(-600, min(600, player_x))
    player_y = max(-5000, min(900, player_y))

    if not first_person:
        cx, cy, cz = camera_pos
        world_py = player_y + player_y_offset
        target_cy = world_py + camera_follow_y

        follow_speed = 6.0
        cy += (target_cy - cy) * follow_speed * dt
        camera_pos = (cx, cy, cz)

    glutPostRedisplay()


# ---------------- minimap (2d map) -----------------------
# =========================================================

# minimap position and size (bottom-left)
minimap_x = 20
minimap_y = 60
minimap_w = 220
minimap_h = 160

# minimap colors
minimap_bg = (0.05, 0.05, 0.08)
minimap_border = (1.0, 1.0, 1.0)


# ---------------------------------------------------------
# convert world coordinates to minimap coordinates
# (no clamp, no helper functions)
# ---------------------------------------------------------
def world_to_minimap(wx, wy):
    # normalize x (invert to fix mirroring)
    nx = (screen_x_max - wx) / (screen_x_max - screen_x_min)
    if nx < 0.0:
        nx = 0.0
    if nx > 1.0:
        nx = 1.0

    # normalize y (start at bottom, goal at top)
    start_y_world = startY
    end_y_world = platforms[-1]["y"] if platforms else -1200.0

    ny = (wy - start_y_world) / (end_y_world - start_y_world)
    if ny < 0.0:
        ny = 0.0
    if ny > 1.0:
        ny = 1.0

    mx = minimap_x + nx * minimap_w
    my = minimap_y + ny * minimap_h
    return mx, my


# ---------------------------------------------------------
# draw minimap
# ---------------------------------------------------------
def draw_minimap():
    if not platforms:
        return

    # switch to 2d overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # -------------------------------------------------
    # platforms (draw FIRST)
    # -------------------------------------------------
    glColor3f(0.2, 0.8, 0.2)
    for p in platforms:
        if p["type"] == "blinking" and not p["visible"]:
            continue

        mx, my = world_to_minimap(p["x"], p["y"])
        glBegin(GL_QUADS)
        glVertex2f(mx - 3, my - 2)
        glVertex2f(mx + 3, my - 2)
        glVertex2f(mx + 3, my + 2)
        glVertex2f(mx - 3, my + 2)
        glEnd()

    # -------------------------------------------------
    # door (goal)
    # -------------------------------------------------
    door = platforms[-1]
    mx, my = world_to_minimap(door["x"], door["y"])
    glColor3f(1.0, 0.6, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(mx, my + 4)
    glVertex2f(mx - 4, my - 4)
    glVertex2f(mx + 4, my - 4)
    glEnd()

    # -------------------------------------------------
    # player
    # -------------------------------------------------
    px, py, _ = mario_position()
    mx, my = world_to_minimap(px, py)
    glColor3f(1.0, 0.1, 0.1)
    glPointSize(6)
    glBegin(GL_POINTS)
    glVertex2f(mx, my)
    glEnd()

    # -------------------------------------------------
    # minimap background (draw LAST)
    # -------------------------------------------------
    glColor3f(*minimap_bg)
    glBegin(GL_QUADS)
    glVertex2f(minimap_x, minimap_y)
    glVertex2f(minimap_x + minimap_w, minimap_y)
    glVertex2f(minimap_x + minimap_w, minimap_y + minimap_h)
    glVertex2f(minimap_x, minimap_y + minimap_h)
    glEnd()

    # -------------------------------------------------
    # border (GL_LINES only)
    # -------------------------------------------------
    glColor3f(*minimap_border)
    glBegin(GL_LINES)
    # bottom
    glVertex2f(minimap_x, minimap_y)
    glVertex2f(minimap_x + minimap_w, minimap_y)
    # right
    glVertex2f(minimap_x + minimap_w, minimap_y)
    glVertex2f(minimap_x + minimap_w, minimap_y + minimap_h)
    # top
    glVertex2f(minimap_x + minimap_w, minimap_y + minimap_h)
    glVertex2f(minimap_x, minimap_y + minimap_h)
    # left
    glVertex2f(minimap_x, minimap_y + minimap_h)
    glVertex2f(minimap_x, minimap_y)
    glEnd()

    # restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def print_game_instructions():
    print("\n================ SKYHOPPER 3D CONTROLS ================\n")
    print("Movement:")
    print("  W  -> Move forward")
    print("  S  -> Move backward")
    print("  A  -> Move left")
    print("  D  -> Move right\n")

    print("Jump:")
    print("  SPACE -> Jump (double jump enabled)\n")

    print("Camera / View:")
    print("  Mouse Left Click -> Toggle First / Third Person\n")

    print("Game Control:")
    print("  P -> Pause / Resume")
    print("  R -> Restart (after Game Over)\n")

    print("Goal:")
    print("  Reach the door at the final platform")
    print("  Collect coins for score")
    print("  Collect gems to regain lives")
    print("  Avoid asteroids\n")

    print("=======================================================\n")

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

    if not first_person:
        draw_player()

    draw_text(10, 770, f"Lives: {lives}")
    time_left = max(0, int(duration - elapsed_time))
    mm = time_left // 60
    ss = time_left % 60
    draw_text(10, 740, f"Time Left: {mm:02d}:{ss:02d}")
    draw_text(10, 710, f"Score: {score}")
    draw_text(10, 660, f"POV: {'FIRST' if first_person else 'THIRD'}")


    if pausedd and not jibon_shesh:
        draw_text(450, 460, "PAUSED")

    if jibon_shesh:
        if jitse:
            draw_text(420, 420, "YOU WIN!")
            draw_text(260, 380, "Congratulations! Press 'R' to Play Again")
        else:
            draw_text(420, 420, "GAME OVER")
            draw_text(300, 380, "Press 'R' to Restart")

    draw_pause_icon()
    glClear(GL_DEPTH_BUFFER_BIT)
    draw_minimap()
    glutSwapBuffers()


# =========================================================
# ---------------- Main ------------------------------
# =========================================================
def main():
    global last_time, next_asteroid_spawn_time

   
    print_game_instructions()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"SkyHopper 3D")
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glEnable(GL_DEPTH_TEST)

    generate_platforms()
    last_time = time.time()
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