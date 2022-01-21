from pyrr import Vector3


class Particle:
    def __init__(self, size, position, direction):
        self.size = size
        self.position = position.copy()

        self.start_velocity = direction.copy()
        self.down_velocity = Vector3([0, 0, 0])

        self.age = 0

    def update(self, Δt):
        self.position += self.start_velocity
        if self.size > 0:
            self.size -= 0.4

        self.down_velocity[1] -= 10 * Δt
        self.position += self.down_velocity

        self.age += 1
