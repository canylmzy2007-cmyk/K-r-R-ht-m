"""Articulated infected dock workers and an original first-person carbine."""

import math
from direct.actor.Actor import Actor
from panda3d.core import Point3, Vec3, DepthOffsetAttrib


def joint(p, name, x, y, z):
    j = p.attachNewNode(name)
    j.setPos(x, y, z)
    return j


class Infected:
    def __init__(self, app, x, y, variant=0):
        self.app = app
        self.x, self.y = x, y
        self.phase = variant * 1.73
        self.hp = 100
        self.speed = 1.23 + 0.11 * (variant % 3)
        self.windup = -1.0
        self.cool = 0.7
        self.flash = 0.0
        self.limp = 0.0
        self.dead = False
        self.age = 0.0
        self.fallside = 1
        self.hit_side = 1
        self.last_zone = "gövde"
        self.root = app.render.attachNewNode("enfekte")
        self.root.setPos(x, y, 0)
        self.blob = app.art.shadow(app.render, x, y, 1.28, 1.49, 0.88)
        self.actor = Actor(app.art.worker)
        self.actor.reparentTo(self.root)
        cloth = self.actor.findTexture("tulum")
        if cloth and variant % 3:
            self.actor.replaceTexture(cloth, app.art.tex[f"tulum{variant % 3}"])

        def bone(name, parent):
            node = self.actor.controlJoint(None, "modelRoot", name)
            node.reparentTo(parent)
            return node

        self.hips = bone("hips", self.root)
        self.rest_height = self.hips.getZ()
        self.chest = bone("chest", self.hips)
        self.neck = bone("neck", self.chest)
        self.head = bone("head", self.neck)
        self.arms = []
        self.forearms = []
        self.thighs = []
        self.shins = []
        self.volumes = [
            (self.head, (0, -0.050, 0.033), (0.103, 0.124, 0.146), "baş"),
            (self.chest, (0, -0.016, 0.235), (0.203, 0.142, 0.272), "gövde"),
            (self.hips, (0, -0.016, -0.01), (0.193, 0.146, 0.158), "gövde"),
        ]
        for sign, s in ((-1, "r"), (1, "l")):
            arm = bone("arm" + s, self.chest)
            fore = bone("fore" + s, arm)
            thigh = bone("leg" + s, self.hips)
            shin = bone("shin" + s, thigh)
            self.arms.append(arm)
            self.forearms.append(fore)
            self.thighs.append(thigh)
            self.shins.append(shin)

            def segment(start, end, rx, ry, zone):
                v = Vec3(end)
                anchor = start.attachNewNode("vuruş hacmi")
                anchor.setPos(v * 0.5)
                anchor.lookAt(start, Point3(*end))
                anchor.setP(anchor.getP() + 90)
                self.volumes.append(
                    (anchor, (0, 0, 0), (rx, ry, v.length() * 0.56), zone)
                )

            segment(arm, fore.getPos(), 0.073, 0.075, "gövde")
            segment(fore, (sign * 0.174, -0.234, -0.190), 0.066, 0.062, "gövde")
            segment(thigh, shin.getPos(), 0.106, 0.11, "bacak")
            segment(shin, (sign * 0.073, -0.018, -0.46), 0.083, 0.09, "bacak")
            eye_x = sign * 0.0343
            app.art.oval(
                self.head,
                (eye_x, -0.121, 0.0345),
                (0.030, 0.032, 0.029),
                (0.67, 0.68, 0.59),
            )
            app.art.oval(
                self.head,
                (eye_x, -0.137, 0.035),
                (0.012, 0.004, 0.012),
                (0.33, 0.35, 0.28),
            )
        self.pose(0, False)

    def pose(self, dt, moving=True):
        self.phase += dt * (5.8 if moving else 1.25)
        p = self.phase
        step = math.sin(p)
        amount = 1 if moving else 0.12
        attack = max(0, 1 - abs(self.windup - 0.16) / 0.22) if self.windup >= 0 else 0
        self.hips.setZ(self.rest_height - 0.025 + 0.023 * abs(math.cos(p)) * amount)
        self.chest.setHpr(
            step * 6 * amount,
            16 + attack * 16 - self.flash * 16,
            math.sin(p * 0.51) * 3 + self.hit_side * self.flash * 12,
        )
        self.neck.setP(9)
        self.head.setHpr(
            math.sin(p * 0.32) * 9,
            -14 + step * 3 - self.flash * 18,
            self.hit_side * self.flash * 15 - 8,
        )
        for i, side in enumerate((-1, 1)):
            self.thighs[i].setHpr(
                0, step * side * (14 if self.limp else 23) * amount, side * 3.5
            )
            self.shins[i].setP(-max(0, step * side) * 25 * amount - 3)
            self.arms[i].setHpr(
                side * (-6),
                -29 + side * 12 + step * side * 13 * amount - attack * 42,
                side * (29 - self.flash * 15),
            )
            self.forearms[i].setP(
                -10 - side * 6 - step * side * 8 * amount - attack * 9
            )
        self.root.setPos(self.x, self.y, 0)
        self.blob.setPos(self.x, self.y, 0.022)

    def intersect(self, origin, direction, limit):
        if self.dead:
            return None
        if (self.x - origin.x) ** 2 + (self.y - origin.y) ** 2 > (limit + 1.9) ** 2:
            return None
        best = None
        for node, center, radii, zone in self.volumes:
            o = node.getRelativePoint(self.app.render, origin)
            v = node.getRelativeVector(self.app.render, direction)
            q = [(o[i] - center[i]) / radii[i] for i in range(3)]
            u = [v[i] / radii[i] for i in range(3)]
            a = sum(s * s for s in u)
            b = sum(s * t for s, t in zip(q, u))
            c = sum(s * s for s in q) - 1
            disc = b * b - a * c
            if disc < 0:
                continue
            t = (-b - math.sqrt(disc)) / a
            if 0 <= t < limit:
                best = (t, zone)
                limit = t
        return best

    def hit(self, zone, side):
        self.last_zone = zone
        self.flash = 1
        self.hit_side = side
        self.windup = -1
        self.cool = max(0.25, self.cool)
        self.hp -= {"baş": 110, "gövde": 42, "bacak": 29}[zone]
        if zone == "bacak":
            self.limp = 1.7
        if self.hp <= 0:
            self.dead = True
            self.age = 0
            self.fallside = side
        return self.dead

    def collapse(self, dt):
        self.age += dt
        f = min(1, self.age / 0.53)
        v = f * f * (3 - 2 * f)
        self.root.setP(-79 * v)
        self.root.setR(self.fallside * 20 * v)
        self.thighs[0].setP(24 * v)
        self.shins[0].setP(-38 * v)
        self.arms[0].setP(-42 + 55 * v)
        self.arms[1].setP(-15 + 33 * v)
        self.root.setZ(0.13 * v)
        if self.age > 4.6:
            self.root.setZ(0.13 - min(1, (self.age - 4.6) / 1.1) * 0.68)
        return self.age > 5.7

    def remove(self):
        self.actor.cleanup()
        self.root.removeNode()
        self.blob.removeNode()


