"""
Ortak yardımcı modül
---------------------
ProgressBar ve encoding tespiti gibi paylaşılan araçlar burada tutulur.
Her iki ana script (merge.py, csv_to_mysql.py) bu modülü import eder;
aynı kodu iki yerde tutmaya gerek kalmaz (DRY prensibi).
"""

import sys
import time


# ── ProgressBar ───────────────────────────────────────────────────────────────

class ProgressBar:
    """
    Tek satırda güncellenen terminal ilerleme çubuğu.

    Kullanım:
        pb = ProgressBar(total=100, label="İşleniyor")
        pb.update()        # +1
        pb.update(10)      # +10
    """

    def __init__(self, total: int, label: str = ""):
        self.total = total        # İşlenecek toplam birim sayısı
        self.done  = 0            # Şimdiye kadar tamamlanan birim
        self.label = label        # Çubuğun sol tarafındaki başlık metni
        self.start = time.time()  # Başlangıç zamanı (ETA hesabı için)
        self.width = 35           # Çubuğun karakter cinsinden genişliği

    def update(self, n: int = 1):
        """
        İlerlemeyi `n` birim artırır ve çubuğu terminalde yeniden çizer.
        Son birime ulaşıldığında satır sonu yazarak çubuğu sabitler.
        """
        self.done += n

        # Tamamlanma oranı (0.0 – 1.0); total=0 ise bölme hatasını önlemek için 1 kullan
        pct = self.done / self.total if self.total else 1

        # Dolu ve boş blok sayısını orana göre hesapla
        filled = int(self.width * pct)
        bar    = "█" * filled + "░" * (self.width - filled)

        # Geçen süre ve kalan tahmini süre (ETA)
        elapsed = time.time() - self.start
        eta     = (elapsed / pct - elapsed) if pct > 0 else 0

        # \r ile imleci satır başına taşı, böylece aynı satır üzerine yaz
        sys.stdout.write(
            f"\r{self.label} [{bar}] "
            f"{self.done:,}/{self.total:,} ({pct*100:.1f}%)  ETA: {eta:.0f}s  "
        )
        sys.stdout.flush()

        # İşlem bitince kalıcı satır sonu yaz
        if self.done >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()


# ── Encoding tespiti ──────────────────────────────────────────────────────────

def detect_encoding(path: str, fallback: str = "utf-8") -> str:
    """
    Verilen dosyanın karakter kodlamasını (encoding) tespit eder.

    Öncelik sırası:
      1. chardet kütüphanesi kuruluysa binary içeriği analiz eder.
         Güven skoru %50'nin altındaysa sonuç güvenilmez kabul edilip
         `fallback` değerine düşülür.
      2. chardet kurulu değilse sık kullanılan encodingleri sırayla dener:
         utf-8-sig → utf-8 → cp1254 (Türkçe Windows) → latin-1
         İlk başarılı okumayı döner.
      3. Hiçbiri çalışmazsa `fallback` döner (varsayılan: utf-8).

    Args:
        path:     Okunacak dosyanın tam yolu.
        fallback: Tespit başarısız olursa döndürülecek encoding adı.

    Returns:
        Encoding adı (str), örn. 'utf-8', 'cp1254', 'latin-1'.
    """
    try:
        import chardet

        # Büyük dosyaları tamamı yerine ilk 1 MB ile analiz et (yeterli doğruluk sağlar)
        with open(path, "rb") as f:
            raw = f.read(min(1_000_000, _file_size(path)))

        result     = chardet.detect(raw)
        enc        = result.get("encoding") or fallback
        confidence = result.get("confidence", 0)

        # Güven skoru düşükse chardet tahminine güvenme
        if confidence < 0.5:
            enc = fallback

        return enc

    except ImportError:
        # chardet kurulu değil; sessizce fallback yöntemine geç
        pass

    # chardet yoksa: her encoding'i 4 KB'lık örnek okuyarak test et
    for enc in ("utf-8-sig", "utf-8", "cp1254", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as f:
                f.read(4096)   # Decode hatası alırsak except'e düşer
            return enc
        except (UnicodeDecodeError, LookupError):
            continue  # Bu encoding çalışmadı, bir sonrakini dene

    # Son çare: hiçbir deneme başarılı olmadı
    return fallback


def _file_size(path: str) -> int:
    """Dosyanın bayt cinsinden boyutunu döner (chardet örnekleme sınırı için)."""
    import os
    return os.path.getsize(path)
