import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import yt_dlp

# Global durum değişkenleri
iptal_edildi = False
secilen_klasor = ""
tum_sarkilar = []
muzik_caliyor = False
muzik_duraklatildi = False
su_an_calan = ""
arama_sonuclari = []

pygame.mixer.init()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def uygulama_kapat():
    if messagebox.askokcancel("Çıkış", "Uygulamayı kapatmak istiyor musunuz?"):
        pygame.mixer.music.stop()
        root.destroy()


def klasor_sec():
    global secilen_klasor
    yol = filedialog.askdirectory(title="Kayıt ve Kütüphane Klasörü Seçin")
    if yol:
        secilen_klasor = yol
        lbl_klasor.config(text=f"📂 {os.path.basename(secilen_klasor)}")
        kütüphaneyi_güncelle()


def klasoru_ac():
    if secilen_klasor and os.path.exists(secilen_klasor):
        subprocess.Popen(f'explorer "{os.path.realpath(secilen_klasor)}"')
    else:
        messagebox.showwarning("Uyarı", "Geçerli bir klasör seçili değil!")


def kütüphaneyi_güncelle():
    global tum_sarkilar
    if secilen_klasor and os.path.exists(secilen_klasor):
        tum_sarkilar = sorted(
            [
                f
                for f in os.listdir(secilen_klasor)
                if f.lower().endswith((".mp3", ".mp4"))
            ]
        )
        filtrele_kutuphane()


def filtrele_kutuphane(*args):
    aranan = entry_lib_search.get().strip().lower()
    lib_list.delete(0, tk.END)
    for dosya in tum_sarkilar:
        if not aranan or aranan == "kütüphanede ara..." or aranan in dosya.lower():
            simge = "🎵" if dosya.lower().endswith(".mp3") else "🎬"
            lib_list.insert(tk.END, f"{simge} {dosya}")


def ses_ayar(val):
    pygame.mixer.music.set_volume(float(val) / 100)


# --- Çalar Kontrolleri (Düzeltilen Kısım) ---
def oynat_sarki(dosya_adi):
    """Verilen parçayı sıfırdan çalar ve buton durumlarını eşitler."""
    global muzik_caliyor, muzik_duraklatildi, su_an_calan
    tam_yol = os.path.join(secilen_klasor, dosya_adi)
    if not os.path.exists(tam_yol):
        messagebox.showerror("Hata", "Dosya bulunamadı!")
        return

    pygame.mixer.music.load(tam_yol)
    pygame.mixer.music.play()
    su_an_calan = dosya_adi
    muzik_caliyor = True
    muzik_duraklatildi = False

    btn_play_pause.config(text="⏸ DURAKLAT", bg="#ffffff", fg="#121212")
    lbl_now_playing.config(text=f"Çalıyor: {su_an_calan[:24]}...")


def oynat_veya_duraklat(event=None):
    global muzik_caliyor, muzik_duraklatildi, su_an_calan
    secili = lib_list.curselection()

    if secili:
        secilen_ham = lib_list.get(secili)
        dosya_adi = secilen_ham[2:].strip()  # '🎵 ' veya '🎬 ' simgesini temizle

        # Eğer video (MP4) seçildiyse: Önce çalan müziği kes, sonra videoyu aç
        if dosya_adi.lower().endswith(".mp4"):
            tam_durdur()
            tam_yol = os.path.join(secilen_klasor, dosya_adi)
            os.startfile(tam_yol)
            lbl_now_playing.config(text=f"Video Açıldı: {dosya_adi[:20]}...")
            return

        # Farklı bir MP3 seçildiyse doğrudan yeni şarkıyı başlat
        if dosya_adi != su_an_calan:
            oynat_sarki(dosya_adi)
            return

    # Aynı şarkı için Duraklat / Devam Et mekanizması
    if muzik_caliyor:
        if not muzik_duraklatildi:
            pygame.mixer.music.pause()
            muzik_duraklatildi = True
            btn_play_pause.config(text="▶ DEVAM ET", bg="#1DB954", fg="#ffffff")
            lbl_now_playing.config(text=f"Duraklatıldı: {su_an_calan[:22]}...")
        else:
            pygame.mixer.music.unpause()
            muzik_duraklatildi = False
            btn_play_pause.config(text="⏸ DURAKLAT", bg="#ffffff", fg="#121212")
            lbl_now_playing.config(text=f"Çalıyor: {su_an_calan[:24]}...")
    else:
        if secili:
            dosya_adi = lib_list.get(secili)[2:].strip()
            if dosya_adi.lower().endswith(".mp3"):
                oynat_sarki(dosya_adi)
        else:
            messagebox.showwarning("Uyarı", "Lütfen listeden bir MP3 seçin!")


