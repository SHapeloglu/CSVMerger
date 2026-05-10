"""
CSV Merger & MySQL Aktarıcı — Yardım Sayfası
----------------------------------------------
Bu script, projenin tüm komutlarını, argümanlarını ve
örnek kullanımlarını renkli ve okunabilir bir biçimde gösterir.

Çalıştır:
    python help.py              # Ana menü
    python help.py merge        # merge.py detayları
    python help.py mysql        # csv_to_mysql.py detayları
    python help.py akis         # Tam iş akışı
    python help.py encoding     # Encoding rehberi
    python help.py guvenlik     # Güvenlik rehberi
    python help.py hata         # Hata senaryoları
"""

import sys
import os

# ── ANSI Renk Kodları ─────────────────────────────────────────────────────────
# Windows'ta renklerin çalışması için ANSI modunu etkinleştir
if sys.platform == "win32":
    os.system("")  # Windows ANSI desteği

R  = "\033[91m"   # Kırmızı   — uyarı, hata
G  = "\033[92m"   # Yeşil     — başarı, onay
Y  = "\033[93m"   # Sarı      — vurgu, örnek
B  = "\033[94m"   # Mavi      — başlık, komut
C  = "\033[96m"   # Camgöbeği — argüman adları
M  = "\033[95m"   # Mor       — bölüm başlığı
W  = "\033[97m"   # Beyaz     — normal metin
DIM = "\033[2m"   # Soluk     — yorum satırları
RST = "\033[0m"   # Sıfırla

def clr(text, color):
    """Metni verilen ANSI rengiyle sarmalar."""
    return f"{color}{text}{RST}"

def baslik(text):
    """Ana bölüm başlığı çizer."""
    cizgi = "═" * 60
    print(f"\n{clr(cizgi, M)}")
    print(f"{clr('  ' + text, M)}")
    print(f"{clr(cizgi, M)}")

def alt_baslik(text):
    """Alt bölüm başlığı çizer."""
    print(f"\n{clr('▶ ' + text, B)}")
    print(f"{clr('  ' + '─' * (len(text) + 2), DIM)}")

def satir(etiket, aciklama, renk=C):
    """Hizalanmış argüman + açıklama satırı yazar."""
    print(f"  {clr(etiket.ljust(28), renk)}  {aciklama}")

def ornek(komut, yorum=""):
    """Komut satırı örneği yazar."""
    yorum_str = f"  {clr('# ' + yorum, DIM)}" if yorum else ""
    print(f"  {clr('$', DIM)} {clr(komut, Y)}{yorum_str}")

def bilgi(text):
    """Bilgi notu yazar."""
    print(f"  {clr('ℹ', C)} {text}")

def uyari(text):
    """Uyarı notu yazar."""
    print(f"  {clr('⚠', Y)}  {text}")

def hata_notu(text):
    """Hata notu yazar."""
    print(f"  {clr('✖', R)} {text}")

def tamam(text):
    """Başarı notu yazar."""
    print(f"  {clr('✔', G)} {text}")


# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜMLER
# ─────────────────────────────────────────────────────────────────────────────

def ana_menu():
    """Ana yardım menüsünü gösterir."""
    print(f"""
{clr('╔══════════════════════════════════════════════════════════════╗', M)}
{clr('║        CSV Merger & MySQL Aktarıcı  —  Yardım Merkezi        ║', M)}
{clr('╚══════════════════════════════════════════════════════════════╝', M)}

Bu araç seti iki ana script içerir:

  {clr('merge.py', B)}          Birden fazla CSV dosyasını tek dosyada birleştirir
  {clr('csv_to_mysql.py', B)}   Birleşik CSV'yi MySQL veritabanına aktarır

{clr('─────────────────────────────────────────────────────────────', DIM)}
Detaylı yardım için bir konu seçin:
{clr('─────────────────────────────────────────────────────────────', DIM)}

  {clr('python help.py merge', Y)}       merge.py argümanları ve örnekleri
  {clr('python help.py mysql', Y)}       csv_to_mysql.py argümanları ve örnekleri
  {clr('python help.py akis', Y)}        Adım adım tam iş akışı
  {clr('python help.py encoding', Y)}    Encoding / karakter seti rehberi
  {clr('python help.py guvenlik', Y)}    Şifre güvenliği rehberi
  {clr('python help.py hata', Y)}        Hata durumları ve çözümleri
  {clr('python help.py hepsi', Y)}       Tüm yardım sayfalarını göster

{clr('─────────────────────────────────────────────────────────────', DIM)}
{clr('Hızlı başlangıç:', W)}

  {clr('$ cp /verim/*.csv source/', Y)}
  {clr('$ python merge.py', Y)}
  {clr('$ python csv_to_mysql.py --db benim_db --table sonuclar', Y)}
{clr('─────────────────────────────────────────────────────────────', DIM)}
""")


