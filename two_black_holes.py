import numpy as np
from vispy import app, scene, io
from vispy.scene import Text
from vispy.visuals import sphere

#initial settings
m1 = 6220
m2 = 6220
M = m1 + m2
d1 = 2 * m1
d2 = 2 * m2
framerate = 25
points = 250
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

# Create a VisPy canvas and scene
canvas = scene.SceneCanvas(keys='interactive', size=(1920, 1080), show=True)
grid = canvas.central_widget.add_grid()
view = grid.add_view(row=1, col=0, row_span=9)
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

# Add text to the scene
view_text = grid.add_view(row=0, col=0)
text = scene.visuals.Text('Dvě rotující černé díry', color='magenta', font_size=20, pos=(.5,  .5), anchor_x='center')
view_text.camera = scene.PanZoomCamera(aspect=1)
view_text.camera.set_range()
view_text.add(text)


# Update function for the animation
def update(event):
    global t, th, dtheta
#    t += 0.05
    th += dtheta
    Z = get_gws(X, Y, th)
    surface.set_data(z=Z)
    black_hole1.transform = scene.transforms.STTransform(translate=(cm1 * np.cos(th + np.pi / 2), cm1 * np.sin(th + np.pi / 2), r))
    black_hole2.transform = scene.transforms.STTransform(translate=(cm2 * np.cos(th - np.pi / 2), cm2 * np.sin(th - np.pi / 2), r))


# Use a timer to animate the meshgrid
timer = app.Timer(interval=1./framerate, connect=update, start=True)


@canvas.events.key_press.connect
def on_key_press(event):
    if event.key.name == 'Q':
        canvas.close()  # Close the window when 'Q' is pressed

if __name__ == '__main__':
    app.run()
