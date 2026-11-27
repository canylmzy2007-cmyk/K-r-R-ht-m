"""Turkish menu and HUD, anchored in aspect-correct screen coordinates."""

from direct.gui.DirectGui import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import TextNode, CardMaker, TransparencyAttrib

PAPER = (0.94, 0.94, 0.865, 1)
DIM = (0.72, 0.77, 0.74, 1)
GOLD = (0.99, 0.69, 0.30, 1)
INK = (0.055, 0.10, 0.11, 1)
GLASS = (0.048, 0.088, 0.098, 0.86)
GREEN = (0.48, 0.93, 0.69, 1)


class Interface:
    def __init__(self, app):
        self.app = app
        self.art = app.art
        self.root = app.aspect2d.attachNewNode("arayüz")
        self.buttons = []
        self.mode = None
        self.texts = {}
        self.width = 0
        self.cached = None
        self.size()

    def size(self):
        self.width = max(0.8, self.app.getAspectRatio())
        if self.mode:
            self.show(self.mode)

    def label(
        self, parent, text, x, z, scale, color=PAPER, bold=False, align=TextNode.ALeft
    ):
        t = TextNode("metin")
        t.setFont(self.art.bold if bold else self.art.font)
        t.setText(text)
        t.setTextColor(*color)
        t.setAlign(align)
        n = parent.attachNewNode(t)
        n.setScale(scale)
        n.setPos(x, 0, z)
        return n

    def rect(self, p, l, r, b, t, color):
        cm = CardMaker("panel")
        cm.setFrame(l, r, b, t)
        n = p.attachNewNode(cm.generate())
        n.setColor(*color)
        n.setTransparency(TransparencyAttrib.MAlpha)
        return n

    def button(self, text, x, z, fn, primary=False):
        c = GOLD if primary else (0.115, 0.175, 0.178, 0.96)
        btn = DirectButton(
            parent=self.layer,
            frameSize=(0, 0.72, -0.068, 0.068),
            frameColor=(
                c,
                (0.79, 0.57, 0.28, 1),
                (0.85, 0.73, 0.49, 1) if primary else (0.25, 0.32, 0.31, 1),
                c,
            ),
            relief=DGG.FLAT,
            borderWidth=(0, 0),
            pressEffect=False,
            command=fn,
            clickSound=None,
            rolloverSound=None,
        )
        btn.setPos(x, 0, z)
        self.buttons.append(btn)
        self.label(btn, text, 0.054, -0.020, 0.052, INK if primary else PAPER, True)
        self.label(btn, "›", 0.625, -0.024, 0.066, INK if primary else GOLD, True)

    def clear(self):
        for b in self.buttons:
            b.destroy()
        self.buttons = []
        if hasattr(self, "layer"):
            self.layer.removeNode()
        self.layer = self.root.attachNewNode("ekran")
        self.texts = {}
        self.cached = None

    def show(self, mode):
        self.mode = mode
        self.clear()
        app = self.app
        a = self.width
        x = -a + 0.105
        layer = self.layer
        if mode == "play":
            self.hud()
            return
        self.art.card(layer, "perde", (-a, a, -1, 1), "perde")
        self.rect(layer, -a, -a + min(0.012, a), -1, 1, GOLD)
        self.rect(layer, x, x + 0.061, 0.798, 0.826, GOLD)
        self.label(
            layer, "MARMARA  /  KARANTİNA BÖLGESİ", x + 0.087, 0.792, 0.036, DIM, True
        )
        if mode == "title":
            self.label(layer, "KÖR", x - 0.014, 0.428, 0.246, PAPER, True)
            self.label(layer, "RIHTIM", x - 0.014, 0.171, 0.286, PAPER, True)
            self.rect(layer, x, x + 0.133, 0.077, 0.086, GOLD)
            self.label(
                layer,
                "YÜK TERMİNALİ   /   VARDİYA 03",
                x + 0.160,
                0.062,
                0.035,
                GOLD,
                True,
            )
            self.label(
                layer,
                "Üç dalgayı atlat. Kuzey kapısından tahliye ol.",
                x,
                -0.077,
                0.044,
            )
            self.button("OYUNA BAŞLA", x, -0.255, app.start, True)
            self.button("ÇIKIŞ", x, -0.420, app.userExit)
        else:
            heading = {
                "pause": "DURAKLATILDI",
                "lost": "SİNYAL KESİLDİ",
                "won": "TAHLİYE TAMAM",
            }[mode]
            self.label(layer, heading, x, 0.35, 0.144, PAPER, True)
            if mode == "pause":
                self.label(layer, "Terminaldeki görev beklemede.", x, 0.228, 0.045, DIM)
                self.button("DEVAM ET", x, -0.004, app.resume, True)
                self.button("YENİDEN BAŞLA", x, -0.170, app.start)
            else:
                self.label(
                    layer,
                    f"Dalga  {app.wave} / 3     •     Etkisiz  {app.kills}     •     Baş isabeti  {app.head_hits}",
                    x,
                    0.226,
                    0.044,
                )
                self.label(
                    layer,
                    "Kuzey kapısına ulaştın."
                    if mode == "won"
                    else "Rıhtımda düştün. Bir sonraki vardiya seni bekliyor.",
                    x,
                    0.118,
                    0.040,
                    DIM,
                )
                self.button("TEKRAR OYNA", x, -0.104, app.start, True)
            self.button("ANA MENÜ", x, -0.340, app.title)
        self.label(layer, "KONTROLLER", x, -0.630, 0.031, GOLD, True)
        self.label(
            layer,
            "WASD  Hareket     •     Shift  Koş     •     Space  Zıpla",
            x,
            -0.702,
            0.035,
            DIM,
        )
        self.label(
            layer,
            "Sol tık  Ateş     •     Sağ tık  Nişan     •     R  Şarjör     •     E  Kullan",
            x,
            -0.765,
            0.035,
            DIM,
        )
        self.texts["settings"] = self.label(layer, "", x, -0.886, 0.032, DIM)
        self.settings()

    def settings(self):
        if "settings" in self.texts:
            self.texts["settings"].node().setText(
                f"F1 / F2  Fare hassasiyeti  {self.app.sensitivity:.2f}     •     M  Ses  {'kapalı' if self.app.muted else 'açık'}"
            )

    def hud(self):
        a = self.width
        lay = self.layer
        left = -a + 0.065
        right = a - 0.065
        top = lay.attachNewNode("dalga")
        self.rect(top, left, left + 0.56, 0.765, 0.919, GLASS)
        self.rect(top, left, left + 0.012, 0.765, 0.919, GOLD)
        self.label(top, "KÖR RIHTIM", left + 0.042, 0.865, 0.028, DIM, True)
        self.texts["wave"] = self.label(
            top, "", left + 0.039, 0.797, 0.055, PAPER, True
        )
        self.texts["remaining"] = self.label(
            lay, "", right, 0.850, 0.045, PAPER, True, TextNode.ARight
        )
        self.texts["direction"] = self.label(
            lay, "", 0, 0.87, 0.033, PAPER, True, TextNode.ACenter
        )
        self.rect(lay, left, left + 0.515, -0.921, -0.756, GLASS)
        self.label(lay, "SAĞLIK", left + 0.035, -0.808, 0.030, DIM, True)
        self.texts["hp"] = self.label(lay, "", left + 0.032, -0.888, 0.076, PAPER, True)
        self.rect(
            lay, left + 0.204, left + 0.467, -0.869, -0.848, (0.24, 0.28, 0.27, 1)
        )
        self.healthbar = self.rect(lay, 0, 0.263, 0, 0.021, GOLD)
        self.healthbar.setPos(left + 0.204, 0, -0.869)
        self.rect(lay, right - 0.518, right, -0.921, -0.756, GLASS)
        self.label(lay, "KARABİNA", right - 0.480, -0.810, 0.031, DIM, True)
        self.texts["mag"] = self.label(
            lay, "", right - 0.480, -0.892, 0.078, PAPER, True
        )
        self.texts["reserve"] = self.label(
            lay, "", right - 0.042, -0.884, 0.047, DIM, True, TextNode.ARight
        )
        self.cross = lay.attachNewNode("nişangâh")
        self.cross_parts = []
        for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            w, h = (0.015, 0.0032) if dx else (0.0032, 0.015)
            n = self.rect(
                self.cross, -w / 2, w / 2, -h / 2, h / 2, (0.96, 0.97, 0.88, 0.94)
            )
            self.cross_parts.append((n, dx, dz))
        self.dot = self.rect(lay, -0.0019, 0.0019, -0.0025, 0.0025, (1, 0.93, 0.73, 1))
        self.hitmark = lay.attachNewNode("isabet")
        for sx in (-1, 1):
            for sz in (-1, 1):
                n = self.rect(self.hitmark, -0.0025, 0.0025, -0.012, 0.012, PAPER)
                n.setPos(0.030 * sx, 0, 0.030 * sz)
                n.setR(-sx * sz * 45)
        self.hitmark.hide()
        self.texts["hit"] = self.label(
            lay, "", 0, -0.114, 0.032, GOLD, True, TextNode.ACenter
        )
        self.texts["prompt"] = self.label(
            lay, "", 0, -0.667, 0.043, PAPER, True, TextNode.ACenter
        )
        self.texts["banner"] = self.label(
            lay, "", 0, 0.630, 0.070, GOLD, True, TextNode.ACenter
        )
        self.texts["sub"] = self.label(
            lay, "", 0, 0.557, 0.039, PAPER, False, TextNode.ACenter
        )
        self.red = lay.attachNewNode("hasar")
        for i in range(8):
            alpha = 0.35 * (1 - i / 8)
            for s in (-1, 1):
                x = s * (a - i * 0.025)
                z = s * (1 - i * 0.017)
                self.rect(
                    self.red,
                    min(x, x - s * 0.026),
                    max(x, x - s * 0.026),
                    -1,
                    1,
                    (0.55, 0.09, 0.055, alpha),
                )
                self.rect(
                    self.red,
                    -a,
                    a,
                    min(z, z - s * 0.018),
                    max(z, z - s * 0.018),
                    (0.55, 0.09, 0.055, alpha),
                )
        self.red.hide()

    def update(self, app):
        if self.mode != "play":
            return
        h = int(round(app.heading / 45)) % 8
        dirs = ("K", "KB", "B", "GB", "G", "GD", "D", "KD")
        stage = app.wave if app.wave else 1
        nearby = app.context_hint()
        prompt = "ŞARJÖR DEĞİŞİYOR" if app.reload_time > 0 else nearby
        if not prompt and app.mag == 0:
            prompt = (
                "R  •  Şarjör değiştir" if app.reserve else "Mühimmat sandığı güneyde"
            )
        counts = (
            stage,
            app.pending + sum(not z.dead for z in app.enemies),
            int(app.hp + 0.5),
            app.mag,
            app.reserve,
            app.phase,
            dirs[h],
            prompt,
            app.banner if app.banner_t > 0 else ("", ""),
            app.hit_label if app.hit_t > 0.02 else "",
        )
        if counts != self.cached:
            self.cached = counts
            wave, n, hp, mag, res, phase, direc, prompt, banner, hit = counts
            for key, value in dict(
                wave=f"DALGA  {wave:02d} / 03",
                remaining=f"{n:02d}   ENFEKTE"
                if phase == "wave"
                else ("KUZEY KAPISI" if phase == "exit" else "HAZIRLIK"),
                hp=f"{hp:03d}",
                mag=f"{mag:02d}",
                reserve=f"/  {res:03d}",
                direction=direc,
                prompt=prompt,
                banner=banner[0],
                sub=banner[1],
                hit=hit,
            ).items():
                self.texts[key].node().setText(value)
            self.healthbar.setSx(max(0.001, hp / 100))
        gap = 0.016 + (app.kick * 0.018 + app.moving * 0.005) * (1 - app.aim)
        for node, x, z in self.cross_parts:
            node.setPos(x * gap, 0, z * gap)
        if app.aim > 0.85:
            self.cross.hide()
        else:
            self.cross.show()
        if app.hit_t > 0:
            self.hitmark.show()
            self.hitmark.setColorScale(
                1, 0.72, 0.36, 1
            ) if app.hit_head else self.hitmark.clearColorScale()
        else:
            self.hitmark.hide()
        if app.damage_t > 0:
            self.red.show()
            self.red.setAlphaScale(min(1, app.damage_t * 3))
        else:
            self.red.hide()