def basa_sar():
    """Çalan şarkıyı en başa sarar."""
    global su_an_calan
    if su_an_calan and os.path.exists(os.path.join(secilen_klasor, su_an_calan)):
        oynat_sarki(su_an_calan)


def tam_durdur():
    """Çalmayı tamamen durdurur ve arayüzü temizler."""
    global muzik_caliyor, muzik_duraklatildi, su_an_calan
    pygame.mixer.music.stop()
    muzik_caliyor = False
    muzik_duraklatildi = False
    su_an_calan = ""
    btn_play_pause.config(text="▶ OYNAT", bg="#1DB954", fg="#ffffff")
    lbl_now_playing.config(text="Hazır")


def iptal_et():
    global iptal_edildi
    iptal_edildi = True
    update_status("⚠️ İptal ediliyor...")
    btn_iptal.config(state="disabled")


def update_status(text, is_progress=False, percent=0):
    def _up():
        if is_progress and status_list.size() > 0:
            last = status_list.get(tk.END)
            if any(m in last for m in ["⏳", "İndirme:", "✔️", "Dönüştürme"]):
                status_list.delete(tk.END)
        status_list.insert(tk.END, text)
        status_list.see(tk.END)
        progress_bar["value"] = percent

    root.after(0, _up)


def progress_hook(d):
    global iptal_edildi
    if iptal_edildi:
        raise Exception("İptal edildi")

    if d["status"] == "downloading":
        sarki = d.get("info_dict", {}).get("title", "Bilinmeyen")
        p_str = d.get("_percent_str", "0%").replace("%", "").strip()
        try:
            p_val = float(p_str)
        except:
            p_val = 0
        hiz = d.get("_speed_str", "N/A")
        update_status(
            f"   ⏳ %{p_val:.1f} | Hız: {hiz}", is_progress=True, percent=p_val
        )
    elif d["status"] == "finished":
        update_status(
            "   ✔️ İndirme tamamlandı, derleniyor...",
            is_progress=True,
            percent=100,
        )


