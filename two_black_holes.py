#!/usr/bin/env python3

import numpy as np
from vispy import app, scene, io
from vispy.scene import Text
from vispy.visuals import sphere
import pygame
import time
import sys
from random import randrange

#pad init
pygame.init()

if pygame.joystick.get_count() > 0:
    print('Dancing pad detected')
    pad = pygame.joystick.Joystick(0)
    pad.init()
else:
    print('No pad detected, use "j" key to jump')
    pad = None


#global timekeeping
ltick, diff, ldiff = 0, 0, 0
jdiff, jfreq = 0, 0
cntr, mcntr = 0, 0
key_jump = False

spd = 3

def logistic_sigmoid(x):
    return 1 / (1 + np.exp(-x))

class BHS():
    def __init__(self, m1=6220, m2=6220, framerate=10, points=100):
        self.m1 = m1
        self.m2 = m2
        self.framerate = framerate
        self.points = points

        self.regen()

        self.recalc()

    def recalc(self):
        self.M = self.m1 + self.m2
        self.d1 = 2 * self.m1
        self.d2 = 2 * self.m2
        self.dsum = self.d1 + self.d2
        self.r = 6 * self.m1
        self.cm1 = self.m2 * self.r / self.M
        self.cm2 = self.m1 * self.r / self.M
        self.freq = 32 * 311 * self.M ** (-1) * (self.r / self.M) ** (-1.5)
        self.dtheta = 2 * np.pi * self.freq / self.framerate
        self.bounds = 15 * self.r
        self.amplitudec = 20 * self.r ** 2 / 3
        self.c = 2 * np.pi * self.freq * self.r / (3 * 0.544331)
        self.alpha = 2 * np.pi * self.freq / self.c

    def regen(self):
        self.m1 = randrange(4000, 7000)
        self.m2 = randrange(4000, 7000)
        self.recalc()

    def get_gws(self, x, y, theta):
        return (self.amplitudec * np.cos(2 * np.arctan2(y, (x + 0.00001 * self.r / 3)) - 2 * theta + self.alpha * np.sqrt(x ** 2 + y ** 2)) /
            (20 * self.r / 3 + np.sqrt(x ** 2 + y ** 2)))

    def get_merge_ringdown(self, x, y, theta):
        rfinal = 2 * self.M
        cm1init = self.m2 * self.r / self.M
        cm2init = self.m1 * self.r / self.M
        cm1final = self.m2 * rfinal / self.M
        cm2final = self.m1 * rfinal / self.M
        freq = 32311 * self.M ** (-1) * (self.r / self.M) ** (-3 / 2)
        athetalen = 2 * np.pi / 4
        mthetalen = 2 * np.pi / 4
        rthetalen = 5.5 * np.pi
        mthetaend = athetalen + mthetalen
        rthetaend = mthetaend + rthetalen
        thetathr = 3 * np.pi / 4
        thetafactor = 2
        c = 2 * np.pi * self.freq * self.r / (3 * 0.544331)
        alpha = 2 * np.pi * self.freq / self.c

         #Define the function
        term1 = -logistic_sigmoid(-thetafactor * (-2 * (theta - thetathr))) * \
            10000 * self.amplitudec / (3 * self.dsum**2 + x**2 + y**2)
        term2 = logistic_sigmoid(thetafactor * (-2 * (theta - thetathr) + alpha * np.sqrt(x**2 + y**2)))
        term3 = logistic_sigmoid(x**2 + y**2 - 25)
        term4 = ((self.amplitudec * np.cos(2 * np.arctan2(y, x + 0.00001 * self.r / 3) - 2 * theta + alpha * np.sqrt(x**2 + y**2))) /
            (20 * self.r / 3 + np.sqrt(x**2 + y**2)))
        return term1 + term2 * term3 * term4

bhs = BHS()

caption1 = f'Černá díra 1 \n  Hmotnost = {bhs.m1} Sluncí \n  Průměr = {bhs.d1}'
caption2 = f'Černá díra 2 \n  Hmotnost = {bhs.m2} Sluncí \n  Průměr = {bhs.d2}'

# Create a VisPy canvas and scene
fullscreen = False if len(sys.argv) > 1 else True
canvas = scene.SceneCanvas(keys='interactive', size=(1920, 1080), show=True,
                           fullscreen=fullscreen, vsync=True, autoswap=False)
grid = canvas.central_widget.add_grid()
view = grid.add_view(row=1, col=1, row_span=5, col_span=5, bgcolor=(1, 0, 0, 0.))
view.camera = scene.cameras.TurntableCamera(up='z', azimuth=0, elevation=25,
                                            distance=2.5 * bhs.bounds)
# Generate the initial meshgrid data
t = 0
th = 0
ths = 0
state = 'game'

# Generate data
x = np.linspace(-bhs.bounds, bhs.bounds, bhs.points)
y = np.linspace(-bhs.bounds, bhs.bounds, bhs.points)

