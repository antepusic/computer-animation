from copy import deepcopy
from math import acos, degrees
from sys import argv

import more_itertools as mit
import numpy as np
from pyglet.gl import *


window = pyglet.window.Window()


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(width) / float(height), 0.1, 256)
    glMatrixMode(GL_MODELVIEW)
    glTranslated(0, 2, -8.0)
    glRotated(60, 3, 0, 0)

    return True


@window.event
def on_draw():
    global BSpline, i, end

    glClearColor(1, 1, 1, 1)
    window.clear()
    trajectory()
    draw_object(BSpline[i] / 10)
    i += 1
    if i >= end:
        i = 0


def trajectory():
    global BSpline

    glColor3f(0, 0, 1)
    glBegin(GL_LINE_STRIP)

    for point in BSpline:
        scaled = point / 10
        glVertex3f(*scaled)

    glEnd()


def draw_object(trajectory_point):
    global tangent, φs, polygons, vertices, i

    glPushMatrix()

    opposite = -1 * trajectory_point
    glTranslatef(*trajectory_point)
    glRotatef(φs[i], *axes[i])
    glTranslatef(*opposite)

    Δ = trajectory_point - vertices[800]
    centered = [v + Δ for v in vertices]

    for polygon in polygons:
        glBegin(GL_POLYGON)

        for v_id in polygon:
            vertex = centered[v_id - 1]

            glColor3f(0, 0, 0)
            glVertex3f(*vertex)

        glEnd()

    glPopMatrix()

    normalized_tangent = tangent[i] / np.linalg.norm(tangent[i])
    normalized_tangent += trajectory_point

    glBegin(GL_LINE_STRIP)
    glColor3f(1, 0, 0)
    glVertex3f(*trajectory_point)
    glVertex3f(*normalized_tangent)
    glEnd()


def update(*args):
    pass


def load_object(path):
    with open(path, mode="r") as object_file:
        for line in object_file:
            line = line.strip()
            if len(line) == 0 or line[0] in ("#", "g"):
                continue

            entity, data = line.split(" ", maxsplit=1)
            data = data.split()
            if entity == "f":
                data = np.array(tuple(map(int, data)))
                polygons.append(data)
            elif entity == "v":
                data = np.array(tuple(map(float, data)))
                vertices.append(data)


TRAJECTORY = np.array(
    [
        [0, 0, 0],
        [0, 10, 5],
        [10, 10, 10],
        [10, 0, 15],
        [0, 0, 20],
        [0, 10, 25],
        [10, 10, 30],
        [10, 0, 35],
        [0, 0, 40],
        [0, 10, 45],
        [10, 10, 50],
        [10, 0, 55],
    ]
)

B = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]])


vertices, polygons = [], []
BSpline, tangent = [], []
axes, φs = [], []
i, end = 0, 0

if __name__ == "__main__":
    load_object(path=argv[1])

    for four_points in mit.windowed(TRAJECTORY, n=4):
        R = np.array(four_points)

        s = np.array([0, 0, 1])
        for t in np.arange(0, 1, 0.01):
            T_3 = np.array([t ** 3, t ** 2, t, 1])
            p_i = 1 / 6 * T_3 @ B @ R
            BSpline.append(p_i)

            Tꞌ_3 = np.array([3 * t ** 2, 2 * t, 1, 0])
            pꞌ_i = Tꞌ_3 @ B @ R
            tangent.append(pꞌ_i)

            e = deepcopy(pꞌ_i)
            axis = np.cross(s, e)
            axes.append(axis)
            φ = degrees(
                acos((np.multiply(s, e) / (np.linalg.norm(s) * np.linalg.norm(e)))[2])
            )
            φs.append(φ)

            s = e + p_i

    end = len(BSpline)

    pyglet.clock.schedule(update, 0.1)
    pyglet.app.run()