def youtube_ara():
    global arama_sonuclari
    query = entry_url.get().strip()
    if not query or query == placeholder_text:
        messagebox.showwarning("Uyarı", "Lütfen bir arama kelimesi girin!")
        return

    if "http://" in query or "https://" in query:
        messagebox.showinfo(
            "Bilgi", "Doğrudan bağlantı girdiniz. 'İNDİR' butonuna basabilirsiniz."
        )
        return

    def run():
        global arama_sonuclari
        btn_ara.config(state="disabled")
        update_status(f"🔍 '{query}' aranıyor...")
        search_list.delete(0, tk.END)

        opts = {"extract_flat": True, "quiet": True, "no_warnings": True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                res = ydl.extract_info(f"ytsearch5:{query}", download=False)
                arama_sonuclari = [
                    (entry.get("title"), entry.get("url"))
                    for entry in res.get("entries", [])
                ]

            root.after(0, arama_listesini_doldur)
            update_status("✅ Sonuçlar listelendi. Parçayı seçip indirebilirsiniz.")
        except Exception as e:
            update_status(f"❌ Arama hatası: {str(e)}")
        finally:
            btn_ara.config(state="normal")

    threading.Thread(target=run, daemon=True).start()


def arama_listesini_doldur():
    search_list.delete(0, tk.END)
    for title, _ in arama_sonuclari:
        search_list.insert(tk.END, f"  {title}")
    if arama_sonuclari:
        search_list.select_set(0)


def muzik_indir():
    global iptal_edildi
    iptal_edildi = False

    if not secilen_klasor or not os.path.exists(secilen_klasor):
        messagebox.showwarning("Uyarı", "Lütfen önce bir indirme klasörü seçin!")
        return

    query = entry_url.get().strip()
    hedef_url = ""

    secili_arama = search_list.curselection()
    if secili_arama and arama_sonuclari:
        hedef_url = arama_sonuclari[secili_arama[0]][1]
    elif "http://" in query or "https://" in query:
        hedef_url = query
    elif query and query != placeholder_text:
        hedef_url = f"ytsearch1:{query}"
    else:
        messagebox.showwarning(
            "Uyarı", "Lütfen bir link girin veya arama listesinden seçim yapın!"
        )
        return

    format_secimi = combo_format.get()
    try:
        limit = int(entry_limit.get())
    except:
        limit = 20

    def run():
        btn_indir.config(state="disabled")
        btn_iptal.config(state="normal")
        root.after(0, lambda: status_list.delete(0, tk.END))
        update_status(f"🚀 İndirme başlatılıyor ({format_secimi})...")

        ayarlar = {
            "ffmpeg_location": resource_path(""),
            "outtmpl": os.path.join(secilen_klasor, "%(title)s.%(ext)s"),
            "noplaylist": not var_playlist.get(),
            "playlist_items": f"1-{limit}" if var_playlist.get() else "1",
            "progress_hooks": [progress_hook],
            "windowsfilenames": True,
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0 Safari/537.36"
            },
        }

        if format_secimi.startswith("MP3"):
            ayarlar["format"] = "bestaudio/best"
            ayarlar["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ]
        else:
            ayarlar["format"] = (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            )
            ayarlar["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ayarlar) as ydl:
                ydl.download([hedef_url])

            update_status("✅ Dosya başarıyla kaydedildi!", percent=100)
            root.after(0, kütüphaneyi_güncelle)
            root.after(0, lambda: messagebox.showinfo("Başarılı", "İndirme bitti!"))
        except Exception as e:
            if "İptal" in str(e):
                update_status("❌ İndirme durduruldu.")
            else:
                update_status(f"❌ Hata: {str(e)}")
        finally:
            btn_indir.config(state="normal")
            btn_iptal.config(state="disabled")
            root.after(0, lambda: progress_bar.configure(value=0))

    threading.Thread(target=run, daemon=True).start()


# --- Arayüz Düzeni ---
root = tk.Tk()
root.title("Asker Media Studio v5.3")
root.geometry("1060x750")
root.minsize(1000, 700)
root.configure(bg="#0c0c0c")
root.protocol("WM_DELETE_WINDOW", uygulama_kapat)

placeholder_text = "Şarkı adı veya YouTube linki..."

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TProgressbar", thickness=8, background="#1DB954", troughcolor="#222222"
)
style.configure(
    "TCombobox",
    fieldbackground="#242424",
    background="#242424",
    foreground="white",
    darkcolor="#181818",
    lightcolor="#181818",
)

main_container = tk.Frame(root, bg="#0c0c0c")
main_container.pack(fill="both", expand=True, padx=15, pady=15)

# ----------------- SOL KART (İNDİRİCİ & ARAMA) -----------------
card_left = tk.Frame(main_container, bg="#181818", bd=0, padx=20, pady=15)
card_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

tk.Label(
    card_left,
    text="Medya İndirme & Arama",
    fg="#1DB954",
    bg="#181818",
    font=("Segoe UI", 15, "bold"),
).pack(anchor="w", pady=(0, 10))

search_box = tk.Frame(card_left, bg="#181818")
search_box.pack(fill="x", pady=(0, 10))

entry_url = tk.Entry(
    search_box,
    font=("Segoe UI", 10),
    bg="#242424",
    fg="#888888",
    bd=0,
    insertbackground="white",
)
entry_url.insert(0, placeholder_text)
entry_url.bind(
    "<FocusIn>",
    lambda e: (
        entry_url.delete(0, "end") if entry_url.get() == placeholder_text else None,
        entry_url.config(fg="#ffffff"),
    ),
)
entry_url.bind(
    "<FocusOut>",
    lambda e: (
        entry_url.insert(0, placeholder_text) if not entry_url.get().strip() else None,
        entry_url.config(fg="#888888") if not entry_url.get().strip() else None,
    ),
)
entry_url.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))

