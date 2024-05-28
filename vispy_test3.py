import numpy as np
import vispy
from vispy import app, scene, io, visuals
from vispy.visuals.transforms import STTransform, MatrixTransform
import time

# Create a canvas with two rows and three columns
canvas = scene.SceneCanvas(keys='interactive', size=(1920, 1080), show=True)
grid = canvas.central_widget.add_grid()

# Top-left: Logo image
img_data = io.read_png('Lisa_ESA_logo.png')
image = scene.visuals.Image(img_data)
view1 = grid.add_view(row=0, col=0)
view1.add(image)
view1.camera = scene.PanZoomCamera(aspect=1)
view1.camera.flip = (False, True, False)
view1.camera.set_range()

# Top-middle: Rotating sphere
sphere = scene.visuals.Sphere(radius=1, rows=30, cols=30, method='latitude')
view2 = grid.add_view(row=0, col=1, col_span=2, bgcolor="#ffffff")
view2.add(sphere)
view2.camera = scene.TurntableCamera(fov=0)

# Top-right: Matrix-style moving numbers
matrix_text = scene.visuals.Text('', color='green', font_size=20)
view3 = grid.add_view(row=0, col=4, row_span=4)
view3.add(matrix_text)
view3.camera = scene.PanZoomCamera(aspect=1)
view3.camera.set_range()

# Second row: Sinusoidal curve
plot = scene.visuals.Line(color='yellow')
view4 = grid.add_view(row=2, col=0, col_span=3)
view4.add(plot)
view4.camera = scene.PanZoomCamera(aspect=1)
view4.camera.set_range()

# Bottom row: Time series plot for space bar pressing
time_series = scene.visuals.Line(color='red')
view5 = grid.add_view(row=3, col=0, col_span=4)
view5.add(time_series)
view5.camera = scene.PanZoomCamera(aspect=1)
view5.camera.set_range()

# Big text overlay for exceeding space bar presses
big_text = scene.visuals.Text('', color='red', font_size=2500, bold=True, parent=canvas.scene)
big_text.pos = canvas.size[0] / 2, canvas.size[1] / 2
big_text.visible = False

# Animation and interaction parameters
start_time = time.time()
rotation_angle = 0
space_press_times = []
update_count = 0  # Counter for updates

# Update functions
def update(event):
    global rotation_angle, space_press_times, update_count
    
    current_time = time.time() - start_time
    
    # Rotating sphere
    rotation_angle += 2 * np.pi * 1.0 / 60  # 1 Hz rotation
    sphere.transform = MatrixTransform()
    sphere.transform.rotate(rotation_angle, (0, 1, 0))
    
    # Sinusoidal curve
    t = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(t + rotation_angle)
    plot.set_data(np.c_[t, y])

    # Update matrix-style text every 10 updates
    if update_count % 10 == 0:
        matrix_text.text = '\n'.join([''.join([str(np.random.randint(10)) for _ in range(10)]) for _ in range(10)])
    update_count += 1
    
    # Time series plot
    if space_press_times:
        times = np.array(space_press_times) - start_time
        data = np.c_[times, np.ones_like(times)]
        time_series.set_data(data)

    # Check space press times
    if len(space_press_times) > 10:
        big_text.text = "SPACE BAR PRESSED OVER 30 TIMES!"
        big_text.visible = True
        restart()

    canvas.update()

def restart():
    global start_time, rotation_angle, space_press_times, update_count
    time.sleep(2)  # Pause to display the message
    start_time = time.time()
    rotation_angle = 0
    space_press_times = []
    update_count = 0
    big_text.visible = False

# Event handler for key presses
@canvas.events.key_press.connect
def on_key_press(event):
    if event.key == 'A':
        space_press_times.append(time.time())
    elif event.key == 'Q' or event.key == 'Escape':
        app.quit()

# Timer for updating the canvas
timer = app.Timer(interval='auto', connect=update, start=True)

if __name__ == '__main__':
    app.run()
