"""Small original meshes, shared geometry and materials for Kör Rıhtım."""

from pathlib import Path
import math
from panda3d.core import (
    Vec3,
    NodePath,
    Geom,
    GeomNode,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomTriangles,
    Texture,
    TransparencyAttrib,
    CardMaker,
    TextNode,
    Filename,
    SamplerState,
)

ASSETS = Path(__file__).resolve().parent / "assets"
WHITE = (1, 1, 1)
STEEL = (0.23, 0.255, 0.25)
DARK = (0.09, 0.12, 0.13)
AMBER = (1, 0.66, 0.29)


def mesh(name, verts, tris):
    data = GeomVertexData(name, GeomVertexFormat.getV3n3t2(), Geom.UHStatic)
    data.setNumRows(len(verts))
    v, n, u = (GeomVertexWriter(data, s) for s in ("vertex", "normal", "texcoord"))
    for xyz, normal, uv in verts:
        v.addData3f(*xyz)
        n.addData3f(*normal)
        u.addData2f(*uv)
    faces = GeomTriangles(Geom.UHStatic)
    for a, b, c in tris:
        faces.addVertices(a, b, c)
    g = Geom(data)
    g.addPrimitive(faces)
    node = GeomNode(name)
    node.addGeom(g)
    return NodePath(node)


def sheet(name, points, normal, repeat=(1, 1)):
    uv = ((0, 0), (repeat[0], 0), repeat, (0, repeat[1]))
    return mesh(name, list(zip(points, [normal] * 4, uv)), [(0, 1, 2), (0, 2, 3)])


def rings(name, shape, count=14):
    """Stack noncircular sections (height, x radius, y radius, forward offset)."""
    verts = []
    tris = []
    for j, (z, rx, ry, offset) in enumerate(shape):
        lower = shape[max(j - 1, 0)]
        upper = shape[min(j + 1, len(shape) - 1)]
        for i in range(count + 1):
            a = 2 * math.pi * i / count
            co, si = math.cos(a), math.sin(a)
            dv = Vec3(
                (upper[1] - lower[1]) * co,
                (upper[2] - lower[2]) * si + upper[3] - lower[3],
                upper[0] - lower[0],
            )
            tangent = Vec3(-max(rx, 0.001) * si, max(ry, 0.001) * co, 0)
            normal = tangent.cross(dv)
            normal.normalize()
            verts.append(
                (
                    (rx * co, ry * si + offset, z),
                    tuple(normal),
                    (i / count, j / (len(shape) - 1)),
                )
            )
            if i < count and j < len(shape) - 1:
                k = j * (count + 1) + i
                tris.extend(
                    ((k, k + 1, k + count + 2), (k, k + count + 2, k + count + 1))
                )
    return mesh(name, verts, tris)


