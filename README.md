# 🎵 Asker Media Studio

YouTube üzerinden ses (MP3) ve video (MP4) arayıp indirmeyi sağlayan, dahili oynatıcısı ve koyu teması bulunan masaüstü medya aracı.

---

### 📖 Projenin Çıkış Hikayesi
Bu proje, zorunlu askerlik görevim sırasında yaşadığım bir ihtiyaca pratik bir çözüm olarak doğdu. Askerde akıllı telefon kullanılamadığı için yanımda götürdüğüm tuşlu telefona müzik yüklemem gerekiyordu. 

İnternetten tek tek şarkı bulup dönüştürmek yerine; aradığım şarkıları doğrudan masaüstünden bularak 128kbps MP3 formatına dönüştüren ve tek tıkla microSD hafıza kartına atmama imkân tanıyan bu aracı geliştirdim.

---

## ✨ Özellikler

- **Hızlı Arama:** YouTube linkine ihtiyaç duymadan doğrudan şarkı veya sanatçı ismiyle arama yapma.
- **Arama Önizleme:** Arama sonuçlarından ilk 5 videoyu listeleyip isteneni seçebilme.
- **Format Seçenekleri:** 
  - **MP3 (Ses):** Eski/tuşlu telefonlar ve tüm MP3 çalarlarla %100 uyumlu 128kbps sıkıştırma.
  - **MP4 (Video):** Video ve sesi birleştiren yüksek kaliteli indirme.
- **Dahili Mini Çalar:** İndirilen parçaları başka programa gerek kalmadan uygulama içinden dinleme, duraklatma ve başa sarma.
- **Toplu İndirme (Playlist):** Belirlenen şarkı limiti kadar oynatma listesini sırayla indirebilme.
- **Doğrudan Klasör Erişimi:** İndirilen dosyaların olduğu hafıza kartı/klasörü tek tıkla Windows Gezgini'nde açma.

---

## 🛠️ Kurulum & Çalıştırma

### Gereksinimler
- **Python 3.9+** (Proje Python 3.9.21 ile test edilmiş ve derlenmiştir)**
- **FFmpeg:** MP3 dönüştürme ve video birleştirme işlemleri için `ffmpeg.exe` ve `ffprobe.exe` dosyalarının proje klasöründe (veya sistem PATH yolunda) bulunması gerekir.

### Adımlar

1. Depoyu klonlayın:
```bash
git clone [https://github.com/HEYDARBEK/muzik-indirme-uygulamasi.git](https://github.com/HEYDARBEK/muzik-indirme-uygulamasi.git)
cd muzik-indirme-uygulamasi