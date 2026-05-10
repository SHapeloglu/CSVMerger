"""
CSV Birleştirici
-----------------
Belirtilen klasördeki tüm .csv dosyalarını okur,
başlıkları tek seferde yazar ve tüm veriyi tek bir
çıktı CSV'sine birleştirir.

Kullanım:
  python merge.py                          # varsayılan: source/ klasörü
  python merge.py -i ./parcalar            # özel giriş klasörü
  python merge.py -i ./parcalar -o birlesik.csv
  python merge.py -p "11-*.csv"            # belirli dosya deseni
  python merge.py --auto-encoding          # encoding otomatik tespit

Değişiklikler (v2):
  - Glob pattern + input_dir çakışması düzeltildi
  - Encoding otomatik tespiti eklendi (chardet veya fallback)
  - ProgressBar utils.py'ye taşındı (DRY)
  - Log dosyası desteği eklendi
  - Boş / bozuk satır istatistikleri eklendi
"""

import argparse
import csv
import glob
import logging
import os
import re
import sys
import time
from pathlib import Path

from utils import ProgressBar, detect_encoding


# ── Ayarlar ──────────────────────────────────────────────────────────────────
DEFAULT_INPUT   = "source"           # Kaynak CSV'lerin arandığı varsayılan klasör
DEFAULT_PATTERN = "*.csv"            # Hangi dosyaların alınacağını belirleyen glob deseni
DEFAULT_OUTPUT  = "birlesik_cikti.csv"  # Birleşik çıktı dosyasının adı
LOG_FILE        = "merge.log"        # Varsayılan log dosyası adı
# ─────────────────────────────────────────────────────────────────────────────


