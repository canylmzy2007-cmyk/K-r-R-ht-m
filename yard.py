"""Marmara kıyısında kurgusal bir yük terminali."""

import math, random
from panda3d.core import AmbientLight, DirectionalLight, Fog
from art import mesh, sheet, STEEL, DARK
from layout import PROPS


def build(app):
    art = app.art
    r = random.Random(19)
    root = app.render.attachNewNode("Terminal")
    box, beam = art.box, art.beam
    ambient = AmbientLight("gökyüzü")
    ambient.setColor((0.55, 0.61, 0.68, 1))
    sun = DirectionalLight("sabah ışığı")
    sun.setColor((0.88, 0.76, 0.58, 1))
    s = app.render.attachNewNode(sun)
    s.setPos(-22, -14, 24)
    s.lookAt(0, 0, 0)
    app.render.setLight(app.render.attachNewNode(ambient))
    app.render.setLight(s)
    fog = Fog("deniz sisi")
    fog.setColor(0.48, 0.54, 0.56)
    fog.setExpDensity(0.0115)
    app.render.setFog(fog)
    # A full equirectangular panorama encloses the entire playing field.
    verts = []
    tris = []
    for band in range(37):
        lat = -math.pi / 2 + math.pi * band / 36
        for i in range(97):
            az = 2 * math.pi * i / 96
            vect = (
                math.cos(lat) * math.sin(az),
                math.cos(lat) * math.cos(az),
                math.sin(lat),
            )
            verts.append((tuple(v * 121 for v in vect), (0, 0, 1), (i / 96, band / 36)))
            if band < 36 and i < 96:
                k = band * 97 + i
                tris.extend(((k, k + 1, k + 98), (k, k + 98, k + 97)))
    sky = mesh("sabah", verts, tris)
    sky.reparentTo(app.render)
    sky.setTwoSided(True)
    sky.setTexture(art.tex["ufuk"])
    sky.setLightOff()
    sky.setFogOff()
    sky.setDepthWrite(False)
    sky.setBin("background", 0)
    sky.setH(95)
    ground = sheet(
        "zemin",
        [
            (-15.25, -21.25, 0),
            (15.25, -21.25, 0),
            (15.25, 21.25, 0),
            (-15.25, 21.25, 0),
        ],
        (0, 0, 1),
    )
    ground.reparentTo(root)
    ground.setTexture(art.tex["saha"])
    # Old traffic lanes, transverse dock markings and channel grates.
    for x in (-11.4, 11.4):
        for y in range(-20, 21, 3):
            box(root, (x, y, 0.009), (0.11, 2.25, 0.012), (0.80, 0.65, 0.32))
    for x in (-5.4, 5.4):
        for y in (-18, -10, -2, 6, 14):
            box(root, (x, y, 0.009), (0.075, 6.2, 0.012), (0.69, 0.68, 0.56))
    for y in (-11, 3, 15):
        box(root, (0, y, 0.011), (9, 0.21, 0.015), (0.18, 0.20, 0.19))
        for x in range(-22, 23):
            box(root, (x * 0.2, y, 0.022), (0.055, 0.19, 0.012), (0.40, 0.41, 0.37))
    for p in PROPS:
        x, y, w, d, h = p.x, p.y, p.w, p.d, p.h
        art.shadow(root, x + 0.42, y + 0.35, w + 2.3, d + 2.5, 0.85)
        if p.kind == "container":
            obj = root.attachNewNode("konteyner")
            obj.setPos(x, y, h / 2)
            if w < d:
                obj.setH(90)
                w, d = d, w
            for i, f in enumerate(art.faces):
                material = f"celik{p.tone}" if i in (0, 1, 4, 5) else f"kapi{p.tone}"
                art.place(obj, f, (0, 0, 0), (w, d, h), (0.96, 0.96, 0.93), material)
            for xx in (-w / 2, w / 2):
                for yy in (-d / 2, d / 2):
                    box(obj, (xx, yy, 0), (0.09, 0.09, h + 0.02), (0.30, 0.29, 0.24))
                    for zz in (-h / 2 + 0.09, h / 2 - 0.09):
                        box(obj, (xx, yy, zz), (0.23, 0.18, 0.18), (0.38, 0.36, 0.28))
            for yy in (-d / 2, d / 2):
                for zz in (-h / 2 + 0.04, h / 2 - 0.04):
                    box(obj, (0, yy, zz), (w, 0.08, 0.085), (0.35, 0.33, 0.26))
        elif p.kind == "crate":
            box(root, (x, y, h / 2), (w, d, h), (0.95, 0.94, 0.91), "kasa")
            for xx in (-0.41, 0.41):
                box(root, (x + w * xx, y, h + 0.007), (0.065, d + 0.015, 0.03), DARK)
        elif p.kind == "barrier":
            box(root, (x, y, 0.17), (w, d, 0.34), (0.79, 0.80, 0.75), "beton")
            box(
                root,
                (x, y, h * 0.52),
                (w - 0.10, d * 0.65, h * 0.90),
                (0.96, 0.95, 0.88),
                "beton",
            )
            for i in range(8):
                b = box(
                    root,
                    (x - w * 0.42 + i * w * 0.12, y - d * 0.33 - 0.012, h * 0.61),
                    (0.18, 0.018, 0.34),
                    (0.73, 0.52, 0.23),
                )
                b.setR(-24)
    # Boundary panels and dock warehouses.
    for side in (-1, 1):
        for iy in range(-21, 22, 6):
            box(
                root,
                (side * 15.25, iy, 2.35),
                (0.5, 5.96, 4.7),
                (0.72, 0.79, 0.77),
                "beton",
            )
            box(root, (side * 14.98, iy - 2.9, 2.35), (0.23, 0.23, 4.75), STEEL)
            box(root, (side * 14.93, iy, 1.28), (0.08, 5.93, 0.15), (0.68, 0.44, 0.20))
        box(root, (side * 18.8, 2, 4.1), (6.5, 31, 8.2), (0.44, 0.54, 0.55), "metal")
        box(root, (side * 18.8, 2, 8.19), (7.2, 31.7, 0.24), DARK)
        for y in range(-12, 18, 3):
            box(root, (side * 15.49, y, 6.2), (0.14, 2.48, 0.98), (0.23, 0.34, 0.36))
            for k in (-0.72, 0, 0.72):
                box(root, (side * 15.4, y + k, 6.2), (0.08, 0.055, 0.96), STEEL)
        for x in (-12, -6, 0, 6, 12):
            if side == 1 and x == 0:
                continue
            box(
                root,
                (x, side * 21.25, 2.2),
                (5.95, 0.5, 4.4),
                (0.77, 0.77, 0.69),
                "beton",
            )
            box(root, (x + 2.90, side * 20.96, 2.25), (0.20, 0.22, 4.5), STEEL)
    for x in (-3.1, 3.1):
        box(root, (x, 21, 2.55), (0.42, 0.7, 5.1), STEEL)
    box(root, (0, 21, 4.9), (6.6, 0.7, 0.5), DARK)
    box(root, (0, 21.35, 1.95), (5.9, 0.23, 3.9), (0.29, 0.39, 0.40), "metal")
    for z in [i * 0.24 for i in range(1, 16)]:
        box(root, (0, 21.2, z), (5.8, 0.06, 0.035), DARK)
    box(root, (0, 20.84, 4.46), (5.72, 0.17, 0.67), (0.10, 0.28, 0.27))
    art.text3(root, "TAHLİYE   /   03", (0, 20.737, 4.30), 0.40, (0.92, 0.89, 0.71))
    for x in (-2.35, 2.35):
        box(root, (x, 20.82, 1.02), (0.18, 0.35, 2.04), (0.83, 0.61, 0.28))
        for z in (0.45, 0.9, 1.35, 1.80):
            box(root, (x, 20.62, z), (0.185, 0.04, 0.19), DARK)

    def lamp(x, y, h):
        box(root, (x, y, h * 0.5), (0.12, 0.12, h), STEEL)
        beam(root, (x, y, h - 0.6), (x + 0.72, y, h), 0.12, STEEL)
        box(root, (x + 0.72, y, h), (0.68, 0.56, 0.18), DARK)
        bulb = box(root, (x + 0.72, y, h - 0.11), (0.58, 0.45, 0.06), (1, 0.83, 0.52))
        bulb.setLightOff()

    for x, y, h in ((-13, -13, 5.7), (13, -1, 6), (11, 18.8, 6.3), (-11, 19, 5.9)):
        lamp(x, y, h)

    # Gantry cranes: lattice legs, trolley, hanging spreader.
    def crane(x, y, s, tone):
        frame = root.attachNewNode("portal vinç")
        frame.setPos(x, y, 0)
        frame.setScale(s)
        for xx in (-5, 5):
            for yy in (-2, 2):
                beam(frame, (xx, yy, 0), (xx * 0.82, yy, 12), 0.42, tone)
            for z in (1, 4, 7, 10):
                beam(frame, (xx * 0.89, -2, z), (xx * 0.86, 2, z + 2), 0.14, tone)
                beam(frame, (xx * 0.89, 2, z), (xx * 0.86, -2, z + 2), 0.14, tone)
        for yy in (-2, 2):
            for z in (11.9, 13.5):
                beam(frame, (-11, yy, z), (8, yy, z), 0.28, tone)
            for i in range(-11, 8, 2):
                beam(frame, (i, yy, 11.9), (i + 1, yy, 13.5), 0.15, tone)
                beam(frame, (i + 1, yy, 13.5), (i + 2, yy, 11.9), 0.15, tone)
        for i in range(-11, 8, 3):
            beam(frame, (i, -2, 13.45), (i, 2, 13.45), 0.18, tone)
        box(frame, (-7, 0, 11.5), (2.2, 4.1, 1.3), tone)
        box(frame, (-7, -2.1, 11.3), (1.5, 0.28, 0.65), (0.24, 0.34, 0.36))
        for xx in (-7.6, -6.35):
            beam(frame, (xx, 0, 11.1), (xx, 0, 5.9), 0.045, DARK)
        box(frame, (-7, 0, 5.8), (2.6, 0.53, 0.25), tone)

    crane(-9, 39, 1.12, (0.37, 0.36, 0.30))
    crane(19, 51, 1.05, (0.44, 0.37, 0.29))
    for i in range(19):
        x = r.uniform(-62, 62)
        y = r.uniform(42, 69)
        h = r.uniform(2, 8)
        box(
            root,
            (x, y, h / 2),
            (r.uniform(3, 9), r.uniform(4, 12), h),
            (0.42, 0.49, 0.50),
        )
        for z in (2.0, 4.2, 6.4):
            if z < h:
                box(root, (x, y - 2.04, z), (2.8, 0.12, 0.38), (0.29, 0.36, 0.38))
        if i % 4 == 0:
            art.place(
                root, art.tube, (x, y, h + 2.4), (0.66, 0.66, 4.8), (0.33, 0.36, 0.35)
            )
    for x, y in ((-28, 24), (28, 25), (-24, -16)):
        art.place(
            root, art.tube, (x, y, 5), (5.4, 5.4, 10), (0.56, 0.59, 0.56), "metal"
        )
        for z in (1.2, 4.0, 7.0, 9.7):
            art.place(root, art.tube, (x, y, z), (5.52, 5.52, 0.12), STEEL)
    for xx in (-10, 10):
        art.text3(
            root,
            "BÖLGE  07" if xx < 0 else "KARANTİNA",
            (xx, 20.96, 2.9),
            0.53,
            (0.34, 0.36, 0.31),
        )
    root.flattenStrong()
    beacon = app.render.attachNewNode("tahliye ışığı")
    for x in (-2.45, 2.45):
        b = box(beacon, (x, 20.70, 3.5), (0.20, 0.14, 0.55), (0.31, 1, 0.66))
        b.setLightOff()
    beacon.hide()
    return beacon