def bolum_merge():
    """merge.py yardım sayfasını gösterir."""
    baslik("merge.py — CSV Birleştirici")

    print(f"""
  {clr('source/', B)} klasöründeki tüm .csv dosyalarını okur, başlıkları
  bir kez yazar ve tüm veriyi tek bir çıktı dosyasında birleştirir.

  Veri akışı:
    {clr('source/*.csv', Y)}  ──▶  {clr('merge.py', B)}  ──▶  {clr('birlesik_cikti.csv', G)}
""")

    alt_baslik("Temel kullanım")
    ornek("python merge.py", "Varsayılan: source/ → birlesik_cikti.csv")
    print()

    alt_baslik("Argümanlar")
    satir("-i DIR, --input DIR",       "Kaynak klasör                  [varsayılan: source]")
    satir("-o FILE, --output FILE",    "Çıktı dosyası adı              [varsayılan: birlesik_cikti.csv]")
    satir("-p DESEN, --pattern DESEN", "Glob dosya deseni              [varsayılan: *.csv]")
    satir("-e ENC, --encoding ENC",    "Sabit encoding                 [varsayılan: utf-8]")
    satir("--auto-encoding",           "Her dosya için encoding tespit et")
    satir("--log FILE",                "Log dosyası yolu               [varsayılan: merge.log]")

    alt_baslik("Örnekler")
    ornek("python merge.py",                                          "Varsayılan")
    ornek("python merge.py -i ./ham_veri",                           "Farklı klasör")
    ornek("python merge.py -o temmuz.csv",                           "Farklı çıktı adı")
    ornek('python merge.py -p "11-*.csv"',                           "Yalnızca 11- ile başlayanlar")
    ornek("python merge.py --auto-encoding",                         "Encoding otomatik")
    ornek("python merge.py -i ./ham -o temiz.csv --auto-encoding",   "Kombine kullanım")
    ornek("python merge.py --log logs/bugun.log",                    "Özel log")

    alt_baslik("Davranış Kuralları")
    tamam("Dosyalar doğal sayı sırasıyla işlenir: 1-, 2-, 10-, 11-…")
    tamam("Farklı başlıklı dosyalar atlanır ve loglanır")
    tamam("Tamamen boş satırlar çıktıya yazılmaz")
    tamam("Boş (0 byte) dosyalar hata vermeden atlanır")
    tamam("Çıktı dosyası UTF-8 olarak yazılır (kaynak encoding'den bağımsız)")

    alt_baslik("Log Çıktısı Örneği")
    print(f"""  {clr('2024-07-15 10:23:01 [INFO] Giriş    : source', DIM)}
  {clr('2024-07-15 10:23:01 [INFO] Bulunan  : 47 CSV dosyası', DIM)}
  {clr('2024-07-15 10:23:04 [INFO] Tamamlandı!', DIM)}
  {clr('2024-07-15 10:23:04 [INFO]   Birleştirilen : 46 dosya', DIM)}
  {clr('2024-07-15 10:23:04 [INFO]   Toplam satır  : 142,381', DIM)}
  {clr('2024-07-15 10:23:04 [WARNING] Atlanan dosyalar (1):', DIM)}
  {clr('2024-07-15 10:23:04 [WARNING]   - 23-ozet.csv: farklı başlık', DIM)}""")
    print()


