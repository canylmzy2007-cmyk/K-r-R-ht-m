"""Kör Rıhtım — single-player 3D survival FPS. Run this file to play."""

from pathlib import Path
import math, random, sys, os

# Make packaged Panda plug-ins visible when Visual Studio starts Python directly.
if sys.platform == "win32":
    _plugins = Path(sys.executable).resolve().parent / "panda3d"
    if _plugins.is_dir():
        _dll_path = os.add_dll_directory(str(_plugins))
        os.environ["PATH"] = str(_plugins) + os.pathsep + os.environ.get("PATH", "")

from panda3d.core import (
    loadPrcFileData,
    WindowProperties,
    Vec3,
    Point3,
    Filename,
    ClockObject,
    LineSegs,
    TransparencyAttrib,
)

HEADLESS = "--offscreen" in sys.argv
loadPrcFileData(
    "KorRihtim",
    "window-title Kör Rıhtım | Son Vapur\nwin-size 1280 720\n"
    "background-color 0.42 0.50 0.53\nsync-video true\ntextures-power-2 none\n"
    "audio-library-name p3openal_audio\nframebuffer-multisample 1\nmultisamples 2\n"
    "notify-level warning\nmodel-cache-dir\n",
)
if HEADLESS:
    loadPrcFileData(
        "QA",
        "window-type offscreen\nload-display p3headlessgl\naudio-library-name null\n"
        "win-size 1000 562\nframebuffer-multisample 0\nmultisamples 0\nsync-video false",
    )
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from art import Art, ASSETS
from actors import Infected, Carbine
from layout import (
    START,
    EXIT,
    PORTALS,
    WAVES,
    Navigation,
    slide,
    support,
    wall_distance,
)
from story_ui import StoryInterface as Interface
from yard import build

MAGAZINE = 24
CACHE = (-1.65, -18.8)


