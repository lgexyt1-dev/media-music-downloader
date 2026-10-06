import customtkinter as ctk
from tkinter import filedialog, colorchooser
import yt_dlp
import threading
import os
import subprocess
import winsound  # İndirme bitince sesli bildirim çalmak için
import queue

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
        self.ui_events = queue.Queue()
        self.download_active = False

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
        self.after(100, self.process_ui_events)

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
            except Exception:
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
                speed = d.get('_speed_str', '').strip()
                self.ui_events.put((
                    "progress", percentage,
                    f"{prefix}İndiriliyor: %{int(percentage * 100)} | Hız: {speed}"
                ))

        elif d['status'] == 'finished':
            self.ui_events.put((
                "status", "İşleniyor (FFmpeg dönüştürmesi yapılıyor)...", "#3498DB"
            ))

    def start_download_thread(self):
        if self.download_active:
            return
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Lütfen geçerli bir link girin!", text_color="#E74C3C")
            return

        self.download_active = True
        self.progress_bar.set(0)
        self.status_label.configure(text="İndirme başlatılıyor...", text_color="#F1C40F")
        self.download_btn.configure(state="disabled")
        threading.Thread(
            target=self.download_media,
            args=(url, self.format_var.get(), self.quality_var.get(), self.download_path),
            daemon=True
        ).start()

    def process_ui_events(self):
        while True:
            try:
                event = self.ui_events.get_nowait()
            except queue.Empty:
                break
            if event[0] == "progress":
                _, percentage, message = event
                self.progress_bar.set(max(0, min(1, percentage)))
                self.status_label.configure(text=message, text_color="#F1C40F")
            elif event[0] == "status":
                _, message, color = event
                self.status_label.configure(text=message, text_color=color)
            elif event[0] == "complete":
                _, succeeded, message, color = event
                self.download_active = False
                self.download_btn.configure(state="normal")
                if succeeded:
                    self.progress_bar.set(1.0)
                    self.play_finish_sound()
                self.status_label.configure(text=message, text_color=color)
        self.after(100, self.process_ui_events)

    def download_media(self, url, fmt, quality, download_path):
        try:
            os.makedirs(download_path, exist_ok=True)
            if "spotify.com" in url.lower():
                self.ui_events.put(("status", "Spotify içeriği indiriliyor...", "#3498DB"))
                cmd = ["spotdl", "download", url, "--output", download_path]
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            else:
                out_template = os.path.join(download_path, '%(title)s.%(ext)s')
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
                    height = {
                        "1080p": 1080, "720p": 720, "480p": 480, "360p": 360
                    }.get(quality)
                    format_str = (
                        f'bestvideo[height<={height}]+bestaudio/'
                        f'best[height<={height}]/best'
                        if height else 'bestvideo+bestaudio/best'
                    )
                    ydl_opts.update({'format': format_str})

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

            self.ui_events.put(("complete", True, "İndirme Tamamlandı! 🎉", "#2ECC71"))
        except Exception as error:
            detail = str(error).strip()
            message = f"İndirme sırasında hata: {detail[:180]}" if detail else "İndirme başarısız oldu!"
            self.ui_events.put(("complete", False, message, "#E74C3C"))

if __name__ == "__main__":
    app = MediaDownloaderApp()
    app.mainloop()