def bolum_mysql():
    """csv_to_mysql.py yardım sayfasını gösterir."""
    baslik("csv_to_mysql.py — MySQL Aktarıcı")

    print(f"""
  {clr('birlesik_cikti.csv', Y)} (veya belirtilen başka bir CSV) dosyasını
  MySQL veritabanına toplu (batch) olarak aktarır.

  Veri akışı:
    {clr('birlesik_cikti.csv', Y)}  ──▶  {clr('csv_to_mysql.py', B)}  ──▶  {clr('MySQL Tablosu', G)}
""")

    alt_baslik("Temel kullanım")
    ornek("python csv_to_mysql.py", "DB_PASSWORD env değişkeni gerekli")
    print()

    alt_baslik("Bağlantı Argümanları")
    satir("--host ADRES",    "MySQL sunucu adresi         [varsayılan: localhost]")
    satir("--port PORT",     "MySQL port                  [varsayılan: 3306]")
    satir("--user KULLANICI","MySQL kullanıcı adı         [varsayılan: root]")
    satir("--password SIFRE",f"⚠ Güvensiz! .env kullanın  [{clr('bkz: python help.py guvenlik', R)}]")
    satir("--db VERITABANI", "Hedef veritabanı adı        [varsayılan: email_db]")
    satir("--table TABLO",   "Hedef tablo adı             [varsayılan: email_sonuclari]")

    alt_baslik("Dosya ve Performans Argümanları")
    satir("--csv FILE",        "Okunacak CSV dosyası        [varsayılan: birlesik_cikti.csv]")
    satir("--batch N",         "Batch boyutu (satır)        [varsayılan: 500]")
    satir("--encoding ENC",    "Sabit encoding              [varsayılan: utf-8]")
    satir("--auto-encoding",   "Encoding otomatik tespit et")
    satir("--log FILE",        "Log dosyası yolu            [varsayılan: import.log]")

    alt_baslik("Veri Yönetimi Argümanları")
    satir("--truncate",  "Insert öncesi tabloyu temizle (TRUNCATE)")
    satir("--upsert",    "Duplicate e-posta varsa güncelle (varsayılan: atla)")

    alt_baslik("Örnekler")
    ornek("python csv_to_mysql.py",                                "Varsayılan")
    ornek("python csv_to_mysql.py --host 192.168.1.50 --db prod",  "Uzak sunucu")
    ornek("python csv_to_mysql.py --csv arsiv/haziran.csv",        "Farklı dosya")
    ornek("python csv_to_mysql.py --batch 2000",                   "Daha büyük batch")
    ornek("python csv_to_mysql.py --truncate",                     "Tabloyu sıfırla")
    ornek("python csv_to_mysql.py --upsert",                       "Duplicate güncelle")
    ornek("python csv_to_mysql.py --auto-encoding --log imp.log",  "Kombine")

    alt_baslik("Sütun Eşlemesi (CSV → MySQL)")
    print(f"  {'CSV Başlığı'.ljust(18)} {'MySQL Sütunu'.ljust(18)} Tip")
    print(f"  {clr('─'*56, DIM)}")
    eslesme = [
        ("email",         "email",         "VARCHAR(255) UNIQUE"),
        ("validity",      "validity",       "ENUM('valid','invalid','unknown')"),
        ("validSMTP",     "valid_smtp",     "TINYINT(1)"),
        ("validIdentity", "valid_identity", "TINYINT(1)"),
        ("customData",    "custom_data",    "VARCHAR(255)"),
        ("jobId",         "job_id",         "VARCHAR(100)"),
        ("reason",        "reason",         "VARCHAR(255)"),
        ("mxDomain",      "mx_domain",      "VARCHAR(255)"),
        ("reasonCode",    "reason_code",    "VARCHAR(100)"),
    ]
    for csv_h, mysql_h, tip in eslesme:
        print(f"  {clr(csv_h.ljust(18), Y)}{clr(mysql_h.ljust(18), C)}{clr(tip, DIM)}")
    print(f"  {clr('─'*56, DIM)}")
    bilgi("Tablo yoksa CREATE TABLE IF NOT EXISTS ile otomatik oluşturulur.")
    bilgi("yukleme_tarihi sütunu her insert'te otomatik doldurulur.")
    print()


