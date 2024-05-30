import numpy as np
from vispy import app, scene, io
from vispy.scene import Text
from vispy.visuals import sphere
import pygame
import time

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
ltick, diff = 0, 0
jdiff, jfreq = 0, 0
btn = False

#initial settings
m1 = 6220
m2 = 6220
M = m1 + m2
d1 = 2 * m1
d2 = 2 * m2
framerate = 25
points = 100
r = 6 * m1
#r = 10 ** (2 / 3) * 6 * m1
cm1 = m2 * r / M
cm2 = m1 * r / M
freq = 32 * 311 * M ** (-1) * (r / M) ** (-1.5)
dtheta = 2 * np.pi * freq / framerate
bounds = 15 * r
amplitudec = 20 * r ** 2 / 3
c = 2 * np.pi * freq * r / (3 * 0.544331)
alpha = 2 * np.pi * freq / c

caption1 = f'Černá díra 1 \n  Hmotnost = {m1} Sluncí \n  Průměr = {d1}'
caption2 = f'Černá díra 2 \n  Hmotnost = {m2} Sluncí \n  Průměr = {d2}'

# Create a VisPy canvas and scene
canvas = scene.SceneCanvas(keys='interactive', size=(1920, 1080), show=True)
#canvas = scene.SceneCanvas(keys='interactive', size=(1920, 1080), show=True, fullscreen=True)
grid = canvas.central_widget.add_grid()
view = grid.add_view(row=1, col=1, row_span=5, col_span=5, bgcolor=(1, 0, 0, 0.))
view.camera = scene.cameras.TurntableCamera(up='z', azimuth=0, elevation=25, distance=2.5 * bounds)
# Generate the initial meshgrid data
t = 0
th = 0
def get_gws(x, y, theta):
    return (amplitudec * np.cos(2 * np.arctan2(y, (x + 0.00001 * r / 3)) - 2 * theta + alpha * np.sqrt(x ** 2 + y ** 2)) /
            (20 * r / 3 + np.sqrt(x ** 2 + y ** 2)))

# Generate data
x = np.linspace(-bounds, bounds, points)
y = np.linspace(-bounds, bounds, points)

X, Y = np.meshgrid(x, y)
Z = get_gws(X, Y, th)
# Create a SurfacePlot to display the meshgrid
surface = scene.visuals.SurfacePlot(x=X, y=Y, z=Z, shading='smooth', color=(0, 0.5, 1, 1))
view.add(surface)

# Create spheres representing the black holes
black_hole1 = scene.visuals.Sphere(radius=d1, edge_color=(0, 0, 0, 1), color=(0, 0, 0, 1), parent=view.scene)
black_hole1.transform = scene.transforms.STTransform(translate=(cm1 * np.cos(th + np.pi / 2), cm1 * np.sin(th + np.pi / 2), r))
black_hole2 = scene.visuals.Sphere(radius=d2, edge_color=(0, 0, 0, 1), color=(0, 0, 0, 1), parent=view.scene)
black_hole2.transform = scene.transforms.STTransform(translate=(cm2 * np.cos(th - np.pi / 2), cm2 * np.sin(th - np.pi / 2), r))

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

# Add target match  to the scene
view_match = grid.add_view(row=1, col=2, col_span=4)
view_match.camera = scene.PanZoomCamera(aspect=1)
view_match.camera.set_range()
match_text = scene.visuals.Text('', color=(0.6, 0.039, 0.2), font_size=50, pos=(.5,  .0), anchor_x='center')
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
#view_sine.transform = scene.transforms.STTransform(translate=(0, 0))
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

def pressed(key=None):
    global btn
    global diff, ltick
    btn = False
    if pad is not None and key is None:
        for pgevent in pygame.event.get():
            if pgevent.type == pygame.JOYBUTTONDOWN:
                btn = True
        pygame.event.pump()
    if key == 'j' or btn:
        btn = True
        ctick = time.time()
        ndiff = ctick - ltick
        diff = ndiff if ndiff < 3 else diff
        ltick = ctick
    return btn

# Update function for the animation
def update(event):
    global t, th, dtheta, r, freq
    global ltick, diff
    global jfreq, jdiff
    #handle buttons
    btn = pressed()

    th += dtheta
    Z = get_gws(X, Y, th)
    surface.set_data(z=Z)
    # update black holes positions
    pos1 = (cm1 * np.cos(th + np.pi / 2), cm1 * np.sin(th + np.pi / 2), r)
    pos2 = (cm2 * np.cos(th - np.pi / 2), cm2 * np.sin(th - np.pi / 2), r)
    black_hole1.transform = scene.transforms.STTransform(translate=pos1)
    black_hole2.transform = scene.transforms.STTransform(translate=pos2)

    # Fifth row
    t = np.linspace(0, 2 * np.pi * 5, 1000)
    y = np.sin(t - th)
    plot_sine.set_data(np.c_[t, y])
    #freq = (1/diff)

    # Sixth row - need to update

    jfreq = 2*np.pi*(1/diff)/framerate if diff > 0 else 0

    if not btn:
        diff = (diff*1.02) if 0 < diff < 20 else 0

    jdiff += jfreq

    err = abs((jfreq - dtheta)/dtheta)

    if err < 0.25:
        print('match!')
        show_match('Shoda !')
    elif err < 0.5:
        show_match('Prihoriva...')
    else:
        show_match('')


    y = np.sin(t - jdiff)
    plot_hops.set_data(np.c_[t, y])
    # update text
    text.text = f'''{caption1} \n  Poloha = ({pos1[0]:6.0f}, {pos1[1]:6.0f})\n{caption2}\n  Poloha = ({pos2[0]:6.0f}, {pos2[1]:6.0f})\nVzdálenost černých děr = {r}\nFrekvence rotace = {freq:5.3f} Hz'''

# Use a timer to animate the meshgrid
timer = app.Timer(interval=1./framerate, connect=update, start=True)

@canvas.events.key_press.connect
def on_key_press(event):
    if event.key.name == 'Q':
        canvas.close()  # Close the window when 'Q' is pressed
    if event.key.name == 'J': #simulate keypad button
        pressed('j')

def main():
    #print(app.use_app())
    app.run()

if __name__ == '__main__':
    main()