btn_ara = tk.Button(
    search_box,
    text="🔍 ARA",
    command=youtube_ara,
    bg="#333333",
    fg="#ffffff",
    font=("Segoe UI", 9, "bold"),
    bd=0,
    padx=12,
    pady=4,
    activebackground="#444444",
)
btn_ara.pack(side="right")

tk.Label(
    card_left,
    text="Arama Sonuçları (İndirmek istediğinizi seçin):",
    fg="#888888",
    bg="#181818",
    font=("Segoe UI", 8),
).pack(anchor="w")
search_list = tk.Listbox(
    card_left,
    height=4,
    bg="#121212",
    fg="#ffffff",
    font=("Segoe UI", 9),
    bd=0,
    highlightthickness=0,
    selectbackground="#1DB954",
)
search_list.pack(fill="x", pady=(3, 10))

row_opts = tk.Frame(card_left, bg="#181818")
row_opts.pack(fill="x", pady=(0, 10))

tk.Button(
    row_opts,
    text="📁 Klasör Seç",
    command=klasor_sec,
    bg="#2a2a2a",
    fg="#ffffff",
    font=("Segoe UI", 9),
    bd=0,
    padx=8,
    pady=3,
).pack(side="left")
lbl_klasor = tk.Label(
    row_opts,
    text="Henüz seçilmedi",
    fg="#aaaaaa",
    bg="#181818",
    font=("Segoe UI", 9),
)
lbl_klasor.pack(side="left", padx=6)

combo_format = ttk.Combobox(
    row_opts,
    values=["MP3 (Ses)", "MP4 (Video)"],
    state="readonly",
    width=11,
    font=("Segoe UI", 9),
)
combo_format.set("MP3 (Ses)")
combo_format.pack(side="right", padx=(8, 0))

var_playlist = tk.BooleanVar(value=False)
tk.Checkbutton(
    row_opts,
    text="Playlist",
    variable=var_playlist,
    bg="#181818",
    fg="#ffffff",
    selectcolor="#242424",
    font=("Segoe UI", 9),
).pack(side="right")
entry_limit = tk.Entry(
    row_opts,
    width=3,
    bg="#242424",
    fg="#ffffff",
    bd=0,
    font=("Segoe UI", 9),
    justify="center",
)
entry_limit.insert(0, "20")
entry_limit.pack(side="right", padx=3, ipady=2)

btn_row = tk.Frame(card_left, bg="#181818")
btn_row.pack(fill="x", pady=(0, 10))

btn_indir = tk.Button(
    btn_row,
    text="İNDİR",
    command=muzik_indir,
    bg="#1DB954",
    fg="#ffffff",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    height=2,
    activebackground="#179b44",
)
btn_indir.pack(side="left", fill="x", expand=True, padx=(0, 5))

btn_iptal = tk.Button(
    btn_row,
    text="İPTAL",
    command=iptal_et,
    bg="#333333",
    fg="#e74c3c",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    height=2,
    state="disabled",
)
btn_iptal.pack(side="right", fill="x", expand=True, padx=(5, 0))

progress_bar = ttk.Progressbar(
    card_left, orient="horizontal", mode="determinate", style="TProgressbar"
)
progress_bar.pack(fill="x", pady=(0, 10))

status_list = tk.Listbox(
    card_left,
    bg="#111111",
    fg="#999999",
    font=("Consolas", 9),
    bd=0,
    highlightthickness=0,
)
status_list.pack(fill="both", expand=True, pady=(0, 10))

tk.Button(
    card_left,
    text="✕ Uygulamadan Çık",
    command=uygulama_kapat,
    bg="#1f1f1f",
    fg="#888888",
    font=("Segoe UI", 9),
    bd=0,
    pady=5,
).pack(fill="x")

# ----------------- SAĞ KART (KÜTÜPHANE & OYNATICI) -----------------
card_right = tk.Frame(main_container, bg="#181818", bd=0, padx=15, pady=15)
card_right.pack(side="right", fill="both", expand=False)
card_right.config(width=340)