class Game(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.camLens.setNearFar(0.045, 175)
        self.camLens.setFov(82)
        self.art = Art(self.loader)
        self.beacon = build(self)
        self.nav = Navigation()
        self.gun = Carbine(self)
        self.enemies = []
        self.effects = []
        self.held = set()
        self.keys = ("w", "a", "s", "d", "shift", "mouse1", "mouse3")
        self.muted = False
        self.sensitivity = 0.13
        self.sounds = {}
        self.sound_slot = {}
        for name, count in [
            ("ates", 5),
            ("isabet", 3),
            ("adim", 2),
            ("hirilti", 2),
            ("uyari", 1),
            ("sarjor", 1),
            ("ortam", 1),
        ]:
            path = Filename.fromOsSpecific(str(ASSETS / (name + ".wav")))
            self.sounds[name] = [self.loader.loadSfx(path) for i in range(count)]
            self.sound_slot[name] = 0
        self.ambient = self.sounds["ortam"][0]
        self.ambient.setLoop(True)
        self.ambient.setVolume(0.44)
        self.ambient.play()
        self.cache = self.render.attachNewNode("ikmal noktası")
        self.art.box(
            self.cache,
            (CACHE[0], CACHE[1], 0.37),
            (1.54, 0.83, 0.74),
            (0.48, 0.53, 0.38),
            "metal",
        )
        for xx in (-0.54, 0.54):
            self.art.box(
                self.cache,
                (CACHE[0] + xx, CACHE[1], 0.38),
                (0.069, 0.85, 0.77),
                (0.21, 0.23, 0.18),
            )
        self.art.text3(
            self.cache,
            "İKMAL",
            (CACHE[0], CACHE[1] + 0.43, 0.34),
            0.17,
            (0.87, 0.86, 0.65),
            180,
        )
        self.cache.flattenStrong()
        self.ui = Interface(self)
        self.mode = ""
        self.tour = 0.0
        self.accumulator = 0.0
        self.ignore_mouse = 0
        self.foreground = True
        self.rng = random.Random()
        for key in self.keys:
            self.accept(key, self.press, [key])
            self.accept(key + "-up", self.release, [key])
        for key, fn in [
            ("enter", self.enter),
            ("escape", self.escape),
            ("r", self.reload),
            ("space", self.jump),
            ("e", self.interact),
            ("m", self.mute),
            ("f1", lambda: self.adjust(-0.01)),
            ("f2", lambda: self.adjust(0.01)),
        ]:
            self.accept(key, fn)
        # Keep ShowBase's own resize and window-close handler registered.
        self.window_listener = DirectObject()
        self.window_listener.accept("window-event", self.window_changed)
        self.title()
        self.taskMgr.add(self.update, "oyun", sort=10)

    def play_sound(self, name, volume=1.0, rate=1.0):
        if self.muted:
            return
        i = self.sound_slot[name]
        sound = self.sounds[name][i]
        self.sound_slot[name] = (i + 1) % len(self.sounds[name])
        sound.setVolume(volume)
        sound.setPlayRate(rate)
        sound.play()

    def mute(self):
        self.muted = not self.muted
        if self.muted:
            for group in self.sounds.values():
                for sound in group:
                    sound.stop()
        else:
            self.ambient.play()
        self.ui.settings()

    def adjust(self, delta):
        self.sensitivity = round(max(0.04, min(0.4, self.sensitivity + delta)), 2)
        self.ui.settings()

    def lock(self, on):
        self.held.clear()
        self.ignore_mouse = 2
        if HEADLESS:
            return
        props = WindowProperties()
        props.setCursorHidden(on)
        self.win.requestProperties(props)
        if on:
            self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)

    def window_changed(self, window):
        if window != self.win or not hasattr(self, "ui") or HEADLESS:
            return
        fg = window.getProperties().getForeground()
        if self.foreground and not fg and self.mode == "play":
            self.pause()
        self.foreground = fg
        if abs(self.getAspectRatio() - self.ui.width) > 0.005:
            self.ui.size()

    def cleanup(self):
        for enemy in self.enemies:
            enemy.remove()
        for node, *_ in self.effects:
            node.removeNode()
        self.enemies.clear()
        self.effects.clear()

    def title(self):
        self.cleanup()
        self.mode = "title"
        self.lock(False)
        self.gun.root.hide()
        self.beacon.hide()
        self.camLens.setFov(65)
        self.tour = 0
        self.ui.show("title")
        for x, y, h, v in (
            (1.58, -5.40, -12, 1),
            (3.10, 2.2, -5, 2),
            (-1.3, 3.6, -9, 1),
        ):
            zombie = Infected(self, x, y, v)
            zombie.root.setH(h)
            zombie.pose(0, False)
            self.enemies.append(zombie)
        self.title_camera()

    def title_camera(self):
        self.camera.setPos(0.88 + math.sin(self.tour * 0.09) * 0.26, -7.8, 1.49)
        self.camera.lookAt(0.64, 3.8, 1.62)

    def start(self):
        self.cleanup()
        self.mode = "play"
        self.lock(True)
        self.beacon.hide()
        self.gun.root.show()
        self.x, self.y = START
        self.feet = 0.0
        self.vz = 0.0
        self.grounded = True
        self.heading = 0.0
        self.pitch = 0.0
        self.aim = 0.0
        self.kick = 0.0
        self.step_t = 0.0
        self.moving = 0.0
        self.walk_phase = 0.0
        self.hp = 100.0
        self.mag = MAGAZINE
        self.reserve = 96
        self.reload_time = 0.0
        self.shot_delay = 0.0
        self.damage_t = 0.0
        self.hit_t = 0.0
        self.hit_head = False
        self.hit_label = ""
        self.wave = 0
        self.kills = 0
        self.head_hits = 0
        self.pending = 0
        self.phase = "prep"
        self.countdown = 2.5
        self.spawn_delay = 0.0
        self.bark = 3.0
        self.cache_delay = 0.0
        self.accumulator = 0
        self.banner = ("TERMİNAL 07", "Üç dalgayı atlat. Tahliye kapısı kuzeyde.")
        self.banner_t = 2.5
        self.ui.show("play")
        self.update_camera()
        self.ui.update(self)

    def enter(self):
        if self.mode in ("title", "lost", "won"):
            self.start()
        elif self.mode == "pause":
            self.resume()

    def escape(self):
        if self.mode == "play":
            self.pause()
        elif self.mode == "pause":
            self.resume()
        elif self.mode in ("lost", "won"):
            self.title()
        else:
            self.userExit()

    def pause(self):
        if self.mode != "play":
            return
        self.mode = "pause"
        self.lock(False)
        self.ui.show("pause")

    def resume(self):
        if self.mode != "pause":
            return
        self.mode = "play"
        self.accumulator = 0
        self.lock(True)
        self.ui.show("play")
        self.ui.update(self)

    def finish(self, won):
        self.mode = "won" if won else "lost"
        self.lock(False)
        self.gun.root.hide()
        self.ui.show(self.mode)
        self.play_sound("uyari", 0.58, 1.1 if won else 0.65)

    def press(self, key):
        if self.mode == "play" and (key != "mouse1" or self.ignore_mouse == 0):
            self.held.add(key)

    def release(self, key):
        self.held.discard(key)

    def jump(self):
        if self.mode == "play" and self.grounded:
            self.vz = 5.28
            self.grounded = False

    def reload(self):
        if (
            self.mode == "play"
            and self.mag < MAGAZINE
            and self.reserve > 0
            and self.reload_time <= 0
        ):
            self.reload_time = 1.60
            self.play_sound("sarjor", 0.75)

    def context_hint(self):
        if self.phase == "exit":
            dist = math.hypot(self.x - EXIT[0], self.y - EXIT[1])
            if dist < 2.5:
                return "E  •  Tahliye ol"
            return f"Kuzey kapısına ulaş   •   {dist:.0f} m"
        if math.hypot(self.x - CACHE[0], self.y - CACHE[1]) < 2.65:
            return "E  •  Mühimmat al"
        return ""

    def interact(self):
        if self.mode != "play":
            return
        if (
            self.phase == "exit"
            and math.hypot(self.x - EXIT[0], self.y - EXIT[1]) < 2.5
        ):
            self.finish(True)
        elif (
            math.hypot(self.x - CACHE[0], self.y - CACHE[1]) < 2.65
            and self.cache_delay <= 0
        ):
            self.reserve = max(self.reserve, 96)
            self.cache_delay = 1.0
            self.banner = ("İKMAL TAMAM", "Yedek mühimmat dolduruldu.")
            self.banner_t = 1.5
            self.play_sound("sarjor", 0.65)

    def mouse_look(self):
        if HEADLESS or not self.foreground:
            return
        p = self.win.getPointer(0)
        cx = self.win.getXSize() // 2
        cy = self.win.getYSize() // 2
        dx = p.getX() - cx
        dy = p.getY() - cy
        if self.ignore_mouse > 0:
            self.ignore_mouse -= 1
        else:
            speed = self.sensitivity * (1 - 0.39 * self.aim)
            self.heading = (self.heading - dx * speed) % 360
            self.pitch = max(-78, min(78, self.pitch - dy * speed))
        if dx or dy:
            self.win.movePointer(0, cx, cy)

    def update_camera(self):
        bob = math.sin(self.walk_phase * 2) * 0.023 * self.moving * (1 - 0.8 * self.aim)
        self.camera.setPos(self.x, self.y, self.feet + 1.58 + bob)
        self.camera.setHpr(self.heading, self.pitch + self.kick * 1.3, 0)
        self.camLens.setFov(82 - 24 * self.aim)
        self.gun.pose(
            self.aim,
            self.kick,
            self.walk_phase,
            1 - self.reload_time / 1.60 if self.reload_time > 0 else -1,
            self.moving,
        )

    def move(self, dt):
        forward = int("w" in self.held) - int("s" in self.held)
        side = int("d" in self.held) - int("a" in self.held)
        length = math.hypot(forward, side)
        self.moving = float(length > 0 and self.grounded)
        run = (
            "shift" in self.held
            and forward > 0
            and "mouse3" not in self.held
            and "mouse1" not in self.held
        )
        speed = 5.3 if run else 3.60 - 1.44 * self.aim
        if length > 0:
            a = math.radians(self.heading)
            c, s = math.cos(a), math.sin(a)
            dx = (side * c - forward * s) * speed * dt / length
            dy = (side * s + forward * c) * speed * dt / length
            self.x, self.y = slide(self.x, self.y, dx, dy, 0.32, self.feet)
            self.walk_phase += dt * speed * 2.06
            if self.grounded:
                self.step_t -= dt
                if self.step_t <= 0:
                    self.play_sound(
                        "adim", 0.43 if run else 0.29, self.rng.uniform(0.88, 1.12)
                    )
                    self.step_t = 0.31 if run else 0.415
        floor = support(self.x, self.y, self.feet)
        self.vz -= 13.4 * dt
        self.feet += self.vz * dt
        if self.feet <= floor:
            self.feet = floor
            self.vz = 0.0
            self.grounded = True
        else:
            self.grounded = False
        target = float("mouse3" in self.held and self.reload_time <= 0)
        self.aim += (target - self.aim) * (1 - math.exp(-15 * dt))

    def spawn(self):
        first = self.wave == 1 and self.pending == WAVES[0]
        if first:
            x, y = 0.1, -3.2
        else:
            portals = [
                p for p in PORTALS if math.hypot(p[0] - self.x, p[1] - self.y) > 8
            ]
            portals.sort(
                key=lambda p: sum(
                    math.hypot(p[0] - z.x, p[1] - z.y) < 3
                    for z in self.enemies
                    if not z.dead
                )
            )
            best = [
                p
                for p in portals
                if all(
                    z.dead or math.hypot(p[0] - z.x, p[1] - z.y) > 1.0
                    for z in self.enemies
                )
            ]
            x, y = self.rng.choice(best or portals or list(PORTALS))
        z = Infected(self, x, y, (self.wave * 3 + self.pending) % 3)
        z.speed += 0.16 * (self.wave - 1)
        z.root.setH(math.degrees(math.atan2(self.x - x, y - self.y)))
        z.pose(0)
        self.enemies.append(z)
        self.pending -= 1

    def mission(self, dt):
        if self.phase == "prep":
            self.countdown -= dt
            if self.countdown <= 0:
                self.wave += 1
                self.phase = "wave"
                self.pending = WAVES[self.wave - 1]
                self.spawn_delay = 0
                self.banner = (
                    f"DALGA  {self.wave:02d}",
                    "Terminal çevresinde hareket var.",
                )
                self.banner_t = 2.0
                self.play_sound("uyari", 0.55)
        if self.phase == "wave":
            self.spawn_delay -= dt
            if self.pending and self.spawn_delay <= 0:
                self.spawn()
                self.spawn_delay = max(0.72, 1.48 - 0.18 * self.wave)
            if not self.pending and all(z.dead for z in self.enemies):
                if self.wave == len(WAVES):
                    self.phase = "exit"
                    self.beacon.show()
                    self.banner = (
                        "KAPI AÇIK",
                        "Yeşil ışıklara git. Kapıda E tuşuna bas.",
                    )
                else:
                    self.phase = "prep"
                    self.countdown = 5.0
                    self.reserve = min(144, self.reserve + 48)
                    self.hp = min(100, self.hp + 20)
                    self.banner = ("DALGA TEMİZ", "+48 mühimmat   /   +20 sağlık")
                self.banner_t = 3.0
                self.play_sound("uyari", 0.62, 1.22)

    def ai(self, dt):
        self.nav.aim(self.x, self.y)
        live = [z for z in self.enemies if not z.dead]
        for z in self.enemies[:]:
            if z.dead:
                if z.collapse(dt):
                    z.remove()
                    self.enemies.remove(z)
                continue
            dx = self.x - z.x
            dy = self.y - z.y
            dist = math.hypot(dx, dy)
            z.cool -= dt
            z.flash = max(0, z.flash - dt * 4.6)
            z.limp = max(0, z.limp - dt)
            gap = Vec3(dx, dy, self.feet + 0.4)
            direct = (
                dist < 4.5
                and wall_distance(
                    Point3(z.x, z.y, 1.13), gap.normalized(), gap.length() + 0.01
                )
                >= gap.length() - 0.05
            )
            reach = dist < 1.24 and self.feet < 1.27 and direct
            if z.windup >= 0:
                z.windup -= dt
                if z.windup <= 0:
                    if reach:
                        self.hurt(9 + self.wave)
                    z.windup = -1
                    z.cool = 1.30
                    if self.mode != "play":
                        return
            elif reach and z.cool <= 0:
                z.windup = 0.39
                self.play_sound("hirilti", 0.34, self.rng.uniform(0.88, 1.15))
            if (not reach or dist > 0.96) and z.windup < 0:
                tx, ty = (
                    (self.x, self.y)
                    if direct
                    else self.nav.waypoint(z.x, z.y, self.x, self.y)
                )
                mx, my = tx - z.x, ty - z.y
                length = math.hypot(mx, my)
                if length > 0.001:
                    mx /= length
                    my /= length
                    for other in live:
                        if other is z:
                            continue
                        ex, ey = z.x - other.x, z.y - other.y
                        sep = math.hypot(ex, ey)
                        if 0.001 < sep < 0.59:
                            strength = (0.59 - sep) * 2.8
                            mx += ex / sep * strength
                            my += ey / sep * strength
                    speed = (
                        z.speed
                        * (0.55 if z.limp > 0 else 1)
                        * (1 - 0.7 * z.flash)
                        * dt
                        / max(1, math.hypot(mx, my))
                    )
                    z.x, z.y = slide(z.x, z.y, mx * speed, my * speed, 0.31)
                    face = math.degrees(math.atan2(mx, -my))
                    z.root.setH(
                        z.root.getH()
                        + ((face - z.root.getH() + 180) % 360 - 180) * min(1, 8 * dt)
                    )
            elif dist > 0:
                z.root.setH(math.degrees(math.atan2(dx, -dy)))
            z.pose(dt, not reach)
        self.bark -= dt
        if self.bark <= 0 and live:
            near = min(math.hypot(self.x - z.x, self.y - z.y) for z in live)
            self.play_sound(
                "hirilti", max(0.05, 0.35 - near * 0.014), self.rng.uniform(0.75, 1.13)
            )
            self.bark = self.rng.uniform(2.0, 4.4)

    def hurt(self, n):
        self.hp = max(0, self.hp - n)
        self.damage_t = 0.48
        self.play_sound("isabet", 0.70, 0.73)
        if self.hp <= 0:
            self.finish(False)

    def fire(self):
        if self.mag <= 0:
            if self.reserve > 0:
                self.reload()
            self.shot_delay = 0.17
            return
        self.shot_delay = 0.132
        self.mag -= 1
        origin = self.camera.getPos(self.render)
        q = self.camera.getQuat(self.render)
        spread = (0.0020 + self.moving * 0.0045 + self.kick * 0.006) * (
            1 - 0.85 * self.aim
        )
        ang = self.rng.uniform(0, 2 * math.pi)
        r = math.sqrt(self.rng.random()) * spread
        direction = (
            q.getForward()
            + q.getRight() * math.cos(ang) * r
            + q.getUp() * math.sin(ang) * r
        )
        direction.normalize()
        maximum = wall_distance(origin, direction, 80)
        victim = None
        part = ""
        for z in self.enemies:
            test = z.intersect(origin, direction, maximum)
            if test:
                maximum, part = test
                victim = z
        point = origin + direction * maximum
        self.kick = min(1.4, self.kick + 0.88)
        self.play_sound("ates", 0.77, self.rng.uniform(0.96, 1.04))
        if victim:
            impact = victim.root.getRelativePoint(self.render, point)
            kill = victim.hit(part, 1 if impact.x >= 0 else -1)
            self.hit_head = part == "baş"
            self.head_hits += int(self.hit_head)
            self.hit_t = 0.23
            self.hit_label = (
                "BAŞ İSABETİ" if self.hit_head else ("ETKİSİZ" if kill else "")
            )
            self.kills += int(kill)
            self.play_sound("isabet", 0.48, 1.1 if self.hit_head else 0.87)
        # Spatial trail, short-lived impact particles and an ejected case.
        line = LineSegs("iz")
        line.setThickness(1.35)
        line.setColor(1, 0.79, 0.42, 0.70)
        muzzle = self.gun.tip.getPos(self.render)
        line.moveTo(muzzle)
        line.drawTo(point)
        n = self.render.attachNewNode(line.create())
        n.setLightOff()
        n.setTransparency(TransparencyAttrib.MAlpha)
        self.effects.append((n, 0.042, None))
        if maximum < 79:
            for _ in range(4):
                v = (
                    Vec3(
                        self.rng.uniform(-0.9, 0.9),
                        self.rng.uniform(-0.9, 0.9),
                        self.rng.uniform(0.2, 1.7),
                    )
                    - direction * 0.5
                )
                color = (0.36, 0.29, 0.22) if victim else (0.9, 0.77, 0.53)
                n = self.art.oval(self.render, point, (0.032, 0.037, 0.031), color)
                self.effects.append((n, 0.2 + self.rng.random() * 0.2, v))
        n = self.art.place(
            self.render,
            self.art.tube,
            self.gun.root.getPos(self.render) + q.getForward() * 0.14,
            (0.022, 0.022, 0.065),
            (0.76, 0.61, 0.30),
        )
        self.effects.append((n, 0.57, q.getRight() * 1.9 + q.getUp() * 1.2))
        self.update_camera()

    def tick(self, dt):
        self.kick = max(0, self.kick - dt * 6.0)
        for name in ("shot_delay", "damage_t", "banner_t", "hit_t", "cache_delay"):
            setattr(self, name, max(0, getattr(self, name) - dt))
        if self.reload_time > 0:
            self.reload_time = max(0.0, self.reload_time - dt)
            if self.reload_time == 0:
                amount = min(self.reserve, MAGAZINE - self.mag)
                self.mag += amount
                self.reserve -= amount
        self.move(dt)
        self.update_camera()
        self.mission(dt)
        self.ai(dt)
        if self.mode != "play":
            return
        if "mouse1" in self.held and self.reload_time <= 0 and self.shot_delay <= 0:
            self.fire()
        effects = []
        for n, life, v in self.effects:
            life -= dt
            if life <= 0:
                n.removeNode()
                continue
            if v is not None:
                n.setPos(n.getPos() + v * dt)
                v.z -= 5.9 * dt
                n.setR(n.getR() + dt * 185)
            effects.append((n, life, v))
        self.effects = effects

    def update(self, task):
        dt = min(0.12, ClockObject.getGlobalClock().getDt())
        if self.mode == "title":
            self.tour += dt
            self.title_camera()
            for z in self.enemies:
                z.pose(dt, False)
        elif self.mode == "play":
            self.mouse_look()
            self.accumulator = min(0.15, self.accumulator + dt)
            while self.accumulator >= 1 / 90 and self.mode == "play":
                self.tick(1 / 90)
                self.accumulator -= 1 / 90
            if self.mode == "play":
                self.ui.update(self)
        return task.cont


from campaign import Campaign


class StoryGame(Campaign, Game):
    """Kör Rıhtım — Son Vapur."""


if __name__ == "__main__":
    StoryGame().run()
