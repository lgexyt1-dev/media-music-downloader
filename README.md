# Media & Music Downloader

Modern, hızlı ve kullanımı kolay bir medya indirme masaüstü uygulaması. YouTube, Spotify ve desteklenen diğer platformlardan video veya ses dosyalarını yüksek kalitede indirmenizi sağlar.

---

## Özellikler

* **Çoklu Platform Desteği:** YouTube (video/oynatma listeleri) ve Spotify entegrasyonu.
* **Format ve Kalite Seçenekleri:** MP4 (Video) ve MP3 (Ses) formatlarında yüksek kaliteli indirme imkanı.
* **Dinamik Arayüz (CustomTkinter):**
* Açık / Koyu (Light/Dark) tema geçişi.
* Özelleştirilebilir vurgu (accent) renk seçici.


* **Oynatma Listesi (Playlist) Desteği:** Tekli bağlantıların yanı sıra tüm listeyi otomatik algılama ve indirme.
* **Sesli Bildirim:** İndirme işlemi tamamlandığında kullanıcıyı uyaran sesli bildirim sistemi (`winsound`).
* **Gelişmiş Yol Yönetimi:** Özel karakterler ve Türkçe dizin yolları ile tam uyumluluk.

---

## Teknolojiler

Proje geliştirilirken kullanılan temel kütüphane ve araçlar:

* **[Python 3.12+](https://www.python.org/)**
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** Modern ve özelleştirilebilir GUI bileşenleri.
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** Gelişmiş video/ses indirme motoru.
* **[spotdl](https://github.com/spotDL/spotify-downloader):** Spotify müzik ve oynatma listesi indirici.
* **[FFmpeg](https://ffmpeg.org/):** Medya dönüştürme ve işleme aracı.
* **[PyInstaller](https://pyinstaller.org/):** Uygulamayı bağımsız `.exe` dosyasına dönüştürmek için.

---

## Kurulum ve Çalıştırma

### Gereksinimler

Projenin çalışabilmesi için sisteminizde **FFmpeg** yüklü ve çevre değişkenlerine (PATH) eklenmiş olmalıdır.

### Kaynak Koddan Çalıştırma

1. **Depoyu klonlayın:**
```bash
git clone https://github.com/lgexyt1-dev/media-music-downloader.git
cd media-music-downloader

```


2. **Sanal ortam oluşturun ve aktif edin:**
```bash
python -m venv venv
# Windows (PowerShell) için:
.\venv\Scripts\activate

```


3. **Gerekli bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt

```


4. **Uygulamayı başlatın:**
```bash
python media-downloader.py

```



---

## `.exe` Olarak Derleme

Python paketlerini ve özel ikonu içeren tek dosyalı Windows uygulamasını PyInstaller ile oluşturabilirsiniz. Spotify indirmeleri için `spotdl`, medya dönüştürme ve birleştirme için FFmpeg ayrıca kurulmalıdır:

```bash
python -m PyInstaller --noconsole --onefile --clean --icon=app.ico --collect-all customtkinter --collect-all yt_dlp --name MediaDownloader media-downloader.py

```

Derlenen uygulama `dist/` klasörü içerisinde `MediaDownloader.exe` adıyla oluşturulacaktır. Hazır Windows sürümü de [`dist/MediaDownloader.exe`](dist/MediaDownloader.exe) yolunda bulunur. Spotify indirmeleri için `spotdl`, medya dönüştürme ve birleştirme için FFmpeg sistemde ayrıca kurulu olmalıdır; bu harici araçlar `.exe` dosyasına dahil değildir.
