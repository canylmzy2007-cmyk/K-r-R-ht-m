"""Son Vapur. Locations, interactive objects and the radio script (in playing order)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    pos: tuple
    label: str
    text: str


@dataclass(frozen=True)
class Run:
    pos: tuple
    action: str
    seconds: int
    line: str


@dataclass(frozen=True)
class Chapter:
    place: str
    time: str
    title: str
    intro: str
    notes: tuple
    console: tuple
    question: str
    answers: tuple
    correct: int
    runs: tuple
    exit: tuple
    door: str
    farewell: str


CHAPTERS = (
    Chapter("Yük terminali", "04.17", "Yoklama", "Vardiya defterinde herkes çıkmış görünüyor. Ama kapalı telsizden üç kısa vuruş geliyor. Sonra bir kadın konuşuyor: «Ben Ada. Depoda hâlâ altı kişiyiz.»",
        (Note((-11,-14),"Vardiya defteri","Son satırı okuyorsun: «Altı kişi soğuk depoya geçti.» İsimlerin karşısındaki çıkış saatleri aynı el yazısıyla doldurulmuş."),
         Note((12,12),"Eski sefer kartı","Yıpranmış kartın arkasında vapurların çağrı işaretleri var. SEHER, Kanal 7 üzerinden dinleme yapıyor.")),
        (-12,13),"SEHER'i hangi kanaldan çağıracaksın?",("Kanal 3","Kanal 7","Kanal 9"),1,
        (Run((5,-15),"Saha vericisini aç",56,"SEHER: Sesin parça parça geliyor. İlk anten tamam. Kuzey hattına geç."),
         Run((-3,12),"Kuzey antenini hizala",58,"Ada: Camda bir ışık gördüm. Bizi duyduğunu onlara söyledim."),
         Run((11,-2),"Tahliye listesini ilet",61,"SEHER: Altı yolcu, bir de sen. İskele pompasına enerji verirsen yanaşabilirim.")),
        (0,18.8),"Bakım atölyesine geç","Vardiya defterini cebine koydun. Kâğıtta bu liman boştu."),
    Chapter("Bakım atölyesi", "04.23", "Sarı hat", "Elektrikçi Nihat kapının altından küçük bir anahtar uzatıyor. «Dizel çalışır. Ama her şalteri birden açarsan bütün liman uyanır.»",
        (Note((11,-13),"Bakım fişi","Nihat'ın notu: «Mavi hat vinci, sarı hat tahliye pompalarını, kırmızı hat atölyeyi besler.»"),
         Note((-12,11),"Pompa sayacı","İskele göstergesi sıfırda. Boruların üstünde taze bir sarı boya izi var.")),
        (4,16),"Jeneratör hangi hattı beslemeli?",("Sarı hat","Kırmızı hat","Mavi hat"),0,
        (Run((-11,-9),"Dizeli devreye al",57,"Nihat: İlk kez bu sesi duyduğuma sevindim. Şimdi regülatör."),
         Run((11,7),"Regülatörü devral",60,"Ada: İçerideki lambalar yandı. Kapı hâlâ kilitli."),
         Run((-5,15),"Pompayı basınca getir",62,"SEHER: Su çekiliyor. Depoya giden servis geçidi açık.")),
        (0,19),"Depoya gir","Nihat anahtarı geri istemedi. «Vapurda verirsin.»"),
    Chapter("Soğuk hava deposu", "04.30", "Altı bardak", "Boş bir kasanın üzerinde altı çay bardağı duruyor. En küçüğüne bir kaşık saplanmış. Ada sessizce söylüyor: «Kimseyi geride bırakmayacağına söz ver.»",
        (Note((-12,-12),"Sevk etiketi","Sevk kaydı: A odası dolu. B odasının kuzey çıkışı buz tutmuş. C odasında servis kapısı var."),
         Note((12,14),"Duvarın ardındaki ses","Boruya üç kez vuruyorsun. Yanıt C odasından geliyor. Küçük bir ses bardağını unutmamanı istiyor.")),
        (-7,17),"Hangi odanın kilidini çözeceksin?",("Oda A","Oda B","Oda C"),2,
        (Run((10,-15),"Buz çözmeyi başlat",58,"Ada: Kapıda küçücük bir aralık var. Biraz daha."),
         Run((-11,5),"Servis kapısını kaldır",62,"Çocuk: Bardağım sende mi?  /  Sen: En üst cebimde."),
         Run((8,11),"Çıkış ışığını yak",59,"Ada: Hepimiz dışarıdayız. Nihat yürüyemiyor. İki kişi koluna girdi.")),
        (0,19),"İskeleye çık","Altı kişiyi saydın. Küçük kız her basamakta cebindeki kaşığı şıkırdatıyor."),
    Chapter("Batı iskelesi", "04.36", "Sis düdüğü", "Su çekilmiş, iskele ikiye ayrılmış. SEHER sisin içinde görünüp kayboluyor. Ada kalabalığı topluyor. Nihat'ın cebinden eski bir vapur bileti düşüyor.",
        (Note((12,-14),"Kılavuzun krokisi","Krokiye göre batı şamandırası sığlığı, doğu şamandırası güvenli yaklaşmayı gösteriyor."),
         Note((-12,13),"Su seviyesi levhası","Batıdaki merdivenin son basamağı bile açıkta. Doğu fenerinin suya yansıyan ışığı hâlâ sabit.")),
        (3,16),"Vapura hangi yaklaşmayı bildirirsin?",("Batı","Doğu","Orta sığlık"),1,
        (Run((-10,-12),"Kıyı fenerini yak",61,"Kaptan: Fenerini aldım. Halatçılar yerlerine."),
         Run((11,4),"Yolcuları ikinci fenere çağır",59,"Ada: Önümde dört kişi, yanımda Nihat. Arkandaki küçük sesi dinle."),
         Run((-10,14),"Biniş köprüsünü yanaştır",60,"Küçük kız: Yedi kişiyiz. Seni de saydım.")),
        (0,19),"SEHER'e bin","Güverteye adım atınca iskele ilk kez sessiz geliyor."),
    Chapter("Makine dairesi", "04.42", "Makinenin kalbi", "SEHER'in jeneratörü tekliyor. Nihat telsizi senden istiyor. «O makinenin sesini kırk yıl dinledim. Ellerim titriyor ama kulağım sağlam.»",
        (Note((-12,-14),"Makine jurnali","Pompa çizelgesinde yeşil devre deniz suyu, beyaz devre içme suyu, turuncu devre ısıtma olarak işaretli."),
         Note((11,11),"Hararet saati","İbre yükseliyor. Nihat: «Isıyı alacak deniz suyu lazım. Rengini jurnale ben yazmıştım.»")),
        (-5,17),"Hangi soğutma devresini açarsın?",("Beyaz devre","Yeşil devre","Turuncu devre"),1,
        (Run((11,-10),"Emiş pompasını aç",55,"Nihat: Şimdi duyuyorsun. Düzgün bir kalp gibi."),
         Run((-11,6),"Sancak devresini bağla",57,"Kaptan: Pervaneye güç geldi. Köprüüstüne bir kişi gönder."),
         Run((8,15),"Motoru köprüye devret",60,"Ada: Üst güvertede ışık var. Seninle bakmamız gerek.")),
        (0,19),"Üst güverteye çık","Kapı kapanırken makine bir kez bile teklemiyor."),
    Chapter("Üst güverte", "04.48", "İki ışık", "Güneş söküyor. Arkanda, tahliye kapısının üstünde bir el feneri yanıp sönüyor. Kaptan iki güvenli yol görüyor. Kimi önce alacağınıza sen karar vereceksin.",
        (Note((11,-13),"İskele dürbünü","Bir liman görevlisi 03 kapısında bekliyor. Gözlerini sudan ayırmıyor. Elinde Nihat'ınkiyle aynı anahtar var."),
         Note((-11,12),"Köprüüstü telsizi","Palamar botundan cızırtı: «İki kişiyiz. Motor durdu. Bizi alırsanız iskeleye yedek halat da getiririz.»")),
        (4,16),"İlk kime yanaşalım?",("Kapıdaki görevliye","Palamar botuna"),-1,
        (Run((-9,-12),"Seyir fenerini aç",57,"Kaptan: Kararını duydum. Başüstü hazır."),
         Run((11,6),"Başüstü hattını kur",59,"Ada: Sancakta bir ışık daha. Herkes güvertede."),
         Run((-5,15),"Son çağrıyı gönder",58,"SEHER: İskeleyle temas kesildi. Hepiniz buradasınız.")),
        (0,19),"Düdüğü çal ve ayrıl","Kıyı geride kalırken Nihat anahtarı avucuna bırakıyor. Masanın üzerinde artık yedi bardak var."),
)
