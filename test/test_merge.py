"""
Unit testler — merge.py ve utils.py
-------------------------------------
Her test fonksiyonu bağımsız çalışır; dış bağımlılık (MySQL, ağ) gerektirmez.

Çalıştır:
    pytest tests/test_merge.py -v

Kapsam:
    - natural_sort_key : doğal sıralama mantığı
    - find_csv_files   : glob + output dosyası hariç tutma
    - merge()          : normal birleştirme, başlık uyuşmazlığı, boş dosya,
                         boş satır filtreleme, output/source çakışma koruması
    - detect_encoding  : UTF-8 ve Latin-1 tespiti
    - ProgressBar      : tamamlama durumu
    - Veri dosyaları   : örnek CSV'lerin varlığı ve başlık doğruluğu
"""

import csv
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Test dosyası tests/ altında; proje kökünü sys.path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from merge import find_csv_files, natural_sort_key, merge
from utils import detect_encoding, ProgressBar


# ── Sabitler ve yardımcılar ───────────────────────────────────────────────────

# Örnek veri dosyalarının bulunduğu klasör
DATA_DIR = Path(__file__).parent / "data"

# Projenin beklediği referans CSV başlığı
HEADER = ["email", "validity", "validSMTP", "validIdentity",
          "customData", "jobId", "reason", "mxDomain", "reasonCode"]


def write_csv(path: Path, rows: list, header=None):
    """
    Test CSV dosyası oluşturan yardımcı fonksiyon.
    header verilmezse global HEADER kullanılır.
    """
    h = header or HEADER
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(h)      # Başlık satırını yaz
        for r in rows:
            w.writerow(r)  # Veri satırlarını yaz


# ── natural_sort_key testleri ─────────────────────────────────────────────────

def test_natural_sort_order():
    """
    Saf string sıralaması '10' < '2' üretir (leksikografik).
    natural_sort_key bunun önüne geçerek 1 < 2 < 10 sağlamalı.
    """
    paths = ["source/10-data.csv", "source/2-data.csv", "source/1-data.csv"]
    sorted_paths = sorted(paths, key=natural_sort_key)
    assert sorted_paths == [
        "source/1-data.csv",
        "source/2-data.csv",
        "source/10-data.csv",
    ]


# ── find_csv_files testleri ───────────────────────────────────────────────────

def test_find_csv_files_excludes_output(tmp_path):
    """
    Çıktı dosyası kaynak klasördeyse find_csv_files onu listeye eklememelidir.
    Aksi hâlde merge() kendi çıktısını okuyarak sonsuz döngüye girebilir.
    """
    (tmp_path / "a.csv").write_text("h\n1\n")
    (tmp_path / "b.csv").write_text("h\n2\n")
    output = tmp_path / "b.csv"  # b.csv hem kaynak hem çıktı gibi davranıyor

    files = find_csv_files(tmp_path, "*.csv", output)
    names = [Path(f).name for f in files]

    assert "a.csv" in names       # a.csv listeye girmeli
    assert "b.csv" not in names   # b.csv (çıktı) listeye girmemeli


def test_find_csv_files_pattern(tmp_path):
    """
    Glob deseni yalnızca .csv dosyalarını seçmeli; .txt gibi dosyalar atlanmalı.
    """
    (tmp_path / "11-abc.csv").write_text("h\n")
    (tmp_path / "22-abc.csv").write_text("h\n")
    (tmp_path / "other.txt").write_text("txt\n")  # Bu seçilmemeli

    files = find_csv_files(tmp_path, "*.csv", tmp_path / "out.csv")
    assert len(files) == 2  # Yalnızca iki .csv dosyası


# ── merge() testleri ──────────────────────────────────────────────────────────

def test_merge_basic(tmp_path):
    """
    İki sağlam CSV dosyası birleştirildiğinde:
      - Çıktı dosyası başlık + 2 veri satırı içermeli
      - Sütun sırası ve değerler korunmalı
    """
    write_csv(tmp_path / "1.csv", [["a@b.com", "valid", "1", "1", "1", "J1", "", "mx.com", ""]])
    write_csv(tmp_path / "2.csv", [["c@d.com", "invalid", "", "", "2", "J2", "err", "", "bad_dns"]])

    out = tmp_path / "out.csv"
    merge(str(tmp_path), str(out), "*.csv", "utf-8", auto_encoding=False)

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert rows[0] == HEADER       # Başlık doğru
    assert len(rows) == 3          # Başlık + 2 veri satırı
    assert rows[1][0] == "a@b.com" # İlk veri satırı doğru
    assert rows[2][0] == "c@d.com" # İkinci veri satırı doğru


def test_merge_skips_wrong_header(tmp_path):
    """
    İkinci dosyanın başlığı birinciden farklıysa o dosya atlanmalı,
    çıktıda yalnızca birinci dosyanın verisi yer almalı.
    Farklı başlıklı veri eklenmesi sütun kaymasına yol açar.
    """
    write_csv(tmp_path / "1.csv", [["a@b.com", "valid", "1", "1", "1", "J1", "", "mx.com", ""]])

    # Kasıtlı olarak farklı başlık
    with open(tmp_path / "2.csv", "w", newline="") as f:
        csv.writer(f).writerow(["email", "farkli"])
        csv.writer(f).writerow(["x@y.com", "foo"])

    out = tmp_path / "out.csv"
    merge(str(tmp_path), str(out), "*.csv", "utf-8", auto_encoding=False)

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert len(rows) == 2  # Başlık + yalnızca 1. dosyanın satırı