class Art:
    def __init__(self, loader):
        self.tex = {}
        for file in ASSETS.iterdir():
            if file.suffix in (".png", ".jpg"):
                t = loader.loadTexture(Filename.fromOsSpecific(str(file)))
                t.setMinfilter(SamplerState.FTLinearMipmapLinear)
                t.setAnisotropicDegree(4)
                if file.suffix == ".png":
                    t.setWrapU(Texture.WMClamp)
                    t.setWrapV(Texture.WMClamp)
                self.tex[file.stem] = t
        self.font = loader.loadFont(
            Filename.fromOsSpecific(str(ASSETS / "yazi.ttf")).getFullpath()
        )
        self.bold = loader.loadFont(
            Filename.fromOsSpecific(str(ASSETS / "baslik.ttf")).getFullpath()
        )
        for f in (self.font, self.bold):
            f.setPixelsPerUnit(72)
            f.setPageSize(1024, 1024)
        self.worker = loader.loadModel(
            Filename.fromOsSpecific(str(ASSETS / "isci.bam"))
        )
        self.cube = NodePath("box")
        self.faces = []
        for points, n in (
            (
                (
                    (-0.5, -0.5, -0.5),
                    (0.5, -0.5, -0.5),
                    (0.5, -0.5, 0.5),
                    (-0.5, -0.5, 0.5),
                ),
                (0, -1, 0),
            ),
            (
                (
                    (0.5, 0.5, -0.5),
                    (-0.5, 0.5, -0.5),
                    (-0.5, 0.5, 0.5),
                    (0.5, 0.5, 0.5),
                ),
                (0, 1, 0),
            ),
            (
                (
                    (0.5, -0.5, -0.5),
                    (0.5, 0.5, -0.5),
                    (0.5, 0.5, 0.5),
                    (0.5, -0.5, 0.5),
                ),
                (1, 0, 0),
            ),
            (
                (
                    (-0.5, 0.5, -0.5),
                    (-0.5, -0.5, -0.5),
                    (-0.5, -0.5, 0.5),
                    (-0.5, 0.5, 0.5),
                ),
                (-1, 0, 0),
            ),
            (
                (
                    (-0.5, -0.5, 0.5),
                    (0.5, -0.5, 0.5),
                    (0.5, 0.5, 0.5),
                    (-0.5, 0.5, 0.5),
                ),
                (0, 0, 1),
            ),
            (
                (
                    (-0.5, 0.5, -0.5),
                    (0.5, 0.5, -0.5),
                    (0.5, -0.5, -0.5),
                    (-0.5, -0.5, -0.5),
                ),
                (0, 0, -1),
            ),
        ):
            f = sheet("panel", points, n)
            self.faces.append(f)
            f.copyTo(self.cube)
        self.cube.flattenStrong()
        self.ball = rings(
            "oval",
            [
                (
                    math.sin(a) * 0.5,
                    max(0.001, math.cos(a) * 0.5),
                    max(0.001, math.cos(a) * 0.5),
                    0,
                )
                for a in [-math.pi / 2 + j * math.pi / 12 for j in range(13)]
            ],
            18,
        )
        self.tube = rings(
            "tube",
            [
                (-0.5, 0.001, 0.001, 0),
                (-0.495, 0.50, 0.50, 0),
                (0.495, 0.50, 0.50, 0),
                (0.5, 0.001, 0.001, 0),
            ],
            14,
        )

    def place(
        self, parent, source, pos=(0, 0, 0), size=(1, 1, 1), color=WHITE, texture=None
    ):
        node = source.copyTo(parent)
        node.setPos(*pos)
        node.setScale(*size)
        node.setColor(*color, 1)
        if texture:
            node.setTexture(self.tex[texture], 1)
        return node

    def box(self, parent, pos, size, color=WHITE, texture=None):
        return self.place(parent, self.cube, pos, size, color, texture)

    def oval(self, parent, pos, size, color=WHITE, texture=None):
        return self.place(parent, self.ball, pos, size, color, texture)

    def beam(self, parent, a, b, width, color, deep=None, round_=False):
        mid = (Vec3(*a) + Vec3(*b)) * 0.5
        delta = Vec3(*b) - Vec3(*a)
        node = self.place(
            parent,
            self.tube if round_ else self.cube,
            mid,
            (width, deep or width, delta.length()),
            color,
        )
        node.lookAt(*b)
        node.setP(node.getP() + 90)
        return node

    def text3(self, parent, txt, pos, scale, color, heading=0):
        t = TextNode("stencil")
        t.setFont(self.bold)
        t.setText(txt)
        t.setAlign(TextNode.ACenter)
        n = parent.attachNewNode(t)
        n.setScale(scale)
        n.setPos(*pos)
        n.setH(heading)
        n.setColor(*color, 1)
        return n

    def card(self, parent, name, frame, texture=None, color=None):
        cm = CardMaker(name)
        cm.setFrame(*frame)
        n = parent.attachNewNode(cm.generate())
        n.setTransparency(TransparencyAttrib.MAlpha)
        if texture:
            n.setTexture(self.tex[texture])
        if color:
            n.setColor(*color)
        n.setLightOff(1)
        return n

    def shadow(self, parent, x, y, sx, sy, opacity=0.78, z=0.018):
        n = self.card(
            parent, "contact", (-0.5, 0.5, -0.5, 0.5), "golge", (1, 1, 1, opacity)
        )
        n.setP(-90)
        n.setPos(x, y, z)
        n.setScale(sx, 1, sy)
        n.setDepthWrite(False)
        n.setBin("fixed", 2)
        return n