def bolum_akis():
    """Tam iş akışını gösterir."""
    baslik("Adım Adım Tam İş Akışı")

    print()
    alt_baslik("Adım 1 — Kurulum (ilk kez)")
    ornek("git clone https://github.com/kullanici/csv-merger.git")
    ornek("cd csv-merger")
    ornek("python -m venv .venv")
    ornek("source .venv/bin/activate",       "Linux/macOS")
    ornek(".venv\\Scripts\\activate",        "Windows")
    ornek("pip install -r requirements.txt")

    print()
    alt_baslik("Adım 2 — Şifre Ayarı (bir kez)")
    ornek("cp .env.example .env")
    print(f"  {clr('# .env dosyasını düzenle:', DIM)}")
    print(f"  {clr('DB_PASSWORD=gercek_sifreniz', Y)}")

    print()
    alt_baslik("Adım 3 — CSV Dosyalarını Hazırla")
    ornek("mkdir -p source")
    ornek("cp /veri/parca*.csv source/",     "CSV'leri source/ klasörüne taşı")
    ornek("ls source/",                      "Kontrol et")

    print()
    alt_baslik("Adım 4 — CSV Birleştirme")
    ornek("python merge.py",                 "Varsayılan ayarlarla")
    ornek("python merge.py --auto-encoding", "Türkçe/karma kaynaklı dosyalar için")
    print()
    bilgi("Çıktı: birlesik_cikti.csv + merge.log")

    print()
    alt_baslik("Adım 5 — MySQL'e Aktarım")
    ornek("python csv_to_mysql.py --db benim_db --table sonuclar")
    print()
    bilgi("Çıktı: MySQL tablosu dolduruldu + import.log")

    print()
    alt_baslik("Adım 6 — Doğrulama")
    print(f"""  MySQL'de kontrol et:
  {clr('SELECT COUNT(*) FROM sonuclar;', Y)}
  {clr('SELECT * FROM sonuclar LIMIT 10;', Y)}
  {clr('SELECT validity, COUNT(*) FROM sonuclar GROUP BY validity;', Y)}
""")

    print()
    alt_baslik("Yeni Veri Geldiğinde (tekrar çalıştırma)")
    ornek("cp /yeni_veri/*.csv source/")
    ornek("python merge.py",                 "Çıktıyı yeniden oluşturur")
    ornek("python csv_to_mysql.py",          "Yeni kayıtları ekler (duplicate'ler atlanır)")
    print()
    bilgi("--upsert ile duplicate'ler güncellenir, --truncate ile tablo sıfırlanır.")


def bolum_encoding():
    """Encoding rehberini gösterir."""
    baslik("Encoding / Karakter Seti Rehberi")

    print(f"""
  Encoding, metin karakterlerinin baytlara nasıl dönüştürüldüğünü tanımlar.
  Türkçe karakterler (ğ, ü, ş, ı, ö, ç) yanlış encoding'de bozuk görünür.
""")

    alt_baslik("Ne Zaman --auto-encoding Kullanmalısınız?")
    uyari("Farklı sistemlerden gelen karışık kaynak dosyalar")
    uyari("Türkçe karakter içeren eski Windows CSV'leri (CP1254)")
    uyari("Kaynak encoding'in ne olduğunu bilmiyorsanız")
    print()

    alt_baslik("Tespit Mekanizması")
    print(f"""
  {clr('--auto-encoding aktif', B)}
         │
         ▼
  {clr('chardet kurulu mu?', W)}
    {clr('Evet', G)} │  {clr('Hayır', R)}
         │         │
         ▼         ▼
  {clr('Binary analiz', G)}   {clr('Sırayla dene:', W)}
  {clr('Güven ≥ %50?', G)}   {clr('1. utf-8-sig', Y)}
    {clr('Evet', G)} │ {clr('Hayır', R)}  {clr('2. utf-8', Y)}
         │    │     {clr('3. cp1254', Y)}  {clr('(Türkçe Windows)', DIM)}
         ▼    ▼     {clr('4. latin-1', Y)}
  {clr('Kullan', G)} {clr('utf-8', Y)}
""")

    alt_baslik("Önerilen Kullanım")
    ornek("python merge.py --auto-encoding",
          "Birleştirirken encoding tespit et")
    ornek("python csv_to_mysql.py --auto-encoding",
          "Aktarırken encoding tespit et")
    ornek("pip install chardet",
          "Daha doğru tespit için chardet kur")
    print()
    bilgi("Çıktı CSV'si her zaman UTF-8 olarak yazılır.")
    bilgi("MySQL tablosu utf8mb4 charset ile oluşturulur (emoji dahil).")


def bolum_guvenlik():
    """Güvenlik rehberini gösterir."""
    baslik("Şifre Güvenliği Rehberi")

    print(f"""
  MySQL şifrenizi komut satırına yazmayın.
  Terminal geçmişine kaydolur, {clr('ps aux', Y)} ile görünür.
""")

    alt_baslik("❌ Yanlış — Şifreyi Komut Satırına Yazma")
    print(f"  {clr('$ python csv_to_mysql.py --password gizlisifre123', R)}")
    hata_notu("bash_history dosyasına kaydolur")
    hata_notu("'ps aux' çıktısında görünür")
    hata_notu("Log dosyalarına sızabilir")
    print()

    alt_baslik("✅ Doğru — Yöntem 1: Ortam Değişkeni")
    ornek("export DB_PASSWORD=gizlisifre123",  "Sadece bu oturum için")
    ornek("python csv_to_mysql.py",            "Şifre otomatik okunur")
    print()
    bilgi("Terminal kapatılınca değişken silinir.")
    bilgi("Kalıcı yapmak için .bashrc / .zshrc dosyanıza ekleyin.")
    print()

    alt_baslik("✅ Doğru — Yöntem 2: .env Dosyası (önerilen)")
    ornek("cp .env.example .env")
    print(f"""
  .env dosyasını düzenleyin:
  {clr('DB_PASSWORD=gizlisifre123', Y)}

  Sonra normal şekilde çalıştırın:""")
    ornek("python csv_to_mysql.py")
    print()
    tamam(".env dosyası .gitignore ile Git'e girmez")
    tamam("python-dotenv otomatik yükler")
    tamam("Takım çalışmasında .env.example paylaşılır, .env paylaşılmaz")
    print()

    alt_baslik("Öncelik Sırası")
    print(f"""
  {clr('1. DB_PASSWORD ortam değişkeni', G)}  ← en güvenli
  {clr('2. .env dosyasındaki DB_PASSWORD', G)}  ← önerilen
  {clr('3. --password argümanı', R)}            ← güvensiz, kullanmayın
""")