def test_merge_skips_empty_file(tmp_path):
    """
    Tamamen boş (0 byte) bir dosya hata vermeden atlanmalı.
    Diğer dosyaların verisi çıktıya yansımalı.
    """
    write_csv(tmp_path / "1.csv", [["a@b.com", "valid", "1", "1", "1", "J1", "", "mx.com", ""]])
    (tmp_path / "2.csv").write_text("")  # Kasıtlı boş dosya

    out = tmp_path / "out.csv"
    merge(str(tmp_path), str(out), "*.csv", "utf-8", auto_encoding=False)

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert len(rows) == 2  # Başlık + yalnızca 1. dosyanın satırı


def test_merge_skips_blank_rows(tmp_path):
    """
    Tüm hücreleri boş olan satırlar (yalnızca virgül içeren satırlar)
    çıktıya yazılmamalıdır; bu tür satırlar empty_rows sayacına eklenir.
    """
    with open(tmp_path / "1.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerow(["a@b.com", "valid", "1", "1", "1", "J1", "", "mx.com", ""])
        w.writerow(["", "", "", "", "", "", "", "", ""])  # Tamamen boş satır

    out = tmp_path / "out.csv"
    merge(str(tmp_path), str(out), "*.csv", "utf-8", auto_encoding=False)

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert len(rows) == 2  # Başlık + 1 gerçek satır (boş satır filtrelendi)


def test_merge_output_not_included_as_source(tmp_path):
    """
    find_csv_files output yolunu kaynak listesinden çıkarmalıdır.
    Çıktı dosyasının kaynak olarak okunması veri tekrarına neden olur.
    """
    write_csv(tmp_path / "1.csv", [["a@b.com", "valid", "1", "1", "1", "J1", "", "mx.com", ""]])
    out = tmp_path / "1.csv"  # Kasıtlı çakışma: out == kaynak

    files = find_csv_files(tmp_path, "*.csv", out)
    # out.resolve() listedeki hiçbir dosyanın resolve() değerine eşit olmamalı
    assert str(out.resolve()) not in [str(Path(f).resolve()) for f in files]


# ── utils testleri ─────────────────────────────────────────────────────────────

def test_detect_encoding_utf8(tmp_path):
    """
    UTF-8 özel karakterler içeren dosya için detect_encoding
    'utf-8', 'ascii' veya 'utf-8-sig' dönmelidir.
    (Saf ASCII içerik bazen 'ascii' olarak raporlanır; bu da geçerlidir.)
    """
    p = tmp_path / "test.csv"
    # UTF-8 özel karakter (İ) ekleyerek chardet'in ascii yerine utf-8 bulmasını sağla
    p.write_text("email,isim\na@b.com,İstanbul\n", encoding="utf-8")
    enc = detect_encoding(str(p))

    # Normalize et ve kabul edilen değerlerle karşılaştır
    assert enc.lower().replace("-", "").replace("_", "") in ("utf8", "utf8sig", "ascii", "utf8bom")


def test_detect_encoding_latin1(tmp_path):
    """
    Latin-1 encoded dosya için detect_encoding None döndürmemeli;
    'latin-1', 'cp1254' veya benzer bir encoding adı dönmelidir.
    """
    p = tmp_path / "latin.csv"
    # \xe7 = 'ç', \xf6 = 'ö' Latin-1'de
    p.write_bytes("email,isim\na@b.com,\xe7i\xe7ek\n".encode("latin-1"))
    enc = detect_encoding(str(p))
    assert enc is not None  # Herhangi bir encoding tespit edilmeli


def test_progress_bar_completes(capsys):
    """
    ProgressBar 3 birimlik toplam için 3 kez update() çağrıldığında
    done == total olmalı ve terminale "3/3" içeren bir çıktı yazılmalı.
    """
    pb = ProgressBar(total=3, label="Test")
    pb.update(1)
    pb.update(1)
    pb.update(1)
    captured = capsys.readouterr()
    # Ya terminale "3/3" yazılmış ya da done değeri doğru
    assert "3/3" in captured.out or pb.done == 3


# ── Örnek veri dosyası testleri ───────────────────────────────────────────────

def test_data_files_exist():
    """
    tests/data/ altındaki örnek CSV dosyaları yerinde mi?
    Bu dosyalar elle silinmiş veya taşınmışsa testler güvenilmez sonuç verir.
    """
    assert (DATA_DIR / "normal_a.csv").exists(),    "normal_a.csv bulunamadı"
    assert (DATA_DIR / "normal_b.csv").exists(),    "normal_b.csv bulunamadı"
    assert (DATA_DIR / "wrong_header.csv").exists(),"wrong_header.csv bulunamadı"
    assert (DATA_DIR / "empty.csv").exists(),       "empty.csv bulunamadı"
    assert (DATA_DIR / "blank_rows.csv").exists(),  "blank_rows.csv bulunamadı"


def test_normal_data_files_have_correct_header():
    """
    Normal örnek dosyalar (normal_a.csv, normal_b.csv) global HEADER ile
    birebir eşleşen başlık satırına sahip olmalı.
    Başlık yanlışsa merge() bu dosyaları atlayacak ve testler yanıltıcı olacaktır.
    """
    for fname in ("normal_a.csv", "normal_b.csv"):
        with open(DATA_DIR / fname, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)  # Yalnızca ilk satırı oku
        assert header == HEADER, f"{fname} başlığı yanlış: {header}"
