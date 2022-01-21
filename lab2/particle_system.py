from math import cos, pi, sin, sqrt
from random import gauss, randint

from pyglet.gl import *
from pyrr import Vector3

from particle import Particle

LIFESPAN = 300


class ParticleSystem:
    def __init__(self, texture, n_particles=10, particle_size=50, lifespan=LIFESPAN):
        self.particles = self.new_particles(n_particles, particle_size)
        self.particle_size = particle_size
        self.texture = texture
        self.lifespan = lifespan

        self.timer = 0
        self.next_explosion = self.until_next_explosion()

    @staticmethod
    def new_particles(n_particles, particle_size):
        # Fibonacci sphere
        φ = pi * (3 - sqrt(5))
        center = Vector3([gauss(0, 100), gauss(0, 100), gauss(0, 50)])
        particles = []
        for n in range(n_particles):
            y = 1 - (n / (n_particles - 1)) * 2
            radius = sqrt(1 - y * y)
            θ = φ * n
            x = cos(θ) * radius
            z = sin(θ) * radius
            particles.append(Particle(particle_size, center, [3 * x, 3 * y, 3 * z]))

        return particles

    @staticmethod
    def until_next_explosion():
        return randint(0, 150)

    def update(self, Δt):
        self.timer += 1

        for particle in self.particles:
            particle.update(Δt)
            if particle.age >= self.lifespan:
                self.particles.remove(particle)

        if self.timer == self.next_explosion:
            self.particles += self.new_particles(
                n_particles=randint(10, 50), particle_size=self.particle_size
            )
            self.next_explosion += self.until_next_explosion()

    def draw(self):
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)

        glPushMatrix()
        for particle in self.particles:
            matrix = (GLfloat * 16)()
            glGetFloatv(GL_MODELVIEW_MATRIX, matrix)
            matrix = list(matrix)
            camera_up = Vector3([matrix[1:11:4]])
            camera_right = Vector3([matrix[0:11:4]])

            size = particle.size
            v1 = particle.position + camera_right * size + camera_up * -size
            v2 = particle.position + camera_right * size + camera_up * size
            v3 = particle.position + camera_right * -size + camera_up * -size
            v4 = particle.position + camera_right * -size + camera_up * size

            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex3f(*v3)
            glTexCoord2f(1, 0)
            glVertex3f(*v4)
            glTexCoord2f(1, 1)
            glVertex3f(*v2)
            glTexCoord2f(0, 1)
            glVertex3f(*v1)
            glEnd()

        glPopMatrix()
        glDisable(GL_BLEND)
        glDisable(self.texture.target)
