"""
CSV Birleştirici
-----------------
Belirtilen klasördeki tüm .csv dosyalarını okur,
başlıkları tek seferde yazar ve tüm veriyi tek bir
çıktı CSV'sine birleştirir.

Kullanım:
  python merge.py                          # varsayılan: script klasörü
  python merge.py -i ./parcalar            # özel giriş klasörü
  python merge.py -i ./parcalar -o birlesik.csv
  python merge.py -p "11-*.csv"            # belirli dosya deseni
"""

import argparse
import csv
import glob
import os
import sys
import time
from pathlib import Path


# ── Ayarlar ──────────────────────────────────────────────────────────────────
DEFAULT_PATTERN = "source/*.csv"
DEFAULT_OUTPUT  = "birlesik_cikti.csv"
# ─────────────────────────────────────────────────────────────────────────────


class ProgressBar:
    def __init__(self, total: int, label: str = ""):
        self.total = total
        self.done  = 0
        self.label = label
        self.start = time.time()
        self.width = 35

    def update(self, n: int = 1):
        self.done += n
        pct     = self.done / self.total if self.total else 1
        filled  = int(self.width * pct)
        bar     = "█" * filled + "░" * (self.width - filled)
        elapsed = time.time() - self.start
        eta     = (elapsed / pct - elapsed) if pct > 0 else 0
        sys.stdout.write(
            f"\r{self.label} [{bar}] "
            f"{self.done}/{self.total} ({pct*100:.1f}%)  ETA: {eta:.0f}s  "
        )
        sys.stdout.flush()
        if self.done >= self.total:
            sys.stdout.write("\n"); sys.stdout.flush()


def find_csv_files(input_dir: Path, pattern: str, output_path: Path) -> list:
    """Klasördeki CSV dosyalarını sıralı olarak bul, çıktı dosyasını hariç tut."""
    files = sorted(glob.glob(str(input_dir / pattern)))
    # Çıktı dosyası aynı klasördeyse listeye girmesin
    files = [f for f in files if Path(f).resolve() != output_path.resolve()]
    return files


def natural_sort_key(path: str):
    """
    Dosyaları doğal sırayla sıralar: 1-, 2-, ..., 10-, 11- gibi.
    Saf string sıralama yerine sayısal parçaları int'e çevirir.
    """
    import re
    parts = re.split(r'(\d+)', Path(path).stem)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def merge(input_dir: str, output_file: str, pattern: str, encoding: str):
    input_dir   = Path(input_dir)
    output_path = Path(output_file)

    if not input_dir.exists():
        print(f"❌ Klasör bulunamadı: {input_dir}")
        sys.exit(1)

    files = find_csv_files(input_dir, pattern, output_path)
    files.sort(key=natural_sort_key)

    if not files:
        print(f"⚠️  '{pattern}' desenine uyan CSV dosyası bulunamadı: {input_dir}")
        sys.exit(1)

    print(f"\n📂 Giriş    : {input_dir}")
    print(f"🔍 Bulunan  : {len(files)} CSV dosyası")
    print(f"📄 Çıktı    : {output_path}\n")

    header        = None
    total_rows    = 0
    skipped_files = []
    progress      = ProgressBar(total=len(files), label="Birleştiriliyor")

    with open(output_path, "w", newline="", encoding=encoding) as out_f:
        writer = None

        for fpath in files:
            try:
                with open(fpath, "r", newline="", encoding=encoding, errors="replace") as in_f:
                    reader = csv.reader(in_f)
                    try:
                        file_header = next(reader)
                    except StopIteration:
                        skipped_files.append((fpath, "boş dosya"))
                        progress.update()
                        continue

                    # İlk dosyada başlığı yaz
                    if header is None:
                        header = file_header
                        writer = csv.writer(out_f, lineterminator="\n")
                        writer.writerow(header)
                    elif file_header != header:
                        skipped_files.append((fpath, f"farklı başlık: {file_header}"))
                        progress.update()
                        continue

                    # Veri satırlarını yaz
                    row_count = 0
                    for row in reader:
                        writer.writerow(row)
                        row_count += 1
                    total_rows += row_count

            except Exception as e:
                skipped_files.append((fpath, str(e)))

            progress.update()

    elapsed = time.time() - progress.start
    out_size = output_path.stat().st_size / 1024

    print(f"\n🎉 Tamamlandı!")
    print(f"   Birleştirilen dosya : {len(files) - len(skipped_files)}")
    print(f"   Toplam veri satırı  : {total_rows:,}")
    print(f"   Çıktı boyutu        : {out_size:.1f} KB")
    print(f"   Süre                : {elapsed:.1f}s")
    print(f"   Çıktı               : {output_path.resolve()}\n")

    if skipped_files:
        print(f"⚠️  Atlanan dosyalar ({len(skipped_files)}):")
        for f, reason in skipped_files:
            print(f"   - {Path(f).name}: {reason}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Birden fazla CSV dosyasını tek dosyada birleştir"
    )
    parser.add_argument(
        "-i", "--input",
        default=".",
        help="CSV dosyalarının bulunduğu klasör (varsayılan: script klasörü)"
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help=f"Çıktı dosyası adı (varsayılan: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "-p", "--pattern",
        default=DEFAULT_PATTERN,
        help=f"Dosya deseni (varsayılan: {DEFAULT_PATTERN}, örnek: '11-*.csv')"
    )
    parser.add_argument(
        "-e", "--encoding",
        default="utf-8",
        help="Dosya encoding (varsayılan: utf-8)"
    )
    args = parser.parse_args()
    merge(args.input, args.output, args.pattern, args.encoding)


if __name__ == "__main__":
    main()
