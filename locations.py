"""Collision-matched sets, practical lights and wet surfaces for the six chapters."""
import math
from panda3d.core import PointLight, Vec3, Fog, Shader, TransparencyAttrib
from art import sheet, mesh
import layout
from evacuees import Evacuees
from layout import Prop

YARD = layout.PROPS
DARK=(.13,.19,.20)
IVORY=(.84,.82,.70)
AMBER=(1,.67,.29)
TEAL=(.36,.80,.80)
RUST=(.58,.30,.17)
# Position, width, depth and height. The renderer and navigation share these solids.
SETS = (
    YARD,
    (Prop("diesel",-6,-4,4.4,6,2.1),Prop("bench",6,6,6,1.8,1.1),Prop("cabinet",7,-4,3.8,1.6,2.8),Prop("tank",-7,9,3.7,3.7,3.6),Prop("crate",0,-10,2.4,2.1,1.8)),
    (Prop("shelf",-6,-7,2.2,9,3.6),Prop("shelf",5,-8,2.2,8,3.6),Prop("shelf",-6,7,2.2,8,3.6),Prop("shelf",5,6,2.2,8,3.6),Prop("freezer",.3,1.5,4.4,2,2.6)),
    (Prop("cargo",-6,-6,3,8,2.8),Prop("crate",6,-3,2.8,3,2),Prop("cargo",6,10,3.1,7,3),Prop("winch",-5,7,3.5,2.4,1.8)),
    (Prop("diesel",-5,-6,4,8,2.6),Prop("diesel",5,6,4,8,2.6),Prop("tank",7,-7,2.7,2.7,3.8),Prop("cabinet",-6,8,3.3,2.2,2.8),Prop("bench",0,13,4,1.8,1.3)),
    (Prop("bridge",-.5,3,7.5,8,3.5),Prop("winch",-6,-7,2.6,2.2,1.4),Prop("locker",6,-8,2,3,1.9),Prop("locker",-6,11,2.5,1.8,1.3)),
)
WATER_VERT = """#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex; out vec3 p;
void main(){p=p3d_Vertex.xyz;gl_Position=p3d_ModelViewProjectionMatrix*p3d_Vertex;}
"""
WATER_FRAG = """#version 130
uniform sampler2D horizon; uniform vec3 watcher; uniform float seconds; uniform float sea;
in vec3 p; out vec4 color;
void main(){
 vec2 a=p.xy; float t=seconds;
 vec3 n=normalize(vec3(.023*sin(a.x*2.1+a.y*1.3+t*.73)+.014*cos(a.y*4.1-t),
 .042*sin(a.y*1.3+a.x*.56-t*.67),1.));
 vec3 v=normalize(watcher-p); vec3 r=reflect(-v,n);
 vec2 uv=vec2(atan(r.x,r.y)*.15915+.55,.5+asin(clamp(r.z,-1.,1.))*.3183);
 vec3 sky=texture(horizon,uv).rgb;
 float glint=pow(max(0.,dot(r,normalize(vec3(-.26,.88,.32)))),28.);
 color=vec4(mix(vec3(.075,.14,.16),sky*.78,.28+.47*pow(1.-abs(v.z),2.))+glint*vec3(.55,.32,.12),sea);
}
"""

def deck_panel(parent, art, name, coords, texture, repeat, color):
    n=sheet(name,coords,(0,0,1),repeat)
    n.reparentTo(parent);n.setTexture(art.tex[texture]);n.setColor(*color,1)
    return n


def ferry(art, root, x,y,h,scale=1):
    ship=root.attachNewNode("SEHER");ship.setPos(x,y,-2.1);ship.setH(h);ship.setScale(scale)
    b=lambda p,s,c:art.box(ship,p,s,c)
    sections=((-17,.25,1.6),(-14,2.9,1.8),(-10,4,2.0),(8,4.2,2.0),(13,3.5,2.2),(17,.12,3.6))
    points=[];faces=[]
    for j,(yy,w,z) in enumerate(sections):
        for xx,zz in ((-w*.73,-1),(-w,z),(-w*.95,z+.18),(w*.95,z+.18),(w,z),(w*.73,-1)):
            points.append(((xx,yy,zz),(0,0,1),(xx*.14,yy*.15)))
        if j:
            for k in range(5):
                q=(j-1)*6+k;faces.extend(((q,q+1,q+7),(q,q+7,q+6)))
    hull=mesh("sac gövde",points,faces);hull.reparentTo(ship);hull.setTwoSided(True);hull.setTexture(art.tex["metro"]);hull.setColor(.40,.35,.30,1)
    for zz,w,d in ((3.3,6.9,18),(5.2,5.5,13)):
        b((0,-1,zz),(w,d,1.8),(.86,.83,.70));b((0,-1,zz+.95),(w+.5,d+.5,.14),DARK)
        for side in (-1,1):
            for i in range(-int(d/2)+1,int(d/2),2):
                b((side*(w/2+.02),i-1,zz+.08),(.09,1.4,.65),(.18,.27,.28))
                b((side*(w/2+.08),i-1,zz+.09),(.04,1.12,.47),(.90,.66,.32)).setLightOff()
    b((0,0,6.9),(1.7,2.3,2.3),(.60,.38,.19));b((0,0,8.05),(1.75,2.4,.36),DARK)
    art.beam(ship,(0,7,3),(0,7,8),.12,DARK);art.text3(ship,"S E H E R",(0,-10.03,3.30),.42,DARK)
    return ship


