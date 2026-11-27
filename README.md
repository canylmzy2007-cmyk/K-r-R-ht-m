# Kör Rıhtım · Son Vapur

![Son Vapur kapak çizimi](assets/son_vapur.jpg)

Marmara kıyısında, tahliye edilmiş görünen bir yük terminalinde vardiyadasın. Telsize üç kez vuruluyor. Birileri hâlâ kıyıda ve SEHER son seferine çıkmak üzere.

Python ve Panda3D ile hazırlanmış Türkçe, tek oyunculu birinci şahıs hayatta kalma oyunu. Altı bölüm limandan atölyeye, soğuk depoya ve vapurun üst güvertesine uzanır. Vardiya kayıtlarını incele, telsizdeki ipuçlarını birleştir, yolculara işaret ver ve son çağrıyı yap. Tahliye sırası finali değiştirir. İlk oynayış için hedef yaklaşık 30 dakikadır.

## Windows’ta oynamak

Bu deponun **Releases** bölümünde **KorRihtim-SonVapur-Windows-x64.zip** dosyasını indir. ZIP’e sağ tıklayıp **Tümünü ayıkla**, çıkan klasörde **OYNA.bat** dosyasına çift tıkla. Windows x64 paketinde Python ve Panda3D bulunur. Oyun çevrimdışı çalışır.

## Kontroller

| Tuş | Oyun içindeki işlevi |
| --- | --- |
| W, A, S, D ve fare | Hareket ve bakış |
| Shift + W / Boşluk | Koş / zıpla |
| E | İşaretli noktayı kullan, kaydı oku, ikmal al |
| 1, 2, 3 veya fare | Panelde yanıt seç |
| Tab | Türkçe görev defterini aç veya kapat |
| Sol tık / sağ tık / R | Ateş et / nişan al / şarjör değiştir |
| Esc | Duraklat, panelden çık |
| F1 ve F2 / M | Fare hassasiyeti / sesi aç veya kapat |

Türkçe diyaloglar altyazıyla anlatılır. **Tab** ile önceki konuşmalara ve notlara dönülebilir. Her tamamlanan hedef bir kontrol noktasıdır. Kapatıp açınca **Devam Et** ile son noktadan başla. Windows kayıtları kullanıcıya özel `%LOCALAPPDATA%\KorRihtim\son_vapur_1.json` dosyasındadır. İkmal için başlangıçtaki sandığa dön.

## Kaynaktan çalıştırmak

Kaynak paketinin kökünde `main.py`, `requirements.txt` ve `assets` birlikte durmalıdır. Python 3.13 x64 ile:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

`story.py` Türkçe diyalogları ve görevleri, `campaign.py` hikâye akışını ve kayıtları, `locations.py` haritaları, `story_ui.py` altyazıları ve arayüzü, `evacuees.py` yolcuları yönetir. Temel hareket ve çatışma `main.py` içindedir. Görsel, ses ve yazı tipi bildirimleri için [KAYNAKLAR.txt](KAYNAKLAR.txt) dosyasına bak.