tk.Label(
    card_right,
    text="Kütüphane",
    fg="#ffffff",
    bg="#181818",
    font=("Segoe UI", 14, "bold"),
).pack(anchor="w", pady=(0, 8))

entry_lib_search = tk.Entry(
    card_right,
    font=("Segoe UI", 9),
    bg="#242424",
    fg="#888888",
    bd=0,
    insertbackground="white",
)
entry_lib_search.insert(0, "Kütüphanede ara...")
entry_lib_search.bind(
    "<FocusIn>",
    lambda e: (
        entry_lib_search.delete(0, "end")
        if entry_lib_search.get() == "Kütüphanede ara..."
        else None,
        entry_lib_search.config(fg="#ffffff"),
    ),
)
entry_lib_search.bind(
    "<FocusOut>",
    lambda e: (
        entry_lib_search.insert(0, "Kütüphanede ara...")
        if not entry_lib_search.get().strip()
        else None,
        (
            entry_lib_search.config(fg="#888888")
            if not entry_lib_search.get().strip()
            else None
        ),
    ),
)
entry_lib_search.bind("<KeyRelease>", filtrele_kutuphane)
entry_lib_search.pack(fill="x", ipady=5, pady=(0, 8))

lib_list = tk.Listbox(
    card_right,
    width=38,
    bg="#111111",
    fg="#e0e0e0",
    font=("Segoe UI", 9),
    bd=0,
    highlightthickness=0,
    selectbackground="#1DB954",
)
lib_list.bind("<Double-Button-1>", oynat_veya_duraklat)
lib_list.pack(fill="both", expand=True, pady=(0, 8))

lbl_now_playing = tk.Label(
    card_right,
    text="Hazır",
    fg="#1DB954",
    bg="#181818",
    font=("Segoe UI", 9, "italic"),
)
lbl_now_playing.pack(pady=(0, 6))

# Kontrol Paneli (Başa Sar, Oynat/Duraklat, Durdur)
ctrl_box = tk.Frame(card_right, bg="#181818")
ctrl_box.pack(fill="x", pady=(0, 8))

tk.Button(
    ctrl_box,
    text="⏮",
    command=basa_sar,
    bg="#242424",
    fg="#ffffff",
    font=("Segoe UI", 10),
    bd=0,
    width=4,
    height=2,
    activebackground="#333333",
).pack(side="left", padx=(0, 3))

btn_play_pause = tk.Button(
    ctrl_box,
    text="▶ OYNAT",
    command=oynat_veya_duraklat,
    bg="#1DB954",
    fg="#ffffff",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    height=2,
)
btn_play_pause.pack(side="left", fill="x", expand=True, padx=3)

tk.Button(
    ctrl_box,
    text="⏹",
    command=tam_durdur,
    bg="#242424",
    fg="#e74c3c",
    font=("Segoe UI", 10),
    bd=0,
    width=4,
    height=2,
    activebackground="#333333",
).pack(side="right", padx=(3, 0))

# Ses Kontrolü
vol_box = tk.Frame(card_right, bg="#181818")
vol_box.pack(fill="x", pady=(0, 8))

tk.Label(
    vol_box,
    text="🔊",
    fg="#888888",
    bg="#181818",
    font=("Segoe UI Emoji", 10),
).pack(side="left", padx=(0, 6))
volume_slider = tk.Scale(
    vol_box,
    from_=0,
    to=100,
    orient="horizontal",
    command=ses_ayar,
    bg="#181818",
    fg="#888888",
    highlightthickness=0,
    bd=0,
    troughcolor="#242424",
    activebackground="#1DB954",
    showvalue=False,
)
volume_slider.set(70)
pygame.mixer.music.set_volume(0.7)
volume_slider.pack(side="left", fill="x", expand=True)

tk.Button(
    card_right,
    text="📂 Klasörü Aç",
    command=klasoru_ac,
    bg="#242424",
    fg="#ffffff",
    font=("Segoe UI", 9),
    bd=0,
    pady=5,
).pack(fill="x")

root.mainloop()
