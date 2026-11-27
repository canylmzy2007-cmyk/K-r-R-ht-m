# Kör Rıhtım

Marmara kıyısında kurgusal bir yük terminalindesin. Telsizden tahliye çağrısı geldiğinde kuzeydeki **TAHLİYE / 03** kapısına ulaş. Bu tek oyunculu görevde üç dalgada toplam 24 enfekte var.

## Windows'ta oyna

1. ZIP dosyasına sağ tıkla, **Tümünü ayıkla** seçeneğini kullan.
2. Çıkan klasörde **OYNA.bat** dosyasına çift tıkla.
3. Ana menüde **Oyuna Başla** düğmesine tıkla veya **Enter** tuşuna bas.

Paket Windows x64 için Python 3.13 ve Panda3D içerir. İlk açılışta internet bağlantısı veya ek kurulum gerekmez. Oyun 1280 × 720 pencerede açılır. Pencereyi büyütebilirsin.

## Visual Studio'da geliştir

Visual Studio'da **KorRihtim.sln** dosyasını aç. Başlangıç dosyası **main.py**. Çözüm, paketteki **runtime/python.exe** yorumlayıcısını kullanacak şekilde ayarlandı. **Ctrl + F5** ile çalıştırabilirsin. Visual Studio Python projesini tanımazsa Visual Studio Installer üzerinden **Python geliştirme** iş yükünü ekle. İstersen kodu değiştirip kaydettikten sonra **OYNA.bat** ile de sonucu görebilirsin.

Kendi Python ortamını kullanmak istersen projenin kök klasöründe, Windows x64 ve Python 3.13 ile şu iki komutu çalıştır.

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 main.py
```

## Kontroller

| Tuş | Eylem |
| --- | --- |
| WASD ve fare | Hareket et ve etrafa bak |
| Sol tık | Ateş et. Basılı tutarak otomatik atış yap |
| Sağ tık | Basılı tutarak nişan al |
| Sol Shift + W | Koş |
| Boşluk | Zıpla |
| R | Şarjör değiştir |
| E | Yakındaki ikmal sandığını veya açık tahliye kapısını kullan |
| Esc | Duraklat veya devam et |
| F1 / F2 | Fare hassasiyetini azalt veya artır |
| M | Sesi kapat veya aç |

## Görev

Enfekteler siperlerin çevresinden dolaşır. Baş, gövde ve bacaklar hareketli modele bağlı ayrı isabet bölgeleridir. Bacak isabeti enfekteyi yavaşlatır. Siperler mermileri keser. Nişan alırken saçılma azalır.

24 mermilik şarjör ve 96 yedek mermiyle başlarsın. Güneyde, başlangıç noktasının arkasındaki **İKMAL** sandığından yedek mühimmat alabilirsin. İlk iki dalganın sonunda sağlık ve mühimmat takviyesi gelir. Üçüncü dalgadan sonra kuzey kapısının iki yanında yeşil ışık yanar. Yanına gidip **E** tuşuna basarak görevi tamamla.

## Kaynak kod

| Dosya | İçerik |
| --- | --- |
| main.py | Oyun döngüsü, girdiler, hareket, mermiler, dalgalar, kazanma ve kaybetme |
| actors.py | İskelet animasyonları, isabet bölgeleri, düşme ve birinci şahıs silahı |
| layout.py | Harita ölçüleri, çarpışma, görüş hattı ve yol bulma |
| yard.py | Terminalin geometrisi, aydınlatma ve tahliye kapısı |
| art.py | Geometri, yazı tipi, model ve doku yükleme |
| interface.py | Türkçe menüler, sağlık, mühimmat, nişangâh ve görev bildirimleri |

Görsel ve ses dosyaları **assets** klasöründedir. Model ve doku kaynakları **KAYNAKLAR.txt** içinde yer alır.
