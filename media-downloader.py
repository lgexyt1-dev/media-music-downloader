import customtkinter as ctk
from tkinter import filedialog, colorchooser
import yt_dlp
import threading
import os
import subprocess
import winsound  # İndirme bitince sesli bildirim çalmak için

# Arayüz İlk Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MediaDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Media & Music Downloader")
        self.geometry("650x600")
        self.resizable(False, False)

        # Varsayılan İndirme Klasörü
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # --- Başlık ---
        self.title_label = ctk.CTkLabel(self, text="Media & Music Downloader", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(padx=20, pady=(20, 10))

        # --- URL Giriş Kutusu ---
        self.url_entry = ctk.CTkEntry(self, placeholder_text="YouTube, Playlist, Instagram veya Spotify Linki...", width=520)
        self.url_entry.pack(padx=20, pady=10)

        # --- Klasör Seçim Alanı ---
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(padx=20, pady=5, fill="x")

        self.folder_label = ctk.CTkLabel(self.folder_frame, text=f"Kaydedilecek Yer: {self.download_path}", font=ctk.CTkFont(size=11), text_color="gray")
        self.folder_label.pack(side="left", padx=(50, 10))

        self.browse_btn = ctk.CTkButton(self.folder_frame, text="Gözat...", width=80, height=24, command=self.browse_folder)
        self.browse_btn.pack(side="right", padx=(0, 50))

        # --- Format Seçimi (MP4 / MP3) ---
        self.format_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.format_frame.pack(padx=20, pady=10)

        self.format_var = ctk.StringVar(value="mp4")
        self.mp4_radio = ctk.CTkRadioButton(self.format_frame, text="Video (MP4)", variable=self.format_var, value="mp4", command=self.toggle_quality_menu)
        self.mp4_radio.pack(side="left", padx=15)
        
        self.mp3_radio = ctk.CTkRadioButton(self.format_frame, text="Sadece Ses (MP3)", variable=self.format_var, value="mp3", command=self.toggle_quality_menu)
        self.mp3_radio.pack(side="left", padx=15)

        # --- Kalite/Çözünürlük Seçimi ---
        self.quality_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quality_frame.pack(padx=20, pady=5)

        self.quality_label = ctk.CTkLabel(self.quality_frame, text="Video Kalitesi:", font=ctk.CTkFont(size=12))
        self.quality_label.pack(side="left", padx=(0, 10))

        self.quality_var = ctk.StringVar(value="En Yüksek (Best)")
        self.quality_option = ctk.CTkOptionMenu(
            self.quality_frame, 
            variable=self.quality_var, 
            values=["En Yüksek (Best)", "1080p", "720p", "480p", "360p"]
        )
        self.quality_option.pack(side="left")

        # --- İndir Butonu ---
        self.download_btn = ctk.CTkButton(self, text="İndirmeyi Başlat", font=ctk.CTkFont(size=15, weight="bold"), height=40, command=self.start_download_thread)
        self.download_btn.pack(padx=20, pady=15)

        # --- İlerleme Çubuğu (Progress Bar) ---
        self.progress_bar = ctk.CTkProgressBar(self, width=480)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=10)

        # --- Durum ve Yüzde Etiketi ---
        self.status_label = ctk.CTkLabel(self, text="Hazır", font=ctk.CTkFont(size=13))
        self.status_label.pack(padx=20, pady=5)

        # ==========================================
        # --- SOL ALT KÖŞE AYARLAR PANALİ (FOOTER) ---
        # ==========================================
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=15, pady=15)

        # 1. Görünüm Modu (Dark / Light)
        self.mode_var = ctk.StringVar(value="Dark")
        self.mode_switch = ctk.CTkSwitch(
            self.footer_frame, 
            text="Karanlık Mod", 
            variable=self.mode_var, 
            onvalue="Dark", 
            offvalue="Light",
            command=self.change_mode,
            font=ctk.CTkFont(size=11)
        )
        self.mode_switch.pack(side="left", padx=(10, 15))

        # 2. Color Picker (Renk Seçici Butonu)
        self.color_picker_btn = ctk.CTkButton(
            self.footer_frame,
            text="🎨 Renk Seç...",
            width=90,
            height=24,
            font=ctk.CTkFont(size=11),
            command=self.open_color_picker
        )
        self.color_picker_btn.pack(side="left", padx=(0, 15))

        # 3. Sesli Bildirim Switch'i
        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_switch = ctk.CTkSwitch(
            self.footer_frame, 
            text="🔔 Ses", 
            variable=self.sound_var,
            font=ctk.CTkFont(size=11),
            width=40
        )
        self.sound_switch.pack(side="left")

    def open_color_picker(self):
        # Sistem renk seçici pencerisini açıyoruz
        color_code = colorchooser.askcolor(title="Arayüz Vurgu Rengini Seçin")
        if color_code and color_code[1]:  # Kullanıcı renk seçip 'Tamam' dediyse
            selected_hex = color_code[1]
            self.apply_custom_color(selected_hex)

    def apply_custom_color(self, hex_color):
        # Ana Butonlar ve Vurgu Öğelerini Seçilen Renge Güncelleme
        self.download_btn.configure(fg_color=hex_color)
        self.browse_btn.configure(fg_color=hex_color)
        self.quality_option.configure(fg_color=hex_color, button_color=hex_color)
        self.progress_bar.configure(progress_color=hex_color)
        self.color_picker_btn.configure(fg_color=hex_color)
        self.mp4_radio.configure(fg_color=hex_color)
        self.mp3_radio.configure(fg_color=hex_color)
        self.mode_switch.configure(progress_color=hex_color)
        self.sound_switch.configure(progress_color=hex_color)

    def change_mode(self):
        ctk.set_appearance_mode(self.mode_var.get())

    def toggle_quality_menu(self):
        if self.format_var.get() == "mp3":
            self.quality_option.configure(state="disabled")
        else:
            self.quality_option.configure(state="normal")

    def browse_folder(self):
        selected_dir = filedialog.askdirectory(initialdir=self.download_path)
        if selected_dir:
            self.download_path = selected_dir
            display_path = self.download_path if len(self.download_path) < 40 else f"...{self.download_path[-35:]}"
            self.folder_label.configure(text=f"Kaydedilecek Yer: {display_path}")

    def play_finish_sound(self):
        if self.sound_var.get():
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            playlist_index = d.get('info_dict', {}).get('playlist_index')
            playlist_count = d.get('info_dict', {}).get('playlist_count')
            prefix = f"[{playlist_index}/{playlist_count}] " if playlist_index and playlist_count else ""

            if total_bytes > 0:
                percentage = downloaded / total_bytes
                self.progress_bar.set(percentage)
                speed = d.get('_speed_str', '').strip()
                self.status_label.configure(text=f"{prefix}İndiriliyor: %{int(percentage * 100)} | Hız: {speed}", text_color="#F1C40F")

        elif d['status'] == 'finished':
            self.progress_bar.set(1.0)
            self.status_label.configure(text="İşleniyor (FFmpeg dönüştürmesi yapılıyor)...", text_color="#3498DB")

    def start_download_thread(self):
        threading.Thread(target=self.download_media, daemon=True).start()

    def download_media(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Lütfen geçerli bir link girin!", text_color="#E74C3C")
            return

        self.progress_bar.set(0)
        self.status_label.configure(text="İndirme başlatılıyor...", text_color="#F1C40F")
        self.download_btn.configure(state="disabled")

        # --- Spotify Kontrolü ---
        if "spotify.com" in url.lower():
            self.status_label.configure(text="Spotify içeriği indiriliyor...", text_color="#3498DB")
            try:
                cmd = ["spotdl", "download", url, "--output", self.download_path]
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                self.progress_bar.set(1.0)
                self.status_label.configure(text="Spotify İndirmesi Tamamlandı! 🎉", text_color="#2ECC71")
                self.play_finish_sound()
            except Exception as e:
                self.status_label.configure(text="Spotify indirme hatası!", text_color="#E74C3C")
                print("Spotify Hata Detayı:", e)
            finally:
                self.download_btn.configure(state="normal")
            return

        # --- Diğer Platformlar ---
        fmt = self.format_var.get()
        quality = self.quality_var.get()
        out_template = os.path.join(self.download_path, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': out_template,
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'merge_output_format': 'mp4',
            'noplaylist': False,
        }

        if fmt == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if quality == "1080p":
                format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
            elif quality == "720p":
                format_str = 'bestvideo[height<=720]+bestaudio/best[height<=720]/best'
            elif quality == "480p":
                format_str = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
            elif quality == "360p":
                format_str = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
            else:
                format_str = 'bestvideo+bestaudio/best'

            ydl_opts.update({'format': format_str})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="İndirme Tamamlandı! 🎉", text_color="#2ECC71")
            self.play_finish_sound()
        except Exception as e:
            self.status_label.configure(text="İndirme sırasında bir hata oluştu!", text_color="#E74C3C")
            print("Hata detayı:", e)
        finally:
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = MediaDownloaderApp()
    app.mainloop()