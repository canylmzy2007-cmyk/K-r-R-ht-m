"""Single-player campaign, with chapter checkpoints and replayable Turkish subtitles."""
from pathlib import Path
from collections import deque
import os, math, json, tempfile
from panda3d.core import Filename
from actors import Infected
from art import ASSETS
from story import CHAPTERS
from locations import SetDesign, SETS, YARD
import layout


class Campaign:
    def __init__(self):
        base=Path(os.environ.get("LOCALAPPDATA") or Path.home())
        self.save_path=base/"KorRihtim"/"son_vapur_1.json"
        self.scene=None
        self.chapter=0
        self.step=0
        self.log=[]
        self.elapsed=0.
        self.choice=-1
        self.cached_save=self.read_save()
        self.caption_queue=deque()
        self.caption="";self.caption_time=0
        self.audio_bed=None
        self.saved_error=False
        super().__init__()
        self.accept("tab",self.journal)
        for i in range(3):self.accept(str(i+1),self.answer,[i])
        self.beds=[]
        for name in ("sahil","atolye","soguk","iskele","makine","guverte"):
            sound=self.loader.loadSfx(Filename.fromOsSpecific(str(ASSETS/(name+".wav"))))
            sound.setLoop(True);sound.setVolume(.54);self.beds.append(sound)

    @property
    def ch(self):return CHAPTERS[self.chapter]

    def read_save(self):
        try:
            s=json.loads(self.save_path.read_text(encoding="utf-8"))
            if not isinstance(s,dict) or s.get("version")!=1:return None
            for k,lo,hi in (("chapter",0,5),("step",0,6),("kills",0,9999),("choice",-1,1)):
                if type(s.get(k)) is not int or not lo<=s[k]<=hi:return None
            if not isinstance(s.get("log"),list) or not all(isinstance(t,str) for t in s["log"]):return None
            if type(s.get("elapsed")) not in (int,float) or not 0<=s["elapsed"]<=1e8:return None
            return s
        except (OSError,UnicodeError,ValueError):return None

    def snapshot(self,finished=False):
        s={"version":1,"chapter":self.chapter,"step":self.step,"kills":self.kills,
           "choice":self.choice,"elapsed":int(self.elapsed),"log":self.log[-125:],"finished":finished}
        self.cached_save=s
        tmp=None
        try:
            self.save_path.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=self.save_path.parent,delete=False) as f:
                tmp=Path(f.name);json.dump(s,f,ensure_ascii=False)
            os.replace(tmp,self.save_path);self.saved_error=False
        except OSError:self.saved_error=True
        finally:
            if tmp and tmp.exists():
                try:tmp.unlink()
                except OSError:pass

    def title(self):
        if self.scene:self.scene.close();self.scene=None
        if self.audio_bed:self.audio_bed.stop()
        layout.PROPS=YARD
        if hasattr(self,"yard_node"):self.yard_node.show();self.cache.show()
        super().title()

    def start(self):
        self.begin_at(None)

    def request_restart(self):
        self.mode="restart";self.ui.show("restart")

    def continue_game(self):
        data=self.cached_save
        self.begin_at(data if data and not data.get("finished") else None)

    def begin_at(self,data):
        self.chapter=data["chapter"] if data else 0
        self.step=data["step"] if data else 0
        self.log=list(data["log"]) if data else []
        self.elapsed=float(data["elapsed"]) if data else 0.
        self.choice=data["choice"] if data else -1
        self.activity=False;self.question_open=False;self.active_left=0.;self.midpoint=False
        self.caption_queue.clear();self.caption="";self.caption_time=0.
        super().start()
        self.kills=data["kills"] if data else 0
        self.open_chapter(resuming=bool(data))

    def open_chapter(self,resuming=False):
        self.cleanup()
        if self.scene:self.scene.close()
        if not hasattr(self,"yard_node"):self.yard_node=self.render.find("**/Terminal")
        layout.PROPS=SETS[self.chapter]
        if self.chapter:self.yard_node.hide();self.cache.hide()
        else:self.yard_node.show();self.cache.show()
        self.nav=layout.Navigation()
        self.scene=SetDesign(self,self.chapter);self.scene.stations(self.ch)
        self.scene.people.send(self.step_pos(self.step))
        self.x,self.y=(self.step_pos(self.step-1) if resuming and self.step else layout.START)
        self.feet=self.vz=self.pitch=0.;self.heading=0.;self.grounded=True
        self.hp=100.;self.mag=24;self.reserve=120
        self.reload_time=self.shot_delay=self.damage_t=self.hit_t=0.
        self.phase="story";self.wave=1+self.chapter//2;self.pending=0
        self.activity=False;self.midpoint=False;self.question_open=False;self.active_left=0.
        self.scouts=0 if resuming else 2;self.spawn_delay=9.;self.threat_count=0
        self.caption_queue.clear();self.caption="";self.caption_time=0.
        self.scene.update(self.step_pos(self.step),self.x,self.y,0.)
        if self.audio_bed:self.audio_bed.stop()
        self.audio_bed=self.beds[self.chapter]
        self.ambient.stop()
        if not self.muted:self.audio_bed.play()
        self.banner=(self.ch.place.upper(),self.ch.title);self.banner_t=4.2
        if resuming:
            self.say("Görev defteri",self.goal(),record=False)
        else:
            self.say(self.ch.place,self.ch.intro);self.snapshot()
        self.update_camera();self.ui.show("play");self.ui.update(self)

    def mute(self):
        super().mute()
        if self.audio_bed:
            self.ambient.stop()
            if self.muted:self.audio_bed.stop()
            else:self.audio_bed.play()

    def say(self,speaker,line,record=True):
        msg=f"{speaker}  /  {line}"
        if record:self.log.append(msg)
        self.caption_queue.append(msg)
        if not self.caption_time:self.next_caption()

    def next_caption(self):
        self.caption=self.caption_queue.popleft() if self.caption_queue else ""
        self.caption_time=max(4.6,min(14.,len(self.caption)/12.5)) if self.caption else 0.

    def step_pos(self,i):
        if i<2:return self.ch.notes[max(0,i)].pos
        if i==2:return self.ch.console
        if i<6:return self.ch.runs[i-3].pos
        return self.ch.exit

    def goal(self):
        if self.step<2:return self.ch.notes[self.step].label+" • İncele"
        if self.step==2:return "Haberleşme panelini kullan"
        if self.step==6:return self.ch.door
        return self.ch.runs[self.step-3].action

    def hint_target(self):
        if self.activity and self.midpoint:return self.aux
        return self.step_pos(self.step)

    def context_hint(self):
        if not getattr(self,"scene",None):return ""
        p=self.hint_target();dx=p[0]-self.x;dy=p[1]-self.y;dist=math.hypot(dx,dy)
        if self.question_open:return "Yanıt seçmek için sayı tuşuna bas."
        if self.activity:
            if self.midpoint:label=("Yolculara işaret ver" if self.chapter in (2,3,5) else "Yedek paneli doğrula")
            else:return f"{self.goal()}   •   {math.ceil(self.active_left)} sn"
        else:label=self.goal()
        if dist<2.25:return "E  •  "+label
        if math.hypot(self.x,self.y+16)<2.1:return "E  •  İlk yardım ve mühimmat al"
        angle=(math.degrees(math.atan2(dx,dy))+self.heading+180)%360-180
        way="önünde" if abs(angle)<35 else ("arkanda" if abs(angle)>142 else ("sağda" if angle>0 else "solda"))
        return f"{label}   •   {dist:.0f} m {way}"

    def interact(self):
        if self.mode!="play" or self.question_open:return
        x,y=self.hint_target()
        if math.hypot(x-self.x,y-self.y)>=2.25:
            if math.hypot(self.x,self.y+16)<2.1 and self.cache_delay<=0:
                self.hp=min(100,self.hp+35);self.reserve=max(self.reserve,96);self.cache_delay=18
                self.banner=("İKMAL","+35 sağlık ve yedek mühimmat");self.banner_t=2.5
            return
        if self.activity:
            if self.midpoint:
                self.midpoint=False;self.confirmed=True
                self.scene.people.send(self.step_pos(self.step))
                self.banner=("HAT AÇIK","İşlem devam ediyor.");self.banner_t=2.
                self.play_sound("uyari",.46,1.12)
            return
        if self.step<2:
            n=self.ch.notes[self.step];self.say(n.label,n.text)
            self.step+=1;self.scouts+=2;self.snapshot()
        elif self.step==2:
            self.question_open=True;self.held.clear();self.lock(False);self.mode="choice";self.ui.show("choice")
        elif self.step<6:
            run=self.ch.runs[self.step-3];self.active_left=float(run.seconds)
            self.activity=True;self.midpoint=False;self.confirmed=False;self.spawn_delay=3.0;self.threat_count=0
            # Walk to a different physical station halfway through each operation.
            self.aux=self.ch.notes[(self.step+self.chapter)%2].pos
            self.banner=("İŞLEM BAŞLADI",self.goal());self.banner_t=2.7;self.play_sound("uyari",.47)
        else:
            self.log.append(self.ch.place+"  /  "+self.ch.farewell)
            if self.chapter+1==len(CHAPTERS):
                self.snapshot(finished=True);self.finish(True)
            else:
                self.last_line=self.ch.farewell;self.chapter+=1;self.step=0
                self.open_chapter();self.mode="brief";self.lock(False);self.ui.show("brief")

    def answer(self,i):
        if self.mode!="choice" or i>=len(self.ch.answers):return
        if self.ch.correct>=0 and i!=self.ch.correct:
            self.ui.choice_error("Hat yanıt vermedi. İki kaydı tekrar oku.");self.play_sound("uyari",.26,.66);return
        if self.ch.correct<0:self.choice=i
        self.step+=1;self.question_open=False;self.mode="play";self.lock(True)
        self.say("Telsiz",self.ch.answers[i]+". Bağlantı kuruldu.")
        self.snapshot();self.ui.show("play");self.ui.update(self)

    def mission(self,dt):
        self.elapsed+=dt
        if self.caption_time:
            self.caption_time=max(0,self.caption_time-dt)
            if not self.caption_time:self.next_caption()
        self.scene.update(self.hint_target(),self.x,self.y,dt)
        self.spawn_delay-=dt
        if self.scouts and self.spawn_delay<=0:
            self.spawn_infected();self.scouts-=1;self.spawn_delay=8.
        if not self.activity:return
        if not self.midpoint:self.active_left=max(0.,self.active_left-dt)
        run=self.ch.runs[self.step-3]
        if not self.midpoint and not self.confirmed and self.active_left<=run.seconds*.49:
            self.midpoint=True;self.scene.people.send(self.aux)
            who,line=(("Ada","İkinci ışığa gel. Orada seni görürsek ilerleyebiliriz.") if self.chapter in (2,3,5) else ("Nihat","Sinyal koptu. Yedek panelden bir kez onay ver."))
            self.say(who,line,False);self.play_sound("uyari",.4)
        live=sum(not z.dead for z in self.enemies)
        if self.spawn_delay<=0 and self.threat_count<6+self.chapter//2 and self.active_left>5 and live<4:
            self.spawn_infected();self.threat_count+=1;self.spawn_delay=7.5
        if self.active_left<=0:
            self.activity=False
            who,sep,line=run.line.partition(":")
            self.say(who if sep else "Telsiz",line.strip() if sep else run.line)
            self.hp=min(100,self.hp+26);self.reserve=min(160,self.reserve+38)
            self.step+=1;self.snapshot();self.banner=("HAT TAMAM",self.goal());self.banner_t=2.8

    def spawn_infected(self):
        positions=[p for p in layout.PORTALS if layout.clear(*p,.40) and math.hypot(self.x-p[0],self.y-p[1])>11]
        if not positions:return
        x,y=self.rng.choice(positions)
        z=Infected(self,x,y,self.rng.randrange(3));self.enemies.append(z)

    def journal(self):
        if self.mode=="play":
            self.mode="journal";self.journal_page=0;self.lock(False);self.ui.show("journal")
        elif self.mode=="journal":self.return_play()
    def return_play(self):
        self.mode="play";self.lock(True);self.ui.show("play");self.ui.update(self)
    def enter(self):
        if self.mode in ("journal","brief"):self.return_play()
        elif self.mode=="lost":self.continue_game()
        elif self.mode=="title" and self.cached_save and not self.cached_save.get("finished"):self.continue_game()
        else:super().enter()
    def escape(self):
        if self.mode in ("journal","brief"):self.return_play()
        elif self.mode=="choice":self.question_open=False;self.return_play()
        elif self.mode=="restart":self.title()
        else:super().escape()