def setup_logging(log_file: str):
    """
    Logging'i hem dosyaya hem de stdout'a yazacak şekilde yapılandırır.
    Tüm INFO ve üstü mesajlar her iki hedefe de iletilir.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),  # Kalıcı log dosyası
            logging.StreamHandler(sys.stdout),                 # Anlık terminal çıktısı
        ],
    )


def natural_sort_key(path: str):
    """
    Dosya adlarını doğal sırayla sıralamak için anahtar üretir.

    Saf string sıralaması "10" < "2" sonucu verir (leksikografik).
    Bu fonksiyon dosya adını rakam / metin parçalarına böler ve
    rakam parçalarını int'e çevirerek doğru sıra sağlar:
      1-data.csv, 2-data.csv, 10-data.csv  ✓
    """
    parts = re.split(r"(\d+)", Path(path).stem)
    # Rakam parçası → int, metin parçası → küçük harfe çevir
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def find_csv_files(input_dir: Path, pattern: str, output_path: Path) -> list:
    """
    Verilen klasörde pattern'e uyan CSV dosyalarını bulur ve
    çıktı dosyasını listeden hariç tutar.

    Args:
        input_dir:   Arama yapılacak klasör (Path nesnesi).
        pattern:     Glob deseni, örn. '*.csv' veya '11-*.csv'.
        output_path: Birleşik çıktı dosyası; aynı klasördeyse listeye girmemeli.

    Returns:
        Doğal sırayla sıralanmış dosya yolları listesi.

    DÜZELTME (v2): Önceki sürümde `input_dir / pattern` kullanılıyordu; bu,
    -i ve -p argümanları birlikte verildiğinde yanlış yol üretiyordu çünkü
    pattern zaten tam yol içerebiliyordu. Artık input_dir ve pattern ayrı
    tutularak glob'a birleşik string verilmektedir.
    """
    # input_dir ile pattern'i birleştirerek tam arama yolu oluştur
    search_path = str(input_dir / pattern)
    files = sorted(glob.glob(search_path), key=natural_sort_key)

    # Çıktı dosyası kaynak klasördeyse tekrar okunmasını önle
    files = [f for f in files if Path(f).resolve() != output_path.resolve()]
    return files


def merge(
    input_dir: str,
    output_file: str,
    pattern: str,
    encoding: str,
    auto_encoding: bool,
):
    """
    Ana birleştirme işlevi.

    Adımlar:
      1. Kaynak klasörün varlığını kontrol et.
      2. Pattern'e uyan CSV dosyalarını bul ve doğal sırala.
      3. Her dosyayı aç; başlığı ilk dosyadan al, sonrakilerle karşılaştır.
      4. Farklı başlıklı veya boş dosyaları atla, logla.
      5. Tamamen boş veri satırlarını filtrele.
      6. Tüm geçerli satırları çıktı dosyasına yaz.
      7. Özet istatistikleri logla.

    Args:
        input_dir:     Kaynak CSV klasörü.
        output_file:   Birleşik çıktı dosyasının yolu.
        pattern:       Glob deseni (örn. '*.csv').
        encoding:      auto_encoding=False ise kullanılacak sabit encoding.
        auto_encoding: True ise her dosya için encoding otomatik tespit edilir.
    """
    input_dir   = Path(input_dir)
    output_path = Path(output_file)

    # Kaynak klasör yoksa anlamlı hata mesajıyla çık
    if not input_dir.exists():
        logging.error(f"Klasör bulunamadı: {input_dir}")
        sys.exit(1)

    files = find_csv_files(input_dir, pattern, output_path)

    # Hiç dosya bulunamadıysa devam etmenin anlamı yok
    if not files:
        logging.warning(f"'{pattern}' desenine uyan CSV bulunamadı: {input_dir}")
        sys.exit(1)

    logging.info(f"Giriş    : {input_dir}")
    logging.info(f"Bulunan  : {len(files)} CSV dosyası")
    logging.info(f"Çıktı    : {output_path}")

    header        = None   # İlk dosyadan alınan referans başlık satırı
    total_rows    = 0      # Başarıyla yazılan toplam veri satırı sayısı
    skipped_files = []     # (dosya_yolu, sebep) çiftlerinden oluşan atlanan dosya listesi
    empty_rows    = 0      # Tamamen boş olduğu için atlanan satır sayısı
    progress      = ProgressBar(total=len(files), label="Birleştiriliyor")

    # Çıktı dosyasını baştan yaz; encoding her zaman utf-8 (tutarlılık için)
    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = None  # İlk dosya işlenene kadar writer None kalır

        for fpath in files:
            # Her dosya için encoding'i ya otomatik tespit et ya da sabit kullan
            file_enc = detect_encoding(fpath) if auto_encoding else encoding

            try:
                with open(fpath, "r", newline="", encoding=file_enc, errors="replace") as in_f:
                    reader = csv.reader(in_f)

                    # İlk satırı başlık olarak oku; dosya tamamen boşsa StopIteration alırız
                    try:
                        file_header = next(reader)
                    except StopIteration:
                        skipped_files.append((fpath, "boş dosya"))
                        logging.warning(f"Atlandı (boş): {fpath}")
                        progress.update()
                        continue

                    if header is None:
                        # İlk dosya: bu başlığı referans olarak kaydet ve çıktıya yaz
                        header = file_header
                        writer = csv.writer(out_f, lineterminator="\n")
                        writer.writerow(header)
                    elif file_header != header:
                        # Başlık uyuşmazlığı: veri bütünlüğünü korumak için dosyayı atla
                        skipped_files.append((fpath, f"farklı başlık: {file_header}"))
                        logging.warning(f"Atlandı (farklı başlık): {Path(fpath).name}")
                        progress.update()
                        continue

                    row_count = 0
                    for row in reader:
                        # Tüm hücreler boş veya yalnızca boşluktan oluşan satırları atla
                        if not any(cell.strip() for cell in row):
                            empty_rows += 1
                            continue
                        writer.writerow(row)
                        row_count += 1

                    total_rows += row_count

            except Exception as e:
                # Beklenmedik hata (izin sorunu, bozuk dosya vb.)
                skipped_files.append((fpath, str(e)))
                logging.error(f"Hata ({Path(fpath).name}): {e}")

            progress.update()

    # İşlem bitti; süre ve boyut istatistiklerini hesapla
    elapsed  = time.time() - progress.start
    out_size = output_path.stat().st_size / 1024

    logging.info("Tamamlandı!")
    logging.info(f"  Birleştirilen : {len(files) - len(skipped_files)} dosya")
    logging.info(f"  Toplam satır  : {total_rows:,}")
    logging.info(f"  Boş satır     : {empty_rows:,} (atlandı)")
    logging.info(f"  Çıktı boyutu  : {out_size:.1f} KB")
    logging.info(f"  Süre          : {elapsed:.1f}s")
    logging.info(f"  Çıktı         : {output_path.resolve()}")

    # Atlanan dosyalar varsa tek tek logla
    if skipped_files:
        logging.warning(f"Atlanan dosyalar ({len(skipped_files)}):")
        for f, reason in skipped_files:
            logging.warning(f"  - {Path(f).name}: {reason}")

    print(f"\n🎉 Tamamlandı! {total_rows:,} satır → {output_path}")


def main():
    """CLI argümanlarını ayrıştırır ve merge() işlevini çağırır."""
    parser = argparse.ArgumentParser(
        description="Birden fazla CSV dosyasını tek dosyada birleştir"
    )
    parser.add_argument(
        "-i", "--input",
        default=DEFAULT_INPUT,
        help=f"CSV dosyalarının bulunduğu klasör (varsayılan: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help=f"Çıktı dosyası adı (varsayılan: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "-p", "--pattern",
        default=DEFAULT_PATTERN,
        help=f"Dosya deseni (varsayılan: {DEFAULT_PATTERN}, örnek: '11-*.csv')",
    )
    parser.add_argument(
        "-e", "--encoding",
        default="utf-8",
        help="Sabit encoding (--auto-encoding kullanılmıyorsa, varsayılan: utf-8)",
    )
    parser.add_argument(
        "--auto-encoding",
        action="store_true",
        help="Her dosya için encoding otomatik tespit et (chardet önerilir)",
    )
    parser.add_argument(
        "--log",
        default=LOG_FILE,
        help=f"Log dosyası yolu (varsayılan: {LOG_FILE})",
    )
    args = parser.parse_args()
    setup_logging(args.log)
    merge(
        input_dir=args.input,
        output_file=args.output,
        pattern=args.pattern,
        encoding=args.encoding,
        auto_encoding=args.auto_encoding,
    )


if __name__ == "__main__":
    main()
