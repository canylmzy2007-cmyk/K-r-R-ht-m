"""Interactive Turkish subtitles, notebook, signal panel and debrief."""
from panda3d.core import TextNode
from interface import Interface, PAPER, DIM, GOLD, INK, GREEN, GLASS
from story import CHAPTERS


class StoryInterface(Interface):
    def wrapped(self, parent, text, x,z,scale,width,color=PAPER,bold=False):
        n=self.label(parent,text,x,z,scale,color,bold)
        n.node().setWordwrap(width/scale)
        return n
    def choice_error(self,text):
        if "error" in self.texts:self.texts["error"].node().setText(text)
    def show(self,mode):
        self.mode=mode;self.clear();a=self.width;app=self.app;layer=self.layer
        if mode=="play":
            self.hud()
            self.subtitle_box=layer.attachNewNode("Türkçe altyazılar")
            w=min(a-.09,1.29)
            self.rect(self.subtitle_box,-w,w,-.565,-.294,(.028,.053,.055,.89))
            self.texts["caption"]=self.wrapped(self.subtitle_box,"",-w+.055,-.363,.040,(w-.055)*2)
            return
        if mode in ("title","won"):
            self.art.card(layer,"SEHER",(-a,a,-1,1),"son_vapur")
        self.art.card(layer,"perde",(-a,a,-1,1),"perde")
        x=-a+max(.08,min(.16,a*.09))
        textw=min(1.86,2*a-.26)
        if mode not in ("title","won"):
            self.rect(layer,-a,a,-1,1,(.025,.052,.056,.83))
        self.rect(layer,x,x+.069,.79,.81,GOLD)
        self.label(layer,"MARMARA   /   SON VAPUR",x+.088,.785,.034,GOLD,True)
        if mode=="title":
            self.label(layer,"KÖR RIHTIM",x,.43,.176,PAPER,True)
            self.label(layer,"Son Vapur",x,.23,.110,GOLD,True)
            self.wrapped(layer,"Defterde liman boş. Telsizde biri var.",x,.087,.049,textw)
            ongoing=bool(app.cached_save and not app.cached_save.get("finished"))
            self.button("DEVAM ET" if ongoing else "YENİ HİKÂYE",x,-.13,app.continue_game if ongoing else app.start,True)
            if ongoing:self.button("YENİ HİKÂYE",x,-.30,app.request_restart)
            self.button("ÇIKIŞ",x,-.46 if ongoing else -.30,app.userExit)
        elif mode=="restart":
            self.label(layer,"Başa dönülsün mü?",x,.42,.090,PAPER,True)
            self.wrapped(layer,"Yeni hikâye başladığında son kontrol noktasının üzerine yazılır.",x,.23,.050,textw)
            self.button("BAŞTAN BAŞLA",x,-.10,app.start,True);self.button("GERİ",x,-.28,app.title)
        elif mode=="choice":
            self.label(layer,"Haberleşme paneli",x,.55,.100,PAPER,True)
            self.wrapped(layer,app.ch.question,x,.34,.060,textw,GOLD,True)
            for j,n in enumerate(app.ch.notes):self.wrapped(layer,n.text,x,.16-j*.23,.040,textw,DIM)
            for i,value in enumerate(app.ch.answers):
                self.button(str(i+1)+"   "+value,x,-.32-.154*i,lambda i=i:app.answer(i),i==0)
            self.texts["error"]=self.wrapped(layer,"",x,-.84,.037,textw,GOLD)
            self.label(layer,"Esc  •  Panele ara ver",x,-.95,.030,DIM)
            return
        elif mode=="brief":
            self.label(layer,app.ch.time+"  /  "+app.ch.place,x,.52,.086,PAPER,True)
            self.wrapped(layer,app.last_line,x,.24,.052,textw,GOLD)
            self.wrapped(layer,app.ch.intro,x,-.02,.046,textw)
            self.button("DEVAM ET",x,-.56,app.return_play,True);return
        elif mode=="journal":
            self.label(layer,"Görev defteri",x,.55,.10,PAPER,True)
            self.wrapped(layer,app.ch.place+"  /  "+app.goal(),x,.39,.046,textw,GOLD,True)
            def page(diff):
                app.journal_page+=diff;self.show("journal")
            newest=list(reversed(app.log))
            start=app.journal_page*3
            for i,t in enumerate(newest[start:start+3]):
                self.wrapped(layer,t,x,.18-i*.27,.041,min(2.3,2*a-.25))
            if start+3<len(newest):self.button("ESKİ KAYIT",x,-.73,lambda:page(1))
            if start:self.button("YENİ KAYIT",x+.78,-.73,lambda:page(-1))
            self.label(layer,"Sekme (Tab) veya Esc  •  Oyuna dön",x,-.92,.034,DIM);return
        elif mode=="pause":
            self.label(layer,"Duraklatıldı",x,.46,.130,PAPER,True)
            msg="Kontrol noktası bu oturumda bellekte." if app.saved_error else "Tamamlanan hedefler otomatik kaydedilir."
            self.wrapped(layer,msg,x,.27,.045,textw,DIM)
            self.button("DEVAM ET",x,.04,app.resume,True);self.button("ANA MENÜ",x,-.14,app.title)
        elif mode=="lost":
            self.label(layer,"Sinyal kesildi",x,.43,.13,PAPER,True)
            self.wrapped(layer,app.ch.place+" • Son kontrol noktasından yeniden bağlan.",x,.22,.048,textw)
            self.button("TEKRAR DENE",x,-.05,app.continue_game,True);self.button("ANA MENÜ",x,-.23,app.title)
        elif mode=="won":
            self.label(layer,"Sabah vardiyası",x,.49,.108,PAPER,True)
            ending=("03 kapısından aldığınız görevli yedek halatı bota atıyor. Nihat kardeşini ilk kez gün ışığında görüyor." if app.choice==0 else
                    "Bottan aldığınız iki yolcu, kapıdaki görevliyi halatla güverteye çekiyor. Nihat kardeşinin sesini tanıyor.")
            self.wrapped(layer,ending,x,.28,.051,textw)
            self.wrapped(layer,CHAPTERS[-1].farewell,x,.025,.047,textw,GOLD)
            self.label(layer,f"Altı bölüm tamamlandı   •   {int(app.elapsed)//60} dk {int(app.elapsed)%60:02d} sn",x,-.27,.042,DIM)
            self.button("ANA MENÜ",x,-.46,app.title,True);return
        self.wrapped(layer,"WASD  Hareket   •   Sol tık  Ateş   •   Sağ tık  Nişan   •   R  Şarjör\nE  Kullan   •   Tab  Görev defteri   •   Shift  Koş   •   Boşluk  Zıpla   •   Esc  Duraklat",x,-.72,.032,min(2.3,2*a-.18),DIM)
        self.texts["settings"]=self.label(layer,"",x,-.91,.030,DIM);self.settings()
    def update(self,app):
        super().update(app)
        if self.mode!="play":return
        phase=(app.chapter,app.step,app.caption)
        if getattr(self,"last_story",None)!=phase or not self.texts["caption"].node().getText():
            self.last_story=phase;self.texts["caption"].node().setText(app.caption)
        (self.subtitle_box.show if app.caption else self.subtitle_box.hide)()
        self.texts["wave"].node().setText(f"BÖLÜM {app.chapter+1} / 6")
        self.texts["remaining"].node().setText(app.ch.place.upper()+"   •   "+app.ch.time)
