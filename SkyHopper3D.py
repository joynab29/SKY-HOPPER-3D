
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random
import time


# Camera-related jinish
cam_x=0
cam_y=300
cam_z=100
camera_pos =(cam_x,cam_y,cam_z)
fovY= 90 
near=0.1
far=1400

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def first_platform(): #always at the start of the game
    glPushMatrix()
    glTranslatef(0, 430, -200)

    platform_half = 230   
    height = 10           

    #top
    glColor3f(0.522, 0.514, 0.510)
    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half, height)
    glVertex3f( platform_half, -platform_half, height)
    glVertex3f( platform_half,  platform_half, height)
    glVertex3f(-platform_half,  platform_half, height)
    glEnd()

    #down
    glColor3f(0.380, 0.380, 0.380)

    glBegin(GL_QUADS)
    glVertex3f(-platform_half, -platform_half,height)
    glVertex3f( platform_half, -platform_half,height)
    glVertex3f( platform_half, -platform_half,0)
    glVertex3f(-platform_half, -platform_half,0)
    glEnd()

    glPopMatrix()
    


#Generate-random-platforms:
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
#limits
max_jump_x = 200
screen_x_min = -350
screen_x_max = 350


def generate_platforms():
    global platforms
    platforms.clear()

    prev_x = 0
    current_y = (first_platform_y - first_platform_half - initial_gap - green_platform_half )

    for i in range(num_platforms):
        dx = random.uniform(-max_jump_x, max_jump_x)
        x = prev_x + dx
        x = max(screen_x_min, min(screen_x_max,x))
        r = random.random() #kon-typer-platform
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
            "last_toggle": time.time()
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

    #TOP SURFACE 
    glColor3f(0.290, 0.627, 0.275) # dark green
    glBegin(GL_QUADS)
    glVertex3f(-w, -d, h)
    glVertex3f( w, -d, h)
    glVertex3f( w,  d, h)
    glVertex3f(-w,  d, h)
    glEnd()

    #under
    glColor3f(0.627, 0.451, 0.275)
    glBegin(GL_QUADS)
    #+Y face
    glVertex3f(-w, d, h)
    glVertex3f( w, d, h)
    glVertex3f( w, d, 0)
    glVertex3f(-w, d, 0)
    #+X face
    glVertex3f(w, -d, h)
    glVertex3f(w,  d, h)
    glVertex3f(w,  d, 0)
    glVertex3f(w, -d, 0)
    glEnd()

    glPopMatrix()

def draw_all_platforms():
    for p in platforms:
        draw_platform(p)
            
def update_platforms():
    current_time = time.time()

    for p in platforms:
        if p["type"] == "moving": #moving
            p["x"] += p["direction"]* 0.4
            if p["x"] >screen_x_max or p["x"]<screen_x_min:
                p["direction"]*= -1
        if p["type"] == "blinking":#blinking
            if current_time - p["last_toggle"]>= 1.0:
                p["visible"] = not p["visible"]
                p["last_toggle"] = current_time

def keyboardListener(key, x, y):
    pass


#camera-functions
camera_angle = 0.0           
camera_radius = 200        
min_angle = -70
max_angle = 70


def specialKeyListener(key, x, y):
    global camera_angle, camera_pos

    cx,cy,cz= camera_pos
    if key == GLUT_KEY_LEFT:
        camera_angle-= 2
        if camera_angle< min_angle:
            camera_angle= min_angle

    if key == GLUT_KEY_RIGHT:
        camera_angle+= 2
        if camera_angle> max_angle:
            camera_angle= max_angle

    if key== GLUT_KEY_UP:
        cy-=5

            
    if key== GLUT_KEY_DOWN:
        cy+=5

    r= math.radians(camera_angle)
    cx=camera_radius * math.sin(r)
    camera_pos=(cx, cy, cz)



def mouseListener(button, state, x, y):
    pass

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, near, far) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    # Position the camera and set its orientation
    gluLookAt(x, y, z,  # Camera position
              0, y - 300, -200,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)


def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    # Ensure the screen updates with the latest changes
    update_platforms()
    glutPostRedisplay()

def draw_sky_gradient():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glBegin(GL_QUADS)
    # Bottom (lighter sky)
    glColor3f(0.7, 0.9, 1.0)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)

    # Top (deeper sky)
    glColor3f(0.2, 0.5, 0.9)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size
    draw_sky_gradient()
   
    setupCamera()  # Configure camera perspective
    first_platform()
    draw_all_platforms()


  

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window
    glClearColor(0.0, 0.0, 0.0, 1.0)
    

   
    generate_platforms()


    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()
