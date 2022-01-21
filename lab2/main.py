from random import randint

from pyglet.gl import *
from pyglet.window import key

import pyglet

from camera import Camera
from particle_system import ParticleSystem

f = 60


class Window(pyglet.window.Window):
    global pyglet

    KEY_PRESS_OFFSET = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_minimum_size(640, 480)
        self.aspect_ratio = self.width / self.height

        self.camera = Camera(position=[1000, 0, 0], look_at=[0, 0, 0], up=[0, 1, 0])
        # self.source = [0, 0, 0]
        self.POV = 60

        texture = pyglet.image.load("textures/cestica.bmp").get_texture()
        self.particle_system = ParticleSystem(
            texture=texture, n_particles=randint(10, 40)
        )

    def update(self, Δt):
        self.particle_system.update(Δt)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.POV, self.aspect_ratio, 0.05, 10000)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(*self.camera.position, *self.camera.look_at, *self.camera.up)

        glPushMatrix()
        self.particle_system.draw()
        glPopMatrix()
        glFlush()

    def on_key_press(self, symbol, _):
        match symbol:
            case pyglet.window.key.UP:
                self.camera.look_at[1] -= self.KEY_PRESS_OFFSET
            case pyglet.window.key.DOWN:
                self.camera.look_at[1] += self.KEY_PRESS_OFFSET
            case pyglet.window.key.RIGHT:
                self.camera.look_at[2] += self.KEY_PRESS_OFFSET
            case pyglet.window.key.LEFT:
                self.camera.look_at[2] -= self.KEY_PRESS_OFFSET


if __name__ == "__main__":
    window = Window(width=1440, height=810, caption="Fireworks", resizable=True)
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    pyglet.clock.schedule_interval(window.update, 1 / f)

    pyglet.app.run()