class Carbine:
    def __init__(self, app):
        art = app.art
        root = app.camera.attachNewNode("karabina")
        self.root = root
        root.setDepthTest(True)
        root.setDepthWrite(True)
        root.setAttrib(DepthOffsetAttrib.make(0, 0, 0.09))
        root.setScale(0.84)
        root.setBin("fixed", 30)
        root.setFogOff()
        box, oval = art.box, art.oval
        gun = root.attachNewNode("metal gövde")
        alloy = (0.245, 0.263, 0.266)
        black = (0.105, 0.125, 0.13)
        tan = (0.36, 0.34, 0.255)
        # The sight line is at local x=0, z=.115.
        box(gun, (0, 0.06, 0.005), (0.120, 0.36, 0.103), alloy, "metal")
        box(gun, (0, 0.045, -0.054), (0.113, 0.232, 0.048), black)
        box(gun, (0, 0.315, 0.002), (0.106, 0.23, 0.103), tan, "metal")
        for side in (-1, 1):
            for i in range(5):
                box(
                    gun,
                    (side * 0.054, 0.232 + i * 0.037, 0.013),
                    (0.004, 0.021, 0.025),
                    black,
                )
            box(gun, (side * 0.061, 0.091, 0.020), (0.005, 0.103, 0.024), black)
        art.beam(gun, (0, 0.412, 0.005), (0, 0.65, 0.005), 0.044, alloy, round_=True)
        art.beam(gun, (0, 0.618, 0.005), (0, 0.718, 0.005), 0.059, black, round_=True)
        box(gun, (0, 0.158, 0.065), (0.054, 0.53, 0.017), black)
        for i in range(23):
            box(gun, (0, -0.088 + i * 0.022, 0.080), (0.062, 0.012, 0.013), alloy)
        for yy in (-0.064, 0.395):
            box(gun, (0, yy, 0.088), (0.066, 0.035, 0.026), black)
        for side in (-1, 1):
            box(gun, (side * 0.032, -0.064, 0.106), (0.014, 0.032, 0.031), black)
            box(gun, (side * 0.026, 0.395, 0.110), (0.009, 0.022, 0.041), black)
        box(gun, (0, 0.395, 0.104), (0.010, 0.021, 0.029), alloy)
        box(gun, (0, -0.19, -0.014), (0.08, 0.18, 0.08), black)
        stock = box(gun, (0, -0.304, -0.037), (0.108, 0.186, 0.135), tan, "metal")
        box(gun, (0, -0.40, -0.039), (0.117, 0.037, 0.144), black)
        grip = box(gun, (0, -0.055, -0.124), (0.071, 0.088, 0.151), black)
        grip.setP(-13)
        self.mag = box(root, (0, 0.117, -0.147), (0.077, 0.10, 0.196), tan, "metal")
        self.mag.setP(-8)
        for xx in (-0.040, 0.040):
            for yy in (0.091, 0.123, 0.149):
                box(gun, (xx, yy, -0.137), (0.003, 0.008, 0.114), black)
        # Gloved hands and jacket sleeves, shaped to the two contact points.
        glove = (0.27, 0.245, 0.19)
        sleeve = (0.25, 0.295, 0.266)
        for a, b, r in (
            ((0.08, -0.27, -0.24), (0.035, -0.062, -0.125), 0.101),
            ((-0.23, -0.20, -0.30), (-0.058, 0.255, -0.098), 0.114),
        ):
            art.beam(gun, a, b, r, sleeve, round_=True)
        oval(gun, (0.031, -0.055, -0.106), (0.105, 0.123, 0.102), glove, "deri")
        oval(gun, (-0.043, 0.248, -0.071), (0.125, 0.152, 0.088), glove, "deri")
        for i in range(4):
            oval(
                gun,
                (-0.048, 0.193 + i * 0.034, -0.041),
                (0.067, 0.037, 0.065),
                glove,
                "deri",
            )
        gun.flattenStrong()
        self.tip = joint(root, "namlu", 0, 0.73, 0.006)
        self.flash = art.oval(
            self.tip, (0, 0.10, 0), (0.069, 0.25, 0.064), (1, 0.73, 0.20)
        )
        self.flash.setLightOff()
        self.flash.hide()

    def pose(self, aim, kick, t, reload_fraction, moving):
        lower = math.sin(math.pi * reload_fraction) if reload_fraction >= 0 else 0
        sway = math.sin(t) * moving * (1 - aim)
        self.root.setPos(
            0.181 * (1 - aim) + 0.012 * sway,
            0.503 + 0.028 * aim - 0.064 * kick,
            -0.150 + 0.0534 * aim - 0.10 * lower + 0.006 * math.cos(2 * t) * moving,
        )
        self.root.setHpr(-lower * 11, kick * 4 - lower * 24, lower * 24 - sway * 1.4)
        self.mag.setZ(-0.147 - 0.095 * lower)
        if kick > 0.76 and not lower:
            self.flash.show()
        else:
            self.flash.hide()
