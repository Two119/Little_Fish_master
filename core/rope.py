import pygame
from core.vector_class import Vector2D as Vec
from math import sqrt, degrees, radians, cos, sin, tan, pi, atan, asin
gravity_strength = Vec(78.4 * -30, 78.4 * 90)
global resultant_gravitational_force
resultant_gravitational_force = 7888.847824619258
class World:
    
    max_point_speed = 100


class Settings:
    point_size = 2
    rope_width = 5


class Point:
    def __init__(self, x, y, distance_to_child, static=False):
        self.pos = Vec(x, y)
        self.vel = Vec()
        self.accel = Vec()
        self.mass = 1

        self.static = static

        self.colour = (255, 255, 255)

        self.child = None
        self.distance_to_child = distance_to_child

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.pos.get(), Settings.point_size)

        if self.child is None:
            return

        pygame.draw.line(
            screen,
            self.colour,
            self.pos.get(),
            self.child.pos.get(),
            Settings.rope_width,
        )
        self.child.draw(screen)

    def set_child(self, child):
        self.child = child
        self.distance_to_child = self.pos.dist(self.child.pos)


class Collider:
    def __init__(self, x, y):
        self.pos = Vec(x, y)
        self.size = 10


class Rope:
    def __init__(self, x, y, length, resolution):
        self.gravity = gravity_strength.copy()
        d_len = length / resolution
        self.points = []
        for i in range(resolution):
            d_y = y - (i * (d_len / 2))
            d_x = x + (i * 10)

            self.points.append(
                Point(
                    d_x,
                    d_y,
                    distance_to_child=d_len,
                    static=(True if i == 0 else False),
                )
            )

            if i > 0:
                self.points[i - 1].set_child(self.points[i])

        for i in range(len(self.points)):
            self.points[i].mass = (i + 1) * 0.3
        self.moving = False
        self.obs=1
        self.lowest_point = None
    def draw(self, screen):
        self.points[0].draw(screen)

    def update(self, colliders, delta_time=1):
        global angle
        gravity = self.gravity

        gravity.mult(delta_time)

        for point in self.points:
            for collider in colliders:
                if not point.static and collider.pos.dist(point.pos) < collider.size:
                    d_pos = point.pos - collider.pos
                    d_pos.normalise()

                    point.accel.set(d_pos)
                    # point.pos.add(d_pos)

            if not point.static:
                point.accel.add(gravity)
                point.accel.div(point.mass)

                point.vel.add(point.accel)
                point.vel.truncate(World.max_point_speed)

                point.pos.add(point.vel)

                point.accel.mult(0)
                
            if point.child is None:
                self.lowest_point = [round(point.pos.x), round(point.pos.y)]
                #print(self.lowest_point)
                continue

            if point.child.pos.dist(point.pos) > point.distance_to_child:
                new_pos = point.child.pos - point.pos
                new_pos.normalise()
                new_pos.mult(point.distance_to_child)
                new_pos.add(point.pos)
                
                point.child.pos = new_pos
                point.child.vel.mult(0)
    def move(self, movement):
        for point in self.points:
            point.pos.x+=movement[0]
            point.pos.y+=movement[1]