X, Y = np.meshgrid(x, y)
Z = bhs.get_gws(X, Y, th)
# Create a SurfacePlot to display the meshgrid
surface = scene.visuals.SurfacePlot(x=X, y=Y, z=Z, shading='smooth', color=(0, 0.5, 1, 1))
#surface = scene.visuals.SurfacePlot(x=X, y=Y, z=Z, shading='smooth', color=(0, 0.5, 1, 1))
view.add(surface)

# Create spheres representing the black holes
black_hole1 = scene.visuals.Sphere(radius=bhs.d1, edge_color=(0, 0, 0, 1),
                                   color=(0, 0, 0, 1), parent=view.scene)
black_hole2 = scene.visuals.Sphere(radius=bhs.d2, edge_color=(0, 0, 0, 1),
                                   color=(0, 0, 0, 1), parent=view.scene)
view.add(black_hole1)
view.add(black_hole2)

#Create big sphere for resulting black hole
black_mhole = scene.visuals.Sphere(radius=bhs.dsum, edge_color=(0, 0, 0, 1),
                                   color=(0, 0, 0, 1))

# Top-left: Logo image
img_data = io.read_png('Lisa_ESA_logo.png')
image = scene.visuals.Image(img_data)
view1 = grid.add_view(row=0, col=0,bgcolor=(0, 0, 1, 0.))
view1.transform = scene.transforms.STTransform(scale=(2.5, 2.5, 1))
view1.add(image)
view1.camera = scene.PanZoomCamera(aspect=1)
view1.camera.flip = (False, True, False)
view1.camera.set_range()

# Add text to the scene
view_text = grid.add_view(row=0, col=2, col_span=4)
text = scene.visuals.Text('Skákání v rytmu gravitačních vln \n s misí LISA', color=(0.6, 0.039, 0.2), font_size=50, pos=(.5,  .0), anchor_x='center')
view_text.camera = scene.PanZoomCamera(aspect=1)
view_text.camera.set_range()
view_text.add(text)

# Add target match to the scene
view_match = grid.add_view(row=1, col=2, col_span=4)
view_match.camera = scene.PanZoomCamera(aspect=1)
view_match.camera.set_range()
match_text = scene.visuals.Text('', color=(0.6, 0.39, 0.2), font_size=50, pos=(.5,  .0), anchor_x='center')
view_match.add(match_text)

def show_match(text):
    #global match_text, scene
    match_text.text = text

# Add text to the scene
view_text = grid.add_view(row=1, col=5, row_span=4, col_span=2, bgcolor=(0, 1, 0, 0.))
text = scene.visuals.Text('', color=(0.6, 0.039, 0.2), font_size=20, pos=(-1., 0), anchor_x='left')
view_text.camera = scene.PanZoomCamera(aspect=1)
view_text.camera.set_range()
view_text.add(text)

# Fifth row: Sinusoidal curve
plot_sine = scene.visuals.Line(color=(0.6, 0.039, 0.2, 0.8), width=5)
view_sine = grid.add_view(row=5, col=0, col_span=7, bgcolor=(0, 1, 0, 0.))
view_sine.add(plot_sine)
view_sine.camera = scene.PanZoomCamera(aspect=1)
view_sine.camera.set_range()
view_sine.camera.set_range(x=(-np.pi/2., 2 * np.pi * 5 + np.pi / 2.), y=(-1, 1))

# Adding x-axis and y-axis
x_axis = scene.visuals.Line(color='white', parent=view_sine.scene)
y_axis = scene.visuals.Line(color='white', parent=view_sine.scene)
x_axis.set_data(np.array([[-0.1, 0], [2 * np.pi * 5, 0 * 10]]))  # x-axis from 0 to 2*pi
y_axis.set_data(np.array([[-0.1, -1], [-0.1, 1]]))  # y-axis from -1 to 1

# Adding labels
x_label = scene.visuals.Text('Čas', color='white', font_size=20, parent=view_sine.scene)
y_label = scene.visuals.Text('Amplituda', color='white', font_size=20, parent=view_sine.scene)
x_label.pos = 2 * np.pi * 5 + 0.5, -0.5
y_label.pos = -1.5, 0.8

# Sixth row: Sinusoidal curve
plot_hops = scene.visuals.Line(color='green', width=5)
view_hops = grid.add_view(row=6, col=0, col_span=7, bgcolor=(1, 0, 0, 0.))
view_hops.add(plot_hops)
view_hops.camera = scene.PanZoomCamera(aspect=1)
view_hops.camera.set_range()
view_hops.camera.set_range(x=(-np.pi/2., 2 * np.pi * 5 + np.pi / 2.), y=(-1, 1))


# Adding x-axis and y-axis
x_axis = scene.visuals.Line(color='white', parent=view_hops.scene)
y_axis = scene.visuals.Line(color='white', parent=view_hops.scene)
x_axis.set_data(np.array([[-0.1, 0], [2 * np.pi * 5, 0 * 10]]))  # x-axis from 0 to 2*pi
y_axis.set_data(np.array([[-0.1, -1], [-0.1, 1]]))  # y-axis from -1 to 1