class SetDesign:
    def __init__(self,g,chapter):
        self.g=g;self.art=a=g.art;self.index=chapter;self.lights=[];self.wet=[];self.props=[]
        self.root=r=g.render.attachNewNode("Sefer alanı")
        self.marker=r.attachNewNode("hedef");self.marker_base=r.attachNewNode("istasyonlar")
        self.solid=r.attachNewNode("mimari")
        colors=[(.47,.55,.55),(.42,.39,.32),(.31,.45,.52),(.42,.53,.54),(.42,.34,.28),(.61,.59,.49)]
        fog=Fog("liman havası");fog.setColor(*colors[chapter]);fog.setExpDensity((.013,.019,.024,.016,.022,.011)[chapter]);g.render.setFog(fog);g.setBackgroundColor(*colors[chapter])
        if chapter:
            self.floor();self.perimeter()
            for p in SETS[chapter]:self.prop(p)
        if chapter in (0,3,5):
            ferry(a,self.solid,24 if chapter!=5 else -55,28 if chapter==0 else 8,8 if chapter!=5 else 25,1.05)
            self.horizon()
        if chapter==5:
            for side in (-1,1):
                for y in (-16,-5,7,16):
                    self.b((side*14.4,y,1.75),(.2,.2,3.5),IVORY)
                    self.glow((side*14.4,y,3.6),(.30,.30,.33),AMBER)
        self.solid.flattenStrong()
        for xx,yy in ((-8,-9),(9,10)):
            c=(1.,.65,.32) if chapter!=2 else (.62,.88,1.)
            light=PointLight("armatür");light.setColor((*c,1));light.setAttenuation((1,.065,.023))
            n=r.attachNewNode(light);n.setPos(xx,yy,3.9);g.render.setLight(n);self.lights.append(n)
        # Shader inputs on independent wet planes keep dry concrete visible between puddles.
        if chapter in (0,3,5):
            for xx,yy,w,d in ((-10,-10,2.8,6),(7,8,2.4,3),(0,13,3.3,1.4),(7,-12,2.2,4.8),(-2,-3,1.6,4)):
                self.water(xx,yy,w,d,.042,False)
        self.signal=self.marker.attachNewNode("hareketli ışık")
        a.place(self.signal,a.tube,(0,0,0),(.18,.18,.30),AMBER).setLightOff()
        a.oval(self.signal,(0,0,.07),(.12,.12,.12),(1,.94,.58)).setLightOff()
        self.ripple=0
        self.people=Evacuees(g,r,chapter)
        self.last_power=None
        p=self.marker_base
        a.box(p,(0,-16.8,.37),(1.0,.55,.74),(.36,.46,.32),"metal")
        a.box(p,(0,-17.09,.40),(.36,.02,.09),IVORY)
        a.box(p,(0,-17.10,.40),(.09,.02,.32),IVORY)
        a.text3(p,"İKMAL",(0,-17.11,.66),.11,IVORY)

    def b(self,pos,size,color,tex=None):
        return self.art.box(self.solid,pos,size,color,tex)
    def glow(self,pos,size,color):
        n=self.b(pos,size,color);n.setLightOff();return n
    def beam(self,a,b,w,c):
        return self.art.beam(self.solid,a,b,w,c)
    def floor(self):
        indoor=self.index in (1,2,4);col=(.79,.82,.84) if self.index==2 else (.72,.73,.70)
        deck_panel(self.solid,self.art,"döşeme",[(-15,-21,0),(15,-21,0),(15,21,0),(-15,21,0)],"zemin_m" if indoor else "beton",(5,7),col)
        for x in (-9,9):
            for y in range(-20,20,4):self.b((x,y,.012),(.073,2.8,.015),(.83,.65,.23))
        for y in (-15,-4,7,17):
            self.b((0,y,.012),(8,.28,.02),DARK)
            for i in range(-15,16):self.b((i*.25,y,.027),(.046,.24,.022),(.48,.52,.50))
    def perimeter(self):
        inside=self.index in (1,2,4)
        if inside:
            h=5.3 if self.index==2 else 6.
            for side in (-1,1):
                for y in range(-18,19,6):
                    self.b((side*15.15,y,h/2),(.3,6.03,h),(.71,.81,.82) if self.index==2 else (.65,.60,.52),"buz" if self.index==2 else "metro")
                    self.b((side*14.98,y-2.82,h/2),(.12,.20,h),DARK)
                    self.b((side*14.94,y,1.18),(.06,5.9,.14),TEAL if self.index==2 else RUST)
                self.b((0,side*21.1,h/2),(30,.3,h),(.65,.72,.70),"metro")
            self.b((0,0,h+.18),(30.4,42.5,.3),(.46,.50,.49),"metal")
            for y in range(-18,19,6):
                self.b((0,y,h-.2),(30,.36,.40),DARK)
                for x in (-8,8):
                    self.b((x,y,h-.43),(2.4,.44,.22),DARK);self.glow((x,y,h-.56),(2.2,.28,.035),(.68,.90,1) if self.index==2 else AMBER)
            for x in (-13,-12.45,13):
                self.beam((x,-20,h-.72),(x,20,h-.72),.19,TEAL if self.index==2 else RUST)
            for y in (-10,2,14):
                self.b((14.88,y,2),(.12,3.5,2.3),(.20,.31,.34))
                for k in (-1,0,1):self.b((14.74,y+k,2),(.10,.055,2.3),IVORY)
            for k in range(4):
                yy=-14+k*9;self.b((-14.77,yy,2.5),(.18,2,1.5),DARK)
                for l in range(9):self.b((-14.65,yy,1.90+l*.14),(.095,1.8,.05),(.52,.59,.57))
        else:
            for side in (-1,1):
                for y in range(-20,22,3):self.b((side*15.2,y,.60),(.13,.13,1.20),IVORY if self.index==5 else DARK)
                for z in (.46,1.08):self.b((side*15.2,0,z),(.08,42,.08),IVORY)
                for x in range(-15,16,3):self.b((x,side*21.15,.65),(.11,.1,1.3),DARK)
                self.b((0,side*21.15,1.15),(30,.09,.09),DARK)
    def prop(self,p):
        x,y,w,d,h=p.x,p.y,p.w,p.d,p.h
        def box(z,s,c,t=None,dx=0,dy=0):return self.b((x+dx,y+dy,z),s,c,t)
        self.art.shadow(self.solid,x+.25,y+.24,w+1.5,d+1.5,.80)
        if p.kind=="shelf":
            for sx in (-1,1):
                for sy in (-1,1):box(h/2,(.14,.14,h),TEAL,dx=sx*w*.47,dy=sy*d*.47)
            for layer in range(3):
                z=.14+layer*1.12;box(z,(w,d,.16),(.65,.64,.53))
                for k in range(4):
                    box(z+.49,(w*.85,d*.20,.80),(.77,.79,.68) if k%2 else (.78,.73,.65),"sandik",dy=(k-1.5)*d*.23)
        elif p.kind in ("diesel","winch","tank"):
            box(.16,(w,d,.32),DARK)
            tone=(.34,.54,.48) if p.kind=="diesel" else (.50,.48,.39)
            self.art.place(self.solid,self.art.tube,(x,y,h*.52),(w*.9,d*.89,h*.93),tone,"metro")
            for k in (-.32,0,.32):
                box(h*.65,(w*.93,.18,h*.64),(.32,.35,.32),dy=k*d)
            for k in (-.26,.26):
                box(h*.86,(.30,d*.72,.23),AMBER,dx=k*w)
            box(h*.62,(w*.91,d*.78,h*.65),(.80,.88,.79),"dizel")
            box(h*.89,(w*.4,d*.52,.20),(.54,.58,.52),"metal")
        elif p.kind=="bridge":
            box(h/2,(w,d,h),(.97,.94,.86),"kopru")
            for side in (-1,1):
                for i in (-1,1):box(h*.95,(w*.47,.09,.056),IVORY,dx=i*w*.25,dy=side*(d/2+.02))
            box(h+.05,(w+.4,d+.4,.17),DARK);box(h+1.08,(.16,.16,2.0),IVORY)
            self.beam((x-2,y,h+.15),(x,y,h+2.07),.04,DARK)
        else:
            tone={"cabinet":(.43,.54,.51),"bench":(.75,.61,.43),"cargo":(.44,.55,.57),"freezer":(.85,.89,.86),"locker":(.69,.62,.50)}.get(p.kind,IVORY)
            box(h/2,(w,d,h),tone,{"crate":"sandik","cabinet":"pano","freezer":"buz","cargo":"oluk","locker":"oluk"}.get(p.kind,"metro"))
            if p.kind not in ("crate","bench"):
                for i in range(7):box(h*.55,(.045,.052,h*.82),DARK,dx=w*(i-3)/7,dy=-d*.50)
                box(h*.72,(w*.34,.08,.27),(.96,.80,.45),dy=-d*.51)
    def horizon(self):
        for k in range(18):
            x=-48+k*5.4;h=2.8+4.3*abs(math.sin(k*39.75))
            self.b((x,52,h*.5-1),(4.6,3.2,h),(.34,.41,.43))
            for l in (-1,1):self.glow((x+l,50.34,h*.65),(.45,.045,.31),(.79,.61,.37))
        for x in (-21,18):
            self.beam((x,39,-1),(x,39,11),.35,RUST);self.beam((x-7,39,10),(x+4,39,12),.22,RUST)
            self.beam((x-7,39,10),(x+4,39,9.5),.18,RUST)
        if self.index!=0:
            self.water(0,0,200,195,-.7,True)
    def water(self,x,y,w,d,z,sea):
        a=self.art; verts=[];tris=[]
        if sea: pts=[(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)]
        else:
            pts=[(math.cos(i*.314)*(.44+.046*math.sin(i*2.1)),math.sin(i*.314)*(.43+.06*math.cos(i*1.42))) for i in range(20)]
        for px,py in pts:verts.append(((x+px*w,y+py*d,z),(0,0,1),(px+.5,py+.5)))
        for i in range(1,len(pts)-1):tris.append((0,i,i+1))
        n=mesh("su",verts,tris);n.reparentTo(self.root);n.setTransparency(TransparencyAttrib.MAlpha);n.setDepthWrite(False)
        if not hasattr(self.g,"water_shader"):self.g.water_shader=Shader.make(Shader.SL_GLSL,WATER_VERT,WATER_FRAG)
        n.setShader(self.g.water_shader);n.setShaderInput("horizon",a.tex["ufuk"]);n.setShaderInput("seconds",0.);n.setShaderInput("watcher",Vec3(0,-12,1.58));n.setShaderInput("sea",.96 if sea else .53);self.wet.append(n)
    def stations(self,ch):
        a=self.art
        specs=[(n.pos,n.label,True) for n in ch.notes]+[(ch.console,"HABERLEŞME",False)]+[(s.pos,s.action,False) for s in ch.runs]+[(ch.exit,ch.door,False)]
        for (x,y),name,note in specs:
            p=self.marker_base.attachNewNode(name);p.setPos(x,y,0)
            a.box(p,(0,0,.44),(.16,.15,.88),DARK)
            a.box(p,(0,0,.94),(.62,.24,.36),(.86,.83,.74),"metal" if note else "pano")
            a.box(p,(0,-.13,.97),(.51,.02,.22),(.83,.77,.57) if note else (.19,.34,.33))
            a.text3(p,name,(0,-.148,.95),min(.085,1.04/max(5,len(name))),DARK if note else IVORY)
            a.oval(p,(.22,-.145,1.05),(.05,.03,.05),AMBER).setLightOff()
        self.marker_base.flattenStrong()
    def update(self,pos,x,y,dt):
        self.ripple+=dt
        # Animate people and environmental uniforms at 30 Hz, independently of physics.
        clock=int(self.ripple*30)
        if getattr(self,"frame",None)==clock:return
        self.frame=clock
        self.people.advance(1/30)
        power=(self.g.step>=4)
        if power!=self.last_power:
            self.last_power=power
            for j,n in enumerate(self.lights):
                c=(.48,.77,1.) if self.index==2 else (1.,.67,.36)
                strength=(1.2 if power else .48) if j==1 else 1.
                n.node().setColor(tuple(v*strength for v in c)+(1,))
        self.marker.setPos(*pos,1.30+.09*math.sin(self.ripple*2.1))
        for n in self.wet:
            n.setShaderInput("watcher",Vec3(x,y,1.58));n.setShaderInput("seconds",float(self.ripple))
    def close(self):
        self.people.close()
        for n in self.lights:self.g.render.clearLight(n)
        self.root.removeNode()
