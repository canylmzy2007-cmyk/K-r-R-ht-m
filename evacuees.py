"""Friendly dock workers follow safe walkable cells between rendezvous points."""
import math
from direct.actor.Actor import Actor
from layout import Navigation, clear, slide


class Evacuees:
    def __init__(self, game, root, chapter):
        self.nav=Navigation();self.members=[];self.dest=None;self.time=0.
        for i in range(3 if chapter in (2,3,5) else 0):
            x,y=[(-2.,-12.),(0.,-13.),(2.,-12.)][i]
            figure=root.attachNewNode("yolcu");figure.setPos(x,y,0)
            actor=Actor(game.art.worker);actor.reparentTo(figure)
            tex=actor.findTexture("tulum")
            if tex:actor.replaceTexture(tex,game.art.tex[("yagmurluk","tulum2","tulum1")[i]])
            head=actor.controlJoint(None,"modelRoot","head")
            left=actor.controlJoint(None,"modelRoot","legl");right=actor.controlJoint(None,"modelRoot","legr")
            arms=[actor.controlJoint(None,"modelRoot",n) for n in ("arml","armr")]
            for hand,side in zip(arms,(1,-1)):hand.setR(hand.getR()+side*32)
            if i==0:
                game.art.oval(head,(0,.025,.12),(.237,.24,.13),(.78,.61,.25))
            figure.setScale((1.,.94,1.02)[i])
            shadow=game.art.shadow(root,x,y,1.05,1.23,.74)
            self.members.append((figure,actor,left,right,left.getP(),right.getP(),shadow))
    def send(self,pos):self.dest=pos
    def advance(self,dt):
        if not self.members or not self.dest:return
        self.time+=dt
        for i,(root,actor,l,r,lp,rp,shadow) in enumerate(self.members):
            x,y=root.getX(),root.getY();gx,gy=self.dest
            gx+=(-.9,.0,.9)[i];gy-=.65
            if not clear(gx,gy,.37):gx,gy=self.dest
            dist=math.hypot(gx-x,gy-y)
            if dist>.85:
                # The shared route points everybody toward one walkable goal.
                self.nav.aim(*self.dest);tx,ty=self.nav.waypoint(x,y,*self.dest)
                if math.hypot(x-self.dest[0],y-self.dest[1])<2.4:tx,ty=gx,gy
                dx,dy=tx-x,ty-y;v=math.hypot(dx,dy) or 1
                nx,ny=slide(x,y,dx/v*dt*(1.32+i*.07),dy/v*dt*(1.32+i*.07),.31)
                root.setPos(nx,ny,0);shadow.setPos(nx,ny,.018)
                root.setH(math.degrees(math.atan2(dx,-dy)));stride=math.sin(self.time*5.5+i)*20
            else:stride=0
            l.setP(lp+stride);r.setP(rp-stride)
    def close(self):
        for _,a,*_ in self.members:a.cleanup()