# Adding labels
x_label = scene.visuals.Text('Čas', color='white', font_size=20, parent=view_hops.scene)
y_label = scene.visuals.Text('Skok', color='white', font_size=20, parent=view_hops.scene)
x_label.pos = 2 * np.pi * 5 + 0.5, -0.5
y_label.pos = -1.5, 0.8


# Generate timescale
t = np.linspace(0, 2 * np.pi * 5, 250)

def pressed(key=None):
    global key_jump
    global diff, ltick
    btn = False
    if pad is not None and key is None:
        for pgevent in pygame.event.get():
            if pgevent.type == pygame.JOYBUTTONDOWN:
                btn = True
        pygame.event.pump()
    if key_jump or btn:
        btn = True
        ctick = time.time()
        ndiff = ctick - ltick
        diff = ndiff if ndiff < 10 else diff
        ltick = ctick
        key_jump = False
    return btn

# Update function for the animation
def update(event):
    global t, th, ths, r, freq
    global ltick, diff, ldiff, cntr
    global jfreq, jdiff
    global spd, mcntr
    global state
    #handle buttons separately
    btn = pressed()

    th += bhs.dtheta

    pos1 = (bhs.cm1 * np.cos(th + np.pi / 2), bhs.cm1 * np.sin(th + np.pi / 2),
            bhs.r)
    pos2 = (bhs.cm2 * np.cos(th - np.pi / 2), bhs.cm2 * np.sin(th - np.pi / 2),
            bhs.r)

    if state == 'win':
        Z = bhs.get_merge_ringdown(X, Y, th)
        mcntr += 1
    else:
        # update black holes positions
        black_hole1.transform = scene.transforms.STTransform(translate=pos1)
        black_hole2.transform = scene.transforms.STTransform(translate=pos2)
        #update ripples
        Z = bhs.get_gws(X, Y, th)
    surface.set_data(z=Z)

    ths += spd * bhs.dtheta

    cfreq = (1/diff) if diff > 0 else 0
    jfreq = 2*np.pi*cfreq/bhs.framerate

    jdiff += jfreq

    if btn:
        jdiff, cntr = 0, 0
        ldiff = diff

    cntr += 1

    if not btn and cntr > 5*bhs.framerate:
        diff = (diff*np.exp(0.02)) if 0 < diff < 20 else 0

    err = abs((jfreq - (bhs.dtheta*spd))/(bhs.dtheta*spd))

    if state=='game':
        if err < 0.15:
            show_match('Super tempo...')
            mcntr += 1
        elif err < 0.5:
            show_match('Přihořívá...')
            mcntr = 0
        else:
            show_match('')
            mcntr = 0

    if state=='game' and mcntr >= 200:
        print('WIN!')
        show_match('!!!Výhra!!!')
        black_hole1.parent = None
        black_hole2.parent = None
        view.add(black_mhole)
        y = np.zeros(250)
        yj = np.zeros(250)
        plot_sine.set_data(np.c_[t, y])
        plot_hops.set_data(np.c_[t, yj])
        state = 'win'
        mcntr = th = ths = jdiff = diff = 0
    elif state=='win' and mcntr >= 200:
        bhs.regen()
        black_mhole.parent = None
        view.add(black_hole1)
        view.add(black_hole2)
        state = 'game'
        mcntr = th = ths = jdiff = diff = 0

    if state=='game':
        # Fifth row
        y = np.sin(t - (ths))
        plot_sine.set_data(np.c_[t, y])

        # Sixth row - need to update
        yj = np.sin(t * (2 * np.pi * jfreq )  - jdiff)
        #yj = np.sin(t * 2 * np.pi * cfreq / spd - jdiff)
        #y = np.sin(t * spd * jfreq)
        plot_hops.set_data(np.c_[t, yj])

        # update text
        text.text = f'''{caption1} \n  Poloha = ({pos1[0]:6.0f}, {pos1[1]:6.0f})\n\
{caption2}\n  Poloha = ({pos2[0]:6.0f},{pos2[1]:6.0f})\n\
Vzdálenost černých děr = {bhs.r}\n\
\tFrekvence rotace = {bhs.freq:5.3f} Hz\n\
\tFrekvence skoku  = {cfreq/spd:5.3f} Hz'''
    else:
        text.text = f''
    #canvas.update()

def pps(event):
    canvas.measure_fps()

# Use a timer to animate the meshgrid
timer = app.Timer(interval=(1./bhs.framerate), connect=update, start=True)

timer_pps = app.Timer(interval=1, connect=pps, start=True)

@canvas.events.key_press.connect
def on_key_press(event):
    global key_jump
    if event.key.name == 'Q':
        canvas.close()  # Close the window when 'Q' is pressed
    if event.key.name == 'J': #simulate keypad button
        key_jump = True

def main():
    #print(app.use_app())
    app.run()

if __name__ == '__main__':
    main()