def bolum_hata():
    """Hata durumları ve çözümlerini gösterir."""
    baslik("Hata Durumları ve Çözümleri")
    print()

    durumlar = [
        (
            "Klasör bulunamadı",
            "HATA: Klasör bulunamadı: source",
            [
                "source/ klasörünün var olduğunu kontrol edin",
                "python merge.py -i ./dogru_klasor",
            ]
        ),
        (
            "MySQL bağlantı hatası",
            "HATA: MySQL bağlantı hatası: Access denied for user",
            [
                "DB_PASSWORD ortam değişkenini kontrol edin",
                "export DB_PASSWORD=dogru_sifre",
                "--host, --user, --db argümanlarını kontrol edin",
            ]
        ),
        (
            "mysql-connector-python kurulu değil",
            "HATA: mysql-connector-python kurulu değil",
            [
                "pip install mysql-connector-python",
            ]
        ),
        (
            "Farklı başlıklı dosya",
            "UYARI: Atlandı (farklı başlık): 23-ozet.csv",
            [
                "Bu dosyanın başlık satırı diğerlerinden farklı",
                "Dosyayı manuel inceleyin: cat source/23-ozet.csv | head -1",
                "Gerekiyorsa başlığı düzeltin veya dosyayı silin",
            ]
        ),
        (
            "CSV dosyası bulunamadı (aktarım)",
            "HATA: CSV dosyası bulunamadı: birlesik_cikti.csv",
            [
                "Önce python merge.py çalıştırın",
                "veya --csv ile doğru yolu belirtin",
            ]
        ),
        (
            "Batch insert hatası",
            "HATA: Batch hatası (atlandı): Data too long for column",
            [
                "Tablodaki VARCHAR boyutu küçük olabilir",
                "COLUMN_TYPES sözlüğünde ilgili sütunun boyutunu artırın",
                "Hatalı batch rollback edilir; diğerleri devam eder",
            ]
        ),
        (
            "encoding hatası / bozuk karakterler",
            "Çıktıda bozuk Türkçe karakterler",
            [
                "python merge.py --auto-encoding",
                "pip install chardet  (daha iyi tespit için)",
                "python merge.py -e cp1254  (Türkçe Windows CSV'leri için)",
            ]
        ),
    ]

    for baslik_metin, hata_mesaji, cozumler in durumlar:
        alt_baslik(baslik_metin)
        print(f"  {clr(hata_mesaji, R)}")
        print(f"  {clr('Çözüm:', G)}")
        for c in cozumler:
            if c.startswith("python") or c.startswith("pip") or c.startswith("export") or c.startswith("cat"):
                ornek(c)
            else:
                bilgi(c)
        print()


# ─────────────────────────────────────────────────────────────────────────────
# GİRİŞ NOKTASI
# ─────────────────────────────────────────────────────────────────────────────

BOLUMLER = {
    "merge":     bolum_merge,
    "mysql":     bolum_mysql,
    "akis":      bolum_akis,
    "encoding":  bolum_encoding,
    "guvenlik":  bolum_guvenlik,
    "hata":      bolum_hata,
}

def main():
    args = sys.argv[1:]

    if not args:
        ana_menu()
        return

    konu = args[0].lower()

    if konu == "hepsi":
        ana_menu()
        for fn in BOLUMLER.values():
            fn()
        return

    if konu in BOLUMLER:
        BOLUMLER[konu]()
    else:
        print(f"\n{clr('Bilinmeyen konu:', R)} {konu}")
        print(f"Geçerli konular: {', '.join(BOLUMLER.keys())}, hepsi")
        print(f"\n{clr('$ python help.py', Y)